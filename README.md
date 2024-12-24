# image_ls

Python 3 and 2 command line tool to dump out simple meta data about images.
Works with directories of images and; tar (CBT), zip (CBZ), rar (CBR) archives.
NOTE rarfile support is python3 only

## Get started

    python -m pip install -r requirements.txt

For Python 3 and rar support:

    python -m pip install rarfile  # https://github.com/markokr/rarfile

    python image_ls.py
    python image_ls.py /some/path
    python image_ls.py C:\some\path
    python image_ls.py C:\some\path\to\file.cbz
    python image_ls.py /some/path/to/file.cbz

### Debian

Alternatively, install os packages instead of PyPi packages

    sudo apt install python3-pillow



### Example

Sample media:

  * https://github.com/clach04/sample_reading_media/tree/main/images/bobby_make_believe
    * https://github.com/clach04/sample_reading_media/releases/tag/v0.2
  * https://github.com/recurser/exif-orientation-examples

Download and run:

    wget https://github.com/clach04/sample_reading_media/releases/download/v0.2/sample_reading_media.zip
    mkdir sample_reading_media
    cd sample_reading_media
    unzip ../sample_reading_media.zip
    cd ..
    python3 ./image_ls.py sample_reading_media/images/*

Output:

    Python 3.6.9 (default, Jan 26 2021, 15:33:00)
    [GCC 8.4.0] on linux
    '....../image_ls/sample_reading_media/images/bobby_make_believe'
        size        res   fmt   depth #col filename
      280.1K   975x1349 'JPEG'  RGB-24  256 'Bobby-Make-Believe_1915__0.jpg'
      257.7K   975x1320 'JPEG'  RGB-24  256 'Bobby-Make-Believe_1915__1.jpg'
      256.1K   975x1351 'JPEG'  RGB-24  256 'Bobby-Make-Believe_1915__2.jpg'
      294.9K   975x1326 'JPEG'  RGB-24  256 'Bobby-Make-Believe_1915__3.jpg'
    4 files

Same output for images in directory as for comic versions; CBZ, CBT, CBR:

    $ python3 ./image_ls.py sample_reading_media/bobby_make_believe_sample.cbz
    Python 3.6.9 (default, Nov 25 2022, 14:10:45)
    [GCC 8.4.0] on linux
    '...sample_reading_media/bobby_make_believe_sample.cbz'
        size        res   fmt   depth #col filename
      280.1K   975x1349 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__0.jpg'
      257.7K   975x1320 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__1.jpg'
      256.1K   975x1351 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__2.jpg'
      294.9K   975x1326 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__3.jpg'
    4 files
    $ python3 ./image_ls.py sample_reading_media/bobby_make_believe_sample.cbt
    Python 3.6.9 (default, Nov 25 2022, 14:10:45)
    [GCC 8.4.0] on linux
    '...sample_reading_media/bobby_make_believe_sample.cbt'
        size        res   fmt   depth #col filename
      280.1K   975x1349 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__0.jpg'
      257.7K   975x1320 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__1.jpg'
      256.1K   975x1351 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__2.jpg'
      294.9K   975x1326 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__3.jpg'
    4 files
    $ python3 ./image_ls.py sample_reading_media/bobby_make_believe_sample.cbr
    Python 3.6.9 (default, Nov 25 2022, 14:10:45)
    [GCC 8.4.0] on linux
    '...sample_reading_media/bobby_make_believe_sample.cbr'
        size        res   fmt   depth #col filename
      280.1K   975x1349 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__0.jpg'
      257.7K   975x1320 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__1.jpg'
      256.1K   975x1351 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__2.jpg'
      294.9K   975x1326 'JPEG'  RGB-24 >999 'Bobby-Make-Believe_1915__3.jpg'
    4 files

## Similar Tools

  * https://github.com/bitbank2/imageinfo - probably faster, no zip support and limited file type support
