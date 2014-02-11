__author__ = 'wallsr'

"""
This script attempts to determine important characteristics of a Yaffs phone image.

Ideally, this functionality will be incorporated into a new version of the Yaffs parser.
"""

import os

from optparse import OptionParser
from YaffsClasses.YaffsChunk import YaffsHeader
from YaffsClasses.YaffsOobTag import YaffsOobTag

import YaffsParser


def scan_file(image):
    chunk_sizes = [1024, 2048, 4096]
    oob_sizes = [32, 64, 128]

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

            headers = get_contacts_headers(image, csize, osize)
            print "Found %d contacts2.db headers" % (len(headers))

            constant_count = count_constant_oobs(image, headers, osize)

            print "Found %d constant oobs for the contacts headers." \
                  % (constant_count)

            count = len(headers) - constant_count

            if count >= max_count:
                max_count = count
                best_csize = csize
                best_osize = osize
                best_headers = headers

    if best_csize is None:
        print "Unable to determine sizes."
    else:
        print "Most likely chunk and oob sizes: %d, %d" % (best_csize, best_osize)

    guess_oob_offset(image, best_headers, best_osize)




def count_constant_oobs(image, chunks, oobsize):
    oobs = get_oob_bytes(image, chunks, oobsize)
    constants_count = 0
    constant = '\xff' * oobsize

    for oob in oobs:
        if oob == constant:
            constants_count += 1

    return constants_count


def get_oob_bytes(imagepath, chunks, oob_size):
    oobs = []

    with open(imagepath, 'rb') as file:
        for chunk in chunks:
            file.seek(chunk.offset+chunk.length)
            oob = file.read(oob_size)
            oobs.append(oob)

    return oobs


def guess_oob_offset(image, headers, oob_size):
    oobs_bytes = get_oob_bytes(image, headers, oob_size)

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


def get_contacts_headers(image, chunk_size, oob_size):
    header_chunks = get_headers(image, chunk_size, oob_size)

    contacts_headers = [h for h in header_chunks
                        if h.name == 'contacts2.db']

    return contacts_headers


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
