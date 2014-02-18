__author__ = 'wallsr'

"""
This script attempts to figure out the sequence numbers of the deleted blocks


"""

import YaffsParser


def main():
    parser = YaffsParser.get_argparser()

    args = parser.parse_args()

    #read in and order all of the blocks
    sorted_blocks = YaffsParser.extract_ordered_blocks(args.imagefile,
                                                       args.pagesize,
                                                       args.oobsize,
                                                       args.blocksize,
                                                       tag_offset=args.tag_offset)

    missing_set = get_missing_block_numbers(sorted_blocks)


def get_missing_block_numbers(sorted_blocks):
    """
    Returns a set of missing sequence numbers, if any exist.
    Otherwise, returns None.
    """
    #Must have at least two blocks
    if len(sorted_blocks) <= 1:
        return

    print "Excluding erased blocks, because they don't have valid sequence numbers"

    blocks = [b for b in sorted_blocks if not b.is_erased]

    seq_set = set([b.sequence_num for b in blocks])

    print "Found %d unique sequence numbers" % len(seq_set)

    #Let's check to make sure that no two blocks have the same sequence number.
    if len(seq_set) < len(blocks):
        print "Warning: Repeated sequence numbers.",
        import collections
        counter = collections.Counter([b.sequence_num for b in blocks])
        print [(element, count) for element, count in counter.most_common() if count > 1]

    #The blocks are sorted in reverse
    last = blocks[0].sequence_num
    first = blocks[-1].sequence_num

    if last == 4294967295:
        print "Sequence numbers might have rolled over. Weird! Stopping."
        return

    if len(blocks) == (last - first + 1):
        print "None of the block sequence numbers are missing."
        return set([])

    missing_set = set(range(first, last + 1)) - seq_set
    print "Missing %d sequence numbers." % len(missing_set)

    holes = []

    for x in range(1, len(blocks)):
        #check if the blocks are not contiguous
        if blocks[x].sequence_num != blocks[x-1].sequence_num-1:
            hole_start = blocks[x].sequence_num + 1
            hole_end = blocks[x-1].sequence_num - 1

            holes.append((hole_start, hole_end))

    print "Found %d holes." % len(holes)

    return missing_set


if __name__ == '__main__':
    main()