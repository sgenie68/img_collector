from datetime import datetime
from PIL import Image
#import time
import random
import argparse
import os
import platform
import shutil
import time


directories=[]

def move_file(args,source_file, destination_dir):
    """
    Move a file to another directory.

    Parameters:
    source_file (str): The path to the file to be moved.
    destination_dir (str): The directory where the file should be moved.
    """
    try:
        # Ensure the destination directory exists
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        # Move the file
        shutil.move(source_file, destination_dir)
        print(f"File '{source_file}' has been moved to '{destination_dir}'.")
        return 1
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0
 
def imgDate(fn):
    "returns the image date from image (if available)\nfrom Orthallelous"
    std_fmt = '%Y:%m:%d %H:%M:%S.%f'
    # for subsecond prec, see doi.org/10.3189/2013JoG12J126 , sect. 2.2, 2.3
    tags = [(36867, 37521),  # (DateTimeOriginal, SubsecTimeOriginal)
            (36868, 37522),  # (DateTimeDigitized, SubsecTimeDigitized)
            (306, 37520), ]  # (DateTime, SubsecTime)

    try:
        exif = Image.open(fn)._getexif()
    except Exception as e:
        return None
 
    if not exif:
        return None
    for t in tags:
        dat = exif.get(t[0])
        sub = exif.get(t[1], 0)
 
        # PIL.PILLOW_VERSION >= 3.0 returns a tuple
        dat = dat[0] if type(dat) == tuple else dat
        sub = sub[0] if type(sub) == tuple else sub
        if dat != None: break
 
    if dat == None: return None
    full = '{}.{}'.format(dat, sub)
    T = datetime.strptime(full, std_fmt)
    return T.timestamp()

def creation_date(fn):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(fn)
    else:
        stat = os.stat(fn)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

def get_file_time(fn):
    t=imgDate(fn)
    if not t:
        #file does not contain date
        #get from file stats
        t=creation_date(fn)

    return t

def process_file(args,path,name,date,outp):
    global directoris
    modification_time = time.localtime(date)
    dirname=""
    if args.hierarchy:
        dirname=f"{modification_time.tm_year:04d}/{modification_time.tm_mon:02d}/{modification_time.tm_mday:02d}"
    else:
        dirname=f"{modification_time.tm_year:04d}-{modification_time.tm_mon:02d}-{modification_time.tm_mday:02d}"
    dest=outp+dirname+"/"
    os.makedirs(dest, exist_ok=True)
    if not dest in directories:
        directories.append(dest)
    move_file(args,path,dest)
        
def check_tail(string, suffixes):
    # Convert the suffixes to lowercase
    suffixes_lower = tuple(suffix.lower() for suffix in suffixes)
    
    # Check if the string ends with any of the suffixes (case-insensitive)
    result = string.lower().endswith(suffixes_lower)
    
    return result

def process_directory(args,inp,out):
    if not os.path.isfile(inp):
        if inp[-1]!='/' and inp[-1]!='//':
            inp+="/"
        print(f"Directory: {inp}")
        if inp in directories:
            return
        for name in os.listdir(inp):
            path = os.path.join(inp, name)
            if not os.path.isfile(path):
                if name[0]!='.' or args.hidden:
                    if not args.norecurse:
                        process_directory(args,path,out)

            else:
                if name[0]=='.' and not args.hidden:
                    continue
                if check_tail(name,{".jpg",".jpeg",".png",".heic",".gif",".webp"}):
                    t=get_file_time(path)
                    process_file(args,path,name,t,out)

def main(args):
    inp_dir=args.input
    out_dir=args.output

    if out_dir[-1]!='/' and out_dir[-1]!='//':
        out_dir+="/"
    process_directory(args,inp_dir,out_dir)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Scheduler')
    parser.add_argument('--input', '-i', required=False, dest='input', type=str, default='./', help='Input directory')
    parser.add_argument('--output', '-o', required=False, dest='output', type=str, default='./', help='Output directory')
    parser.add_argument("--norecurse",'-n',dest="norecurse",action='store_true',help="Do not traverse recursievely")
    parser.add_argument("--hidden",'-d',dest="hidden",action='store_true',help="Process hidden files and directories")
    parser.add_argument("--hierarchy",'-a',dest="hierarchy",action='store_true',help="Process hidden files and directories")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as ex:
        print(ex)
