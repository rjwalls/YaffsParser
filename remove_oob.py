__author__ = 'wallsr'

"""
This simple script removes the OOB bytes from the image and writes
the bytes to stdout.

"""

import sys
from optparse import OptionParser

def main():
    """
    Assume we pass this scirpt the image file as an argument
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

    with open(image, 'rb') as f:
        while f.read(1) != '':
            f.seek(-1, True)
            sys.stdout.write(f.read(options.chunk_size))
            f.seek(options.oob_size, True)


if __name__ == '__main__':
    main()