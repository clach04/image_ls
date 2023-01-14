#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#

import glob
import os
import sys
from tarfile import is_tarfile, TarFile
from zipfile import is_zipfile, ZipFile

try:
    from cStringIO import StringIO as FakeFile
except ImportError:
    try:
        from StringIO import StringIO as FakeFile
    except ImportError:
        from io import BytesIO as FakeFile  # py3

# import Pillow
try:
    # Pillow and PIL
    import PIL  # http://www.pythonware.com/products/pil/
    from PIL import Image  # http://www.pythonware.com/products/pil/
    try:
        from PIL import UnidentifiedImageError  # PIL.VERSION missing, PIL.PILLOW_VERSION == '7.1.2'
    except ImportError:
        pass
except ImportError:
    import Image  # Older namespace - http://www.pythonware.com/products/pil/


try:
    from rarfile import is_rarfile, RarFile  # py3 ONLY https://github.com/markokr/rarfile.git
    # TODO Consider making use of:
    #   rarfile.UNRAR_TOOL - 7z support if unrar not availabke as it can also read some rar files
    #   USE_EXTRACT_HACK
    #   HACK_TMP_DIR and determine if os variable TMP/TEMP impact location
except (ImportError, SyntaxError):
    is_rarfile = RarFile = None
#from rarfile import RarFile  # rarfile from Mangle doesn't support recent RAR5 file formats
#from rar import is_rarfile, RarFile  # not py3 compat and fails with one of my sample RAR5 media files
"""
import rarfile

# Set to full path of unrar.exe if it is not in PATH
#rarfile.UNRAR_TOOL = "unrar"

# Set to 0 if you don't look at comments and want to
# avoid wasting time for parsing them
rarfile.NEED_COMMENTS = 0

# Set up to 1 if you don't want to deal with decoding comments
# from unknown encoding.  rarfile will try couple of common
# encodings in sequence.
rarfile.UNICODE_COMMENTS = 0

my_RAR_ID = rarfile.RAR_ID[:-1]  # skip last byte
def my_is_rarfile(fn):
    '''Check quickly whether file is rar archive.'''
    buf = open(fn, "rb").read(len(my_RAR_ID))
    if buf != my_RAR_ID :
        print('DEBUG buf %r my_RAR_ID %r same %r', (buf, my_RAR_ID, buf == my_RAR_ID))
        for x in range(len(buf)):
                print(x, buf[x]  == my_RAR_ID[x])
    return buf == my_RAR_ID

#rarfile.RAR_ID = my_RAR_ID  # monkey patch, so as to hack _parse_real()
"""

"""
class UnidentifiedImageError (OSError):
	pass
"""
try:
    UnidentifiedImageError
except NameError:
    UnidentifiedImageError = OSError  # Python3 PIL.VERSION == '1.1.7' and  PIL.PILLOW_VERSION == '5.1.0'
    UnidentifiedImageError = IOError  # Python2 PIL.VERSION missing, PIL.PILLOW_VERSION == '6.2.2'
    # NOTE this workaround also seems to work for PIL.PILLOW_VERSION == '7.1.2'

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


try:
    glob_escape = glob.escape
except AttributeError:
    def glob_escape(in_str):
        return in_str  # i.e. not implemented!


option_accurate_colour_count = False

def image_ls(dir_or_archive_name):
    if os.path.isdir(dir_or_archive_name):
        is_dir = True
        is_archive = False
        dir_name = os.path.abspath(dir_or_archive_name)
        glob_search_str = os.path.join(glob_escape(dir_name), '*')  # NOTE escape maybe Py3 only? - New in version 3.4.
        print(repr(dir_name))
        file_list = glob.glob(glob_search_str)
        file_list.sort()  # TODO natsort file_list
    else:
        # Assume a zip (archive) file
        is_dir = False
        is_archive = True
        archive_filename = os.path.abspath(dir_or_archive_name)
        print(repr(archive_filename))
        if is_zipfile(archive_filename):
            arch = ZipFile(archive_filename, 'r')
        elif is_rarfile and is_rarfile(archive_filename):
            arch = RarFile(archive_filename, 'r')
        elif is_tarfile(archive_filename):
            arch = TarFile(archive_filename, 'r')
        else:
            raise NotImplementedError('Unknown file (archive) format for %r' % archive_filename)
        if isinstance(arch, TarFile):
            # stupid non-conforming tarfile API...
            arch.namelist = arch.getnames  # Monkey patch in zipfile/rarfile like list function
        file_list = arch.namelist()
        file_list.sort()  # TODO natsort file_list

    counter = 0  # file counter, currently ignores directories
    print('%8s %10s %5s %7s %s %s' % ('size', 'res', 'fmt', 'depth', '#col', 'filename'))

    for filename in file_list:
        if is_dir:
            if os.path.isdir(filename):
                # skip directories (TODO consider displaying them?)
                continue
            file_info = os.stat(filename)  # try and retain py2 support, so skip Python3 pathlib
            file_size = file_info.st_size  # os.path.getsize(filename)
            file_ptr = open(filename, 'rb')

        if is_archive:
            if filename.endswith('/'):
                # skip directories (TODO consider displaying them?)
                continue
            if isinstance(arch, TarFile):
                # stupid non-conforming tarfile API...
                file_ptr = arch.extractfile(filename)
                tar_member_info = arch.getmember(filename)
                file_size = tar_member_info.size
            else:
                file_contents = arch.read(filename)  # read into memory
                file_size = len(file_contents) ## FIXME lookup metadata from arch
                file_ptr = FakeFile(file_contents)
            if filename.startswith('/'):
                # NOTE unix style path
                # TODO win too
                filename = filename[1:]

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
        try:
            im = Image.open(file_ptr)
            if option_accurate_colour_count:
                # processes all image data (which is expensive)
                colour_count = len(set(im.getdata()))  # essentially number of colors
            else:
                colour_count = pow(2, mode_to_bpp[im.mode])  # max possible (might not all be used)
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

        #filename_basename = os.path.basename(filename)  # for zip file, this will hide paths
        filename_basename = filename
        print('%8s %10s %r %7s %s %r' % (bytesize2human_ls_en(file_size), image_size_str, im_format, format_str, colour_count_str, filename_basename))
        file_ptr.close()
        counter += 1
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

    if is_archive:
        arch.close()
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

    image_ls(dir_name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
