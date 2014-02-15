__author__ = 'wallsr'

import YaffsParser


def main():
    parser = YaffsParser.get_argparser()

    args = parser.parse_args()

    blocks = YaffsParser.extract_ordered_blocks(args.imagefile,
                                                args.chunksize,
                                                args.oobsize,
                                                args.blocksize,
                                                args.tag_offset)

    objects = YaffsParser.extract_objects(blocks)

    tuple_set = set()

    for object in objects:
        for version in object.versions:
            tuple_set.add((object.object_id, version[0][1].name))

    for tuple in tuple_set:
        print tuple


if __name__ == '__main__':
    main()