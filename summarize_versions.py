__author__ = 'wallsr'

import YaffsParser
import math
import sys


def main():
    parser = YaffsParser.get_argparser()
    args = parser.parse_args()

    #read in and order all of the blocks, by reverse order of sequence number
    sorted_blocks = YaffsParser.extract_ordered_blocks(args.imagefile,
                                                       args.chunksize,
                                                       args.oobsize,
                                                       args.blocksize,
                                                       args.tag_offset)

    objects = YaffsParser.extract_objects(sorted_blocks)

    current_objects = [o for o in objects if not o.is_deleted]

    current_file_objects = []

    for obj in current_objects:
        #check the object type from the first header chunk.
        if len(obj.versions) > 0 and obj.versions[0][0][1].obj_type == 1:
            current_file_objects.append(obj)

    print "object_id,name,time_diff,expected,actual"

    for obj in current_file_objects:
        missing = get_missing_chunks_by_version(obj)

        for expected, actual, time_diff, name in missing:
            if time_diff < 0:
                pass

            print "%d\t%s\t%s\t%d\t%d" % (obj.object_id, name, time_diff, expected, actual)


def get_missing_chunks_by_version(obj):
    """

    """
    missing = []
    most_recent_time = None

    if obj.object_id == 624:
        pass

    for version in obj.versions:
        header_oob, header_chunk = version[0]

        if most_recent_time is None:
            most_recent_time = header_chunk.mtime

        filesize = header_oob.num_bytes
        num_chunks_expected = int(math.ceil(filesize * 1.0 / header_chunk.length))
        num_chunks_actual = len(version) - 1

        time_diff = most_recent_time - header_chunk.mtime

        # I am not entirely sure why this happens, but I have seen
        # instance of objects were the modification time is before the creation
        # time.
        if time_diff < 0:
            sys.stderr.write('Object modification times are unreliable. Skipping object %d, %s\n'
                       % (obj.object_id, header_chunk.name))
            return []

        if num_chunks_actual > num_chunks_expected:
            sys.stderr.write('More chunks than expected?! Probably a bug in our code. Object: %d, %s'
                       % (obj.object_id, header_chunk.name))

        missing.append((num_chunks_expected, num_chunks_actual, time_diff, header_chunk.name))

    return missing



if __name__ == '__main__':
    main()