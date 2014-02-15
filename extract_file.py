__author__ = 'wallsr'

import os
import time
import YaffsParser
from optparse import OptionParser


def extract_files(image, filenames, chunksize, oobsize, blocksize, oob_tag_offset, versions):
    """
    Extracts the most recent version of every file in the filenames
    list.
    """
    blocks = YaffsParser.extract_ordered_blocks(image, chunksize, oobsize,
                                                blocksize, oob_tag_offset)
    objects = YaffsParser.extract_objects(blocks)

    destination = os.path.dirname(image)

    for name in filenames:
        extract_file(objects, name, destination, versions)


def extract_file(objects, filename, destination_path, versions):
    """

    """
    print 'Looking for', filename

    for object in objects:
        if len(object.versions) == 0:
            continue

        # Deleted objects might have the name 'deleted'
        # so we need to check past versions
        name_set = set([x[0][1].name for x in object.versions])

        if filename in name_set:
            print 'Object %d has %d versions.' % (object.object_id, len(object.versions))
            print 'Most recent version: %d bytes' % object.versions[0][0][0].num_bytes

            largest_index = 0
            byte_count = 0

            #Find the version with the most bytes
            for x in xrange(len(object.versions)):
                if object.versions[x][0][0].num_bytes > byte_count:
                    largest_index = x
                    byte_count = object.versions[x][0][0].num_bytes

            print 'Largest version is %d: %d bytes' \
                  % (largest_index, object.versions[largest_index][0][0].num_bytes)

            root, ext = os.path.splitext(filename)

            for vnum in versions:
                header_oob, header_chunk = object.versions[vnum][0]

                print 'Version %d: %d bytes' % (vnum, header_oob.num_bytes)
                print 'modified: %s' % (time.ctime(header_chunk.mtime))

                #Create a unique string for the object by id and version
                #replace any negative values with 'n'
                obj_str = "_id%04d_v%03d" % (object.object_id, vnum)
                obj_str = obj_str.replace('-', 'n')

                outfile = os.path.join(destination_path, root + obj_str + ext)

                print outfile
                object.writeVersion(vnum, outfile)


def main():
    """
    Assume we pass this scirpt the image file as an argument
    """
    DEFAULT_VERSIONS = [0]

    parser = YaffsParser.get_argparser()

    parser.add_argument("--files",
                    help="The files to extract.",
                    nargs='*', dest="files")

    parser.add_argument("--versions",
                        help="The version numbers to extract, 0 is newest, -1 is oldest",
                        type=int,
                        default=DEFAULT_VERSIONS,
                        nargs='*', dest='version_numbers')

    args = parser.parse_args()

    extract_files(args.imagefile, args.files, args.chunksize,
                  args.oobsize, args.blocksize, args.tag_offset, args.version_numbers)


if __name__ == '__main__':
    main()

