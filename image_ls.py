#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#

import glob
import os
import sys

# import Pillow
try:
    # Pillow and PIL
    from PIL import Image, UnidentifiedImageError  # http://www.pythonware.com/products/pil/
except ImportError:
    import Image  # Older namespace - http://www.pythonware.com/products/pil/


# See https://pillow.readthedocs.io/en/stable/handbook/concepts.html
# from https://stackoverflow.com/questions/1996577/how-can-i-get-the-depth-of-a-jpg-file
mode_to_bpp = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, "CMYK": 32, "YCbCr": 24, "LAB": 24, "HSV": 24, "I": 32, "F": 32}
# consider;; "I;16": 16, "I;16B": 16, "I;16L": 16, "I;16S": 16, "I;16BS": 16, "I;16LS": 16, "I;32": 32, "I;32B": 32, "I;32L": 32, "I;32S": 32, "I;32BS": 32, "I;32LS": 32

# https://parassharmaa.github.io/blog/image/processing/2017/05/29/image-processing-pil/

def bytesize2human_en(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def bytesize2human_ls_en(num):
    """Return the size string that "ls -lh" returns
    FIXME size 0 difference from ls
    """
    for x in ['', 'K', 'M', 'G', 'T']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0


def doit(dir_name):
    counter = 0  # file counter, currently ignores directories
    dir_name = os.path.abspath(dir_name)
    glob_search_str = os.path.join(glob.escape(dir_name), '*')  # NOTE escape maybe Py3 only?
    print(repr(dir_name))
    file_list = glob.glob(glob_search_str)
    # TODO natsort file_list
    print('%8s %10s %5s %7s %s %s' % ('size', 'res', 'fmt', 'depth', '#col', 'filename'))
    for filename in file_list:
        if os.path.isdir(filename):
            # skip directories (TODO consider displaying them?)
            continue
        counter += 1
        # TODO grayscale
        # TODO file timestamp?
        # filesize, resolution, format - mode/bit-depth - num colors
        #print('%r' % filename)
        #print('\t%r' % os.path.basename(filename))
        """
        # f is a file-like object. 
        old_file_position = f.tell()
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        f.seek(old_file_position, os.SEEK_SET)
        """
        # os.path.getsize(filename)
        file_info = os.stat(filename)  # try and retain py2 support, so skip Python3 pathlib
        try:
            im = Image.open(filename)
            colour_count = len(set(im.getdata()))  # essentially number of colors
            if colour_count >= 1000:
                colour_count_str = '>999'
            else:
                colour_count_str = '%4d' % colour_count
            format_str = '%4s-%d' % (im.mode, mode_to_bpp[im.mode])
            image_size_str = '%5dx%d' % im.size  # width, height
            im_format = im.format
        except UnidentifiedImageError:
            # FIXME get lengths correct
            image_size_str = ''
            im_format = '???'
            format_str = ''
            colour_count_str = '    '

        print('%8s %10s %r %7s %s %r' % (bytesize2human_ls_en(file_info.st_size), image_size_str, im_format, format_str, colour_count_str, os.path.basename(filename)))
        """
        print('%r' % im)
        print('%r' % file_info.st_size)
        print('%r' % bytesize2human_ls_en(file_info.st_size))
        print('%r' % (im.size,)) # width, height
        print('%r' % im.format)
        print('%r' % im.mode)
        print('%r' % mode_to_bpp[im.mode])
        #print('%r' % im.bits)
        
        print('%r' % depth)
        #print('%r' % dir(im.palette))
        print('%r' % im.format_description)
        print('%r' % im.get_format_mimetype())
        print('%r' % im.info)  # look for Orientation - https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.info
        """
    #print('%r' % dir(im))
    print('%d files' % counter)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))

    # dumb arg processing
    try:
        dir_name = argv[1]
    except IndexError:
        dir_name = '.'
    doit(dir_name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
