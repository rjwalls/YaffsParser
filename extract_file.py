__author__ = 'wallsr'

import os
import sys
import Scanner
from YaffsClasses.YaffsOobTag import YaffsOobTag
import YaffsParser
from optparse import OptionParser


def extract_files(image, filenames, chunksize, oobsize, oob_tag_offset):
    """
    Extracts the most recent verison of every file in the filenames
    list.
    """
    blocks = YaffsParser.extract_ordered_blocks(image, chunksize, oobsize, 64, tag_offset=oob_tag_offset)
    objects = YaffsParser.extract_objects(blocks)

    for object in objects:
        object.splitByVersion()

    destination = os.path.dirname(image)

    for name in filenames:
        extract_file(objects, name, destination)


def extract_file(objects, filename, destination_path):
    """

    """
    print 'Looking for', filename

    for object in objects:
        if len(object.versions) == 0:
            continue

        if object.versions[0][0][1].name == filename:
            root, ext = os.path.splitext(filename)
            outfile = os.path.join(destination_path,
                                   root + "_{0}".format(object.object_id) + ext)

            print outfile

            object.writeVersion(name=outfile)


def main():
    """
    Assume we pass this scirpt the image file as an argument
    """

    usage = 'usage: %prog [options] imagefile_1 .. imagefile_n'

    parser = OptionParser(usage=usage)
    parser.add_option('--chunksize', action='store', type='int',
                      dest='chunk_size', default=2048)
    parser.add_option('--oobsize', action='store', type='int',
                      dest='oob_size', default=64)
    parser.add_option('--oobtagoffset', action='store', type='int',
                      dest='oob_tag_offset', default=29)
    parser.add_option('-f', '--filenames', dest='filenames')

    options, args = parser.parse_args()

    filenames = options.filenames.split(',')

    for image in args:
        extract_files(image, filenames, options.chunk_size,
                      options.oob_size, options.oob_tag_offset)


if __name__ == '__main__':
    main()

