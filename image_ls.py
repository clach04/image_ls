#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#

import glob
import os
import sys
from zipfile import ZipFile

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
    import PIL.ExifTags
    from PIL import Image  # http://www.pythonware.com/products/pil/
    try:
        from PIL import UnidentifiedImageError  # PIL.VERSION missing, PIL.PILLOW_VERSION == '7.1.2'
    except ImportError:
        pass
except ImportError:
    import Image  # Older namespace - http://www.pythonware.com/products/pil/

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

exif_tag_names_to_numbers = {PIL.ExifTags.TAGS[x]:x for x in PIL.ExifTags.TAGS}
exif_gps_tag_names_to_numbers = {PIL.ExifTags.GPSTAGS[x]:x for x in PIL.ExifTags.GPSTAGS}
TAG_DATETIME_ORIGINAL = exif_tag_names_to_numbers['DateTimeOriginal']  # 36867
TAG_DATETIME_DIGITIZED = exif_tag_names_to_numbers['DateTimeDigitized']  # 36868
TAG_SUBSECTIME_ORIGINAL = exif_tag_names_to_numbers['SubsecTimeOriginal']  # 37521
TAG_MAKE = exif_tag_names_to_numbers['Make']
TAG_MODEL = exif_tag_names_to_numbers['Model']
TAG_GPSINFO = exif_tag_names_to_numbers['GPSInfo']
TAG_GPS_GPSLONGITUDEREF = exif_gps_tag_names_to_numbers['GPSLongitudeRef']
TAG_GPS_GPSLONGITUDE = exif_gps_tag_names_to_numbers['GPSLongitude']
TAG_GPS_GPSLATITUDEREF = exif_gps_tag_names_to_numbers['GPSLatitudeRef']
TAG_GPS_GPSLATITUDE = exif_gps_tag_names_to_numbers['GPSLatitude']
"""
for x in exif_tag_names_to_numbers:
    print(x)
"""

def get_exif_gpsinfo(image):
    gps_info = image._getexif().get(TAG_GPSINFO)
    return gps_info

def get_exif_original_date(image):
    """
    returns (string of) the DateTimeOriginal/DateTimeDigitized exif data from the given PIL/Pillow Image file
    """
    try:
        # NOTE: using old "private" method because new public method
        #       doesn't include this tag. It does include 306 "DateTime"
        #       though, but "DateTime" might differ from "DateTimeOriginal"
        # pylint: disable-next=protected-access
        date_created = image._getexif().get(TAG_DATETIME_ORIGINAL)
        if not date_created:
            date_created = image._getexif().get(TAG_DATETIME_DIGITIZED)
        if date_created:
            date_created = date_created.replace(':', '-', 2)  # replace date (only) seperator
            # pylint: disable-next=protected-access
            date_created += "." + image._getexif().get(
                TAG_SUBSECTIME_ORIGINAL, ""
            ).zfill(3)
    except (UnidentifiedImageError, AttributeError):
        print("unable to parse '%s'", filepath)
        return None

    return date_created


def printable_coords(coords, ref):
    """
    GPSLatitude, GPSLatitudeRef
    GPSLongitude, GPSLongitudeRef
    """
    result = u"""%d\u00b0%d'%f"%s""" % ((float(coords[0][0]) / float(coords[0][1])) , (float(coords[1][0]) / float(coords[1][1])), (float(coords[2][0]) / float(coords[2][1])), ref)
    return result


def decimal_coords(coords, ref):
    """
    GPSLatitude, GPSLatitudeRef
    GPSLongitude, GPSLongitudeRef
    """
    decimal_degrees = (float(coords[0][0]) / float(coords[0][1]))  + ((float(coords[1][0]) / float(coords[1][1])) / 60 )+ ((float(coords[2][0]) / float(coords[2][1])) / 3600 )
    if ref == 'S' or ref == 'W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def dump_gps_exif(image):
    tmp_exif_dict = image._getexif().get(TAG_GPSINFO, {})
    exif_dict = {
        PIL.ExifTags.GPSTAGS[x]:tmp_exif_dict[x]
        for x in tmp_exif_dict
    }
    #return exif_dict
    import json
    return json.dumps(exif_dict, indent=4)


def dump_all_exif(image):
    tmp_exif_dict = image._getexif()
    exif_dict = {
        PIL.ExifTags.TAGS.get(x, x):tmp_exif_dict[x]  # handle case where EXIF magic number is not known to PIL/Pillow
        for x in tmp_exif_dict
    }
    #return exif_dict
    import json
    #from pprint import pprint
    #pprint(exif_dict)
    #del exif_dict['MakerNote']  # unclear from inspection what this is, after reviewing https://exiv2.org/makernote.html looks like is Vendor dependent (and typically not documented)
    import base64
    exif_dict['MakerNote'] = base64.encodestring(exif_dict['MakerNote'])  # unclear from inspection what this is, after reviewing https://exiv2.org/makernote.html looks like is Vendor dependent (and typically not documented)
    return json.dumps(exif_dict, indent=4, sort_keys=True)


option_accurate_colour_count = False

def doit(dir_name):
    counter = 0  # file counter, currently ignores directories
    dir_name = os.path.abspath(dir_name)
    glob_search_str = os.path.join(glob_escape(dir_name), '*')  # NOTE escape maybe Py3 only? - New in version 3.4.
    print(repr(dir_name))
    file_list = glob.glob(glob_search_str)
    file_list.sort()  # TODO natsort file_list
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
            exif_dict = im._getexif()
        except UnidentifiedImageError:
            # FIXME get lengths correct
            im = exif_dict = None
            image_size_str = ''
            im_format = '???'
            format_str = ''
            colour_count_str = '    '

        print('%8s %10s %r %7s %s %r' % (bytesize2human_ls_en(file_info.st_size), image_size_str, im_format, format_str, colour_count_str, os.path.basename(filename)))
        if exif_dict:
            #print('\t\t\t\t\t%r' % (exif_dict.get(TAG_MAKE),))
            #print('\t\t\t\t\t%r' % (exif_dict.get(TAG_MODEL),))
            print('\t\t\t\t\t%r' % (exif_dict.get(TAG_MAKE) + ' ' + exif_dict.get(TAG_MODEL),))
            print('\t\t\t\t\t%s' % get_exif_original_date(im))
            #print('\t\t\t\t\t%s' % get_exif_gpsinfo(im))
            #print('\t\t\t\t\t%s' % im._getexif())
            #print('\t\t\t\t\t%s' % dump_all_exif(im))
            #print('\t\t\t\t\t%s' % dump_gps_exif(im))

            gps_info = get_exif_gpsinfo(im)
            if gps_info:
                #print('\t\t\t\t\t%r' % (gps_info,))
                """
                print('\t\t\t\t\t%r' % (gps_info[TAG_GPS_GPSLONGITUDE],))
                print('\t\t\t\t\t%s' % printable_coords(gps_info[TAG_GPS_GPSLATITUDE], gps_info[TAG_GPS_GPSLATITUDEREF]))
                print('\t\t\t\t\t%s' % printable_coords(gps_info[TAG_GPS_GPSLONGITUDE], gps_info[TAG_GPS_GPSLONGITUDEREF]))
                print('\t\t\t\t\t%r' % decimal_coords(gps_info[TAG_GPS_GPSLATITUDE], gps_info[TAG_GPS_GPSLATITUDEREF]))
                print('\t\t\t\t\t%r' % decimal_coords(gps_info[TAG_GPS_GPSLONGITUDE], gps_info[TAG_GPS_GPSLONGITUDEREF]))
                """

                print('\t\t\t\t\t%r' % (
                    (decimal_coords(gps_info[TAG_GPS_GPSLATITUDE], gps_info[TAG_GPS_GPSLATITUDEREF]), decimal_coords(gps_info[TAG_GPS_GPSLONGITUDE], gps_info[TAG_GPS_GPSLONGITUDEREF])),
                    ))

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


# FIXME refactor, e.g. doit_zip() image open and processing code duplicates doit()
def doit_zip(zip_filename):
    counter = 0  # file counter, currently ignores directories
    zip_filename = os.path.abspath(zip_filename)
    print(repr(zip_filename))
    arch = ZipFile(zip_filename, 'r')
    file_list = arch.namelist()
    file_list.sort()  # TODO natsort file_list
    print('%8s %10s %5s %7s %s %s' % ('size', 'res', 'fmt', 'depth', '#col', 'filename'))
    for filename in file_list:
        if filename.endswith('/'):
            # skip directories (TODO consider displaying them?)
            continue
        file_contents = arch.read(filename)  # read into memory
        file_size = len(file_contents) ## FIXME lookup metadata from arch
        file_ptr = FakeFile(file_contents)
        if filename.startswith('/'):
            # NOTE unix style path
            # TODO win too
            filename = filename[1:]

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

    # FIXME merge and refactor doit() and doit_zip()
    if os.path.isdir(dir_name):
        doit(dir_name)
    else:
        # Assume a zip file
        doit_zip(dir_name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
