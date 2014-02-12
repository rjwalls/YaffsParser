__author__ = 'wallsr'

"""
This script attempts to determine important characteristics of a Yaffs phone image.

Ideally, this functionality will be incorporated into a new version of the Yaffs parser.
"""

import os

from YaffsClasses.YaffsChunk import YaffsHeader
from YaffsClasses.YaffsOobTag import YaffsOobTag

import YaffsParser


def scan_file(image, anchor):
    chunk_sizes = [1024, 2048]
    oob_sizes = [32, 64]

    max_count = 0
    best_csize = None
    best_osize = None
    best_headers = None

    for csize in chunk_sizes:
        for osize in oob_sizes:
            size = os.path.getsize(image)

            #Check if image size is a multiple of the chunk plus oob size.
            if size % (csize + osize) != 0:
                continue

            headers = get_anchor_headers(image, csize, osize, anchor)
            print "Found %d %s headers" % (len(headers), anchor)

            constant_count = count_constant_oobs(image, headers, osize)

            print "Found %d constant oobs for the headers." \
                  % (constant_count)

            count = len(headers) - constant_count

            if count >= max_count:
                max_count = count
                best_csize = csize
                best_osize = osize
                best_headers = headers

    if max_count == 0:
        print "Unable to determine sizes."
        return None

    print "Most likely chunk and oob sizes: %d, %d" % (best_csize, best_osize)

    guess_oob_offset(image, best_headers, best_osize)

    return best_osize, best_csize


def count_constant_oobs(image, chunks, oobsize):
    oobs = YaffsParser.get_oob_bytes(image, chunks, oobsize)
    constants_count = 0
    constant = '\xff' * oobsize

    for oob in oobs:
        if oob == constant:
            constants_count += 1

    return constants_count

def guess_oob_offset(image, headers, oob_size):
    oobs_bytes = YaffsParser.get_oob_bytes(image, headers, oob_size)

    for offset in xrange(1, oob_size-17):
        parsed = []

        for bytes in oobs_bytes:
            parsed_oob = YaffsOobTag(bytes, offset)
            if not parsed_oob.isHeaderTag:
                parsed = []
                break
            else:
                parsed.append(parsed_oob)

        object_ids = set([o.object_id for o in parsed])

        if len(object_ids) == 1:
            print "OOB tag offset is %d" % offset
            print "Object id: %s" % str(object_ids)
            return

    print "Unable to determine OOB tag offset."
    return


def get_headers(image, chunk_size, oob_size):
    chunk_pairs = YaffsParser.extract_chunks(image, chunk_size, oob_size)

    #First filter, The first byte should be 0x01
    #Litte endian
    header_chunks = [YaffsHeader(c) for c, obb in chunk_pairs
                     if c.get_bytes(4) == '\x01\00\00\00']

    #Now use the second, slower filter.
    header_chunks = [c for c in header_chunks
                     if YaffsHeader(c).is_valid()]

    return header_chunks


def get_anchor_headers(image, chunk_size, oob_size, anchor):
    header_chunks = get_headers(image, chunk_size, oob_size)

    anchor_headers = [h for h in header_chunks
                        if h.name == anchor]

    return anchor_headers


def main():
    """
    Assume we pass this script the image file path as an argument on the
    command line.
    """
    DEFAULT_ANCHOR = ['contacts2.db']

    parser = YaffsParser.get_argparser()
    parser.add_argument("--anchors",
                        help="The filenames to use for anchoring the search. Default: %s" % DEFAULT_ANCHOR,
                        nargs='*', default=DEFAULT_ANCHOR, dest="anchors")
    args = parser.parse_args()

    for anchor in args.anchors:
        scan_file(args.imagefile, anchor)

    pass


if __name__ == '__main__':
    main()
