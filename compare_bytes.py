__author__ = 'wallsr'

from optparse import OptionParser

def main():
    """
    Assume we pass this script the input file path as an argument on the
    command line.
    """

    usage = 'usage: %prog [options] inputfile'

    parser = OptionParser(usage=usage)
    parser.add_option('--chunksize', action='store', type='int',
                      dest='chunk_size', default=64,
                      help='the size of each chunk to analyze')
    parser.add_option('--skipsize', action='store', type='int',
                      dest='skip_size', default=16,
                      help='the size of the byte padding, to skip, between each chunk')

    options, args = parser.parse_args()

    if len(args) != 1:
        print "Incorrect command line arguments. Missing (or too many) image files"
        return 1

    inputfile = args[0]

    chunks = []

    with open(inputfile, 'rb') as f:
        while( f.read(1) != '' ):
            f.seek(-1, True)
            chunks.append(f.read(options.chunk_size))
            f.seek(options.skip_size, True)

    print 'Looking at %d chunks' % len(chunks)

    constants = []

    for x in xrange(0, options.chunk_size):
        byte = None
        for chunk in chunks:
            if byte is None:
                byte = chunk[x]
            elif byte != chunk[x]:
                break
        else:
            constants.append(x)

    #Let's collapse the contants in a nice visual range.
    prev = None

    for position in constants:
        if prev is None:
            pretty_range = str(position) + "--"
        elif position != prev + 1:
            pretty_range += str(prev) + ", " + str(position) + "--"

        prev = position

    pretty_range += str(constants[-1])


    print "%d bytes don't change. They are:" % len(constants)
    print pretty_range


if __name__ == '__main__':
    main()