from datetime import datetime
from PIL import Image
#import time
import random
import argparse
import os
import platform
 
def imgDate(fn):
    "returns the image date from image (if available)\nfrom Orthallelous"
    std_fmt = '%Y:%m:%d %H:%M:%S.%f'
    # for subsecond prec, see doi.org/10.3189/2013JoG12J126 , sect. 2.2, 2.3
    tags = [(36867, 37521),  # (DateTimeOriginal, SubsecTimeOriginal)
            (36868, 37522),  # (DateTimeDigitized, SubsecTimeDigitized)
            (306, 37520), ]  # (DateTime, SubsecTime)
    exif = Image.open(fn)._getexif()
 
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
    #T = time.mktime(time.strptime(dat, '%Y:%m:%d %H:%M:%S')) + float('0.%s' % sub)
    return T

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

def process_directory(args,inp,out):
    if not os.path.isfile(inp):
        print(f"Directory: {inp}")
        for root, dirs, files in os.walk(inp):
            for name in dirs:
                if name[0]!='.' or args.hidden:
                    dir_path = os.path.join(root, name)
                    print("* ",dir_path)
                    if not args.norecurse:
                        process_directory(args,dir_path,out)

            for name in files:
                file_path = os.path.join(root, name)
                if name[0]=='.' and not args.hidden:
                    continue
                if file_path.endswith("jpeg"):
                    t=get_file_time(file_path)
                    print(f"File: {file_path}: {t}")

def main(args):
    inp_dir=args.input
    out_dir=args.output

    process_directory(args,inp_dir,out_dir)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Scheduler')
    parser.add_argument('--input', '-i', required=False, dest='input', type=str, default='./', help='Input directory')
    parser.add_argument('--output', '-o', required=False, dest='output', type=str, default='./', help='Output directory')
    parser.add_argument("--norecurse",'-n',dest="norecurse",action='store_true',help="Do not traverse recursievely")
    parser.add_argument("--hidden",'-d',dest="hidden",action='store_true',help="Process hidden files and directories")
    args = parser.parse_args()
    try:
        main(args)
    except Exception as ex:
        print(ex)