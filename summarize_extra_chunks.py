__author__ = 'wallsr'

import YaffsParser


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

    print "object_id,name,chunk_id,count"

    for obj in current_file_objects:
        count = 0
        name = obj.versions[0][0][1].name

        for id in obj.chunkDict:
            if id == 0:
                continue
            if len(obj.chunkDict[id]) > 1:
                print "%d\t%s\t%d\t%d" % (obj.object_id, name, id, len(obj.chunkDict[id]))


if __name__ == '__main__':
    main()