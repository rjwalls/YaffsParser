__author__ = 'wallsr'

from YaffsClasses.YaffsChunk import YaffsHeader
import YaffsParser
import os
import datetime
import time

import summarize_deleted_blocks

def main():
    parser = YaffsParser.get_argparser()
    args = parser.parse_args()

    print args.imagefile, args.chunksize, args.oobsize, args.blocksize, args.tag_offset
    print "Script started: ", datetime.datetime.now()
    print 'File size: ', os.path.getsize(args.imagefile)

    #read in and order all of the blocks, by reverse order of sequence number
    sorted_blocks = YaffsParser.extract_ordered_blocks(args.imagefile,
                                                       args.chunksize,
                                                       args.oobsize,
                                                       args.blocksize,
                                                       args.tag_offset)



    nonerased_blocks = [b for b in sorted_blocks if not b.is_erased]

    print '%d blocks' % len(sorted_blocks)
    print 'Sequence number range: %d -- %d' \
          % (nonerased_blocks[-1].sequence_num, nonerased_blocks[0].sequence_num)

    print 'Found %d erased blocks.' % (len(sorted_blocks) - len(nonerased_blocks))

    #This can happen if the phone is turned off while writing.
    print 'Found %d blocks with mismatched sequence numbers' \
          % len([block for block in sorted_blocks if block.possible_parse_error])

    missing_seq_nums = summarize_deleted_blocks.get_missing_block_numbers(sorted_blocks)

    objects = YaffsParser.extract_objects(sorted_blocks)

    print 'Found %d objects' % len(objects)
    print 'Found %d objects with a header.' % len([obj for obj in objects if 0 in obj.chunkDict])
    print 'Found %d deleted objects.' % len([obj for obj in objects if obj.is_deleted])

    recent_pairs = []
    total_pairs_count = 0
    for block in sorted_blocks:
        recent_pairs.extend([(tag, chunk) for tag, chunk in block.chunk_pairs if tag.is_most_recent])
        total_pairs_count += len(block.chunk_pairs)

    print 'Number of Recent chunks: %d' % len(recent_pairs)
    print 'Total number of chunks: %d' % total_pairs_count
    print 'Fraction recent: %0.2f' % (float(len(recent_pairs)) / total_pairs_count)

    last_time = None
    first_time = None

    for block in nonerased_blocks:
        for tag, chunk in block.chunk_pairs:
            if tag.isHeaderTag:
                print block.sequence_num
                last_time = time.ctime(YaffsHeader(chunk).mtime)
                break

        if last_time:
            break


    for x in xrange(len(nonerased_blocks)-1, 0, -1):
        block = nonerased_blocks[x]
        for y in xrange(len(block.chunk_pairs)-1, 0, -1):
            tag, chunk = block.chunk_pairs[y]
            if tag.isHeaderTag:
                print block.sequence_num
                first_time = time.ctime(YaffsHeader(chunk).mtime)
                break
        if first_time:
            break


    print 'Oldest object modification: %s' % first_time
    print 'Newest object modification: %s' % last_time



if __name__ == '__main__':
    main()