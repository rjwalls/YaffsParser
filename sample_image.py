__author__ = 'wallsr'

import YaffsParser
import math
import os
import random


def main():
    parser = YaffsParser.get_argparser()
    parser.add_argument("--fraction",
                        help='The file size of the sampled file as a fraction of the original.',
                        type=float, default=0.01, dest="sample_fraction")

    args = parser.parse_args()

    image_size = os.path.getsize(args.imagefile)
    #We use ceiling so that we always have at least one block to grab, even
    #if the fraction is 0.000000000001
    total_num_blocks = image_size / (args.blocksize * (args.chunksize + args.oobsize))
    num_blocks = math.ceil(total_num_blocks * args.sample_fraction)
    num_blocks = int(num_blocks)

    blocks = YaffsParser.extract_ordered_blocks(args.imagefile,
                                                args.chunksize,
                                                args.oobsize,
                                                args.blocksize,
                                                args.tag_offset)

    sampled_blocks = random.sample(blocks, num_blocks)

    root, ext = os.path.splitext(args.imagefile)
    outfile = "%s_sampled_%s%s" % (root, str(args.sample_fraction).replace('.', "d"), ext)
    print 'Outfile: %s' % outfile

    with open(args.imagefile, 'rb') as f:
        with open(outfile, 'wb') as out:
            for sblock in sampled_blocks:
                f.seek(sblock.chunk_pairs[0][1].offset)
                out.write(f.read((args.chunksize + args.oobsize) * args.blocksize))


if __name__ == '__main__':
    main()