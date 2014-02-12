__author__ = 'wallsr'

"""
This is a simple script to output the OOB data for every located contacts2.db header
in the image file.
"""

import sys

from optparse import OptionParser

import Scanner



def main():
    """
    Assume we pass this script the image file path as an argument on the
    command line.
    """

    usage = 'usage: %prog [options] imagefile'

    parser = OptionParser(usage=usage)
    parser.add_option('--chunksize', action='store', type='int',
                      dest='chunk_size', default=2048)
    parser.add_option('--oobsize', action='store', type='int',
                      dest='oob_size', default=64)

    options, args = parser.parse_args()

    if len(args) != 1:
        print "Incorrect command line arguments. Missing (or too many) image files"
        return 1

    image = args[0]

    headers = Scanner.get_anchor_headers(image, options.chunk_size,
                                           options.oob_size)

    oobs = Scanner.get_oob_bytes(image, headers, options.oob_size)

    for oob in oobs:
        sys.stdout.write(oob)

        #Separate each oob with 16 'X' Bytes.
        sys.stdout.write('X'*16)



if __name__ == '__main__':
    main()