__author__ = 'wallsr'


def main():
    """
    Assume we pass this script the image file path as an argument on the
    command line.
    """

    usage = 'usage: %prog [options] imagefile'

    parser = OptionParser(usage=usage)
    options, args = parser.parse_args()

    if len(args) != 1:
        print "Incorrect command line arguments. Missing (or too many) image files"
        return 1

    image = args[0]

    scan_file(image)

    pass


if __name__ == '__main__':
    main()