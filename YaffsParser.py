# Scans the YAFFS2 image and rebuilds the filesystem.

import argparse
import summarize_deleted_blocks

import datetime
import os


from YaffsClasses import *

import Scanner

SCRIPT_NAME = "YaffsParser"
VERSION = "0.0"

DEFAULT_PAGESIZE = 2048
DEFAULT_PAGES_PER_BLOCK = 64
DEFAULT_OOB = 64
DEFAULT_OOB_TAG_OFFSET = 29


def get_argparser():
    """
    Assume we pass this scirpt the image file as an argument
    """

    parser = argparse.ArgumentParser(description="Scans the YAFFS2 image and attempts to rebuild the filesystem.");

    parser.add_argument("imagefile", help="The path to the YAFFS2 image.", type=str)

    parser.add_argument("-p", help="The NAND page size (e.g. 2048 bytes). Default: %d" % DEFAULT_PAGESIZE,
                        type=int, default=DEFAULT_PAGESIZE, dest="pagesize")

    parser.add_argument('-o', help="The NAND OOB (Out of Band) size. Default: %d" % DEFAULT_OOB,
                        type=int, default=DEFAULT_OOB, dest="oobsize")

    parser.add_argument('-b', help="The NAND Block size in chunks per block. Default: %d" % DEFAULT_PAGES_PER_BLOCK,
                        type=int, default=DEFAULT_PAGES_PER_BLOCK, dest="blocksize")

    parser.add_argument('-t', help="The tag offset within the OOB. Default: %d" % DEFAULT_OOB_TAG_OFFSET,
                        type=int, default=DEFAULT_OOB_TAG_OFFSET, dest="tag_offset")

    return parser


def main():

    print "=" * 40
    print SCRIPT_NAME
    print "v%s" % VERSION
    print "By Robert Walls"
    print "Copyright 2014"
    print "=" * 40

    parser = get_argparser()

    args = parser.parse_args()

    print args.imagefile, args.pagesize, args.oobsize, args.blocksize, args.tag_offset
    print "Script started: ", datetime.datetime.now()
    print 'File size: ', os.path.getsize(args.imagefile)

    #read in and order all of the blocks, by reverse order of sequence number
    sorted_blocks = extract_ordered_blocks(args.imagefile,
                                           args.pagesize,
                                           args.oobsize,
                                           args.blocksize,
                                           args.tag_offset)

    print 'Found %d blocks.' % len(sorted_blocks)
    print 'Found %d good blocks.' \
          % len([block for block in sorted_blocks
                 if not (block.is_erased or block.possible_parse_error)])

    print 'Found %d erased blocks.' \
          % len([block for block in sorted_blocks if block.is_erased])

    #This can happen if the phone is turned off while writing.
    print 'Found %d blocks with mismatched sequence numbers' \
          % len([block for block in sorted_blocks if block.possible_parse_error])

    missing_seq_nums = summarize_deleted_blocks.get_missing_block_numbers(sorted_blocks)

    objects = extract_objects(sorted_blocks)

    print 'Found %d objects' % len(objects)
    print 'Found %d deleted objects.' % len([obj for obj in objects if obj.is_deleted])
    print 'Found %d objects with a header.' % len([obj for obj in objects if 0 in obj.chunkDict])

    for obj in objects:
        if len(obj.versions) == 0:
            continue

        oob, chunk = obj.versions[0][0]

        if oob.num_bytes == 0 and chunk.name == 'deleted':
            obj.is_deleted = True


    for object in objects:
        if object.object_id == 692:

            #We need to look at the each version to see if any holes exist in
            #the block sequence numbers that might affect the chunks,
            # i.e., missing blocks that might have contained chunks
            #of the particular version.
            holey_versions = []

            for version in object.versions:
                for chunk_id in version:
                    if chunk_id == 0:
                        version_seq_num = version[0][0].block_seq
                        continue

                    oob, chunk = version[chunk_id]

                    if oob.is_most_recent:
                        continue
                    if oob.block_seq == version_seq_num:
                        continue
                    if oob.block_seq > version_seq_num:
                        print "Wait! This chunk was written after the header. Error."
                        break
                    if oob.block_seq < version_seq_num:
                        between = set(range(oob.block_seq+1, version_seq_num)) & missing_seq_nums
                        if len(between) > 0:
                            #print "Chunk and version header are separated by %d holes." % len(between)
                            holey_versions.append(version)
                            break

            object.holey_versions = holey_versions
            #print 'Found %d versions with holes.' % len(holey_versions)

            for version in holey_versions:
                header_oob, header_chunk = version[0]

                if header_oob.is_shrink_header:
                    pass

                size = 0

                for id in version:
                    if id == 0:
                        continue
                    else:
                        size += version[id][0].num_bytes

                if size != header_oob.num_bytes:
                    #TODO: Is this an indication that a certain version
                    #of a file cannot be recovered due to missing chunks?
                    #How will shrink headers impact this?
                    print 'Size mismatch.'



    #estimateOldChunks(objects)

    #objects_deleted = [object for object in objects if object.isDeleted]

    #printObjectInfo(objects)

    #testVersionSplit(objects)

    #testWriteVersion(objects)

    #printAllObjectNames(objects)

    testExtractSpecificFile(objects)

    return


def testExtractSpecificFile(objects):

    for object in objects:
        if object.objectId == 564:
        #if object.versions[0][0][1].name == 'contacts2.db':
            print 'found object'

            object.splitByVersion()
            print 'Object has %d version(s)' % len(object.versions)

            object.writeVersion()


def printAllObjectNames(objects):
    names = []

    for object in objects:
        for version in object.versions:
            if version[0]:
                names.append(version[0][1].name)

    #Remove duplicates and sort
    names = sorted(set(names))

    for name in names:
        print name


def testWriteVersion(objects) :

    for object in objects :
        if object.objectId == 2889:
            print 'testing write of version'
            object.writeVersion(2)


def testVersionSplit(objects):
    for object in objects:
            object.splitByVersion()


def printObjectInfo(objects) :
    errors=0

    for object in objects :
        try:
            print 'Object id:', object.objectId

            for (headerTag, chunk) in object.chunkDict[0] :
                if hasattr(chunk, 'name'):
                    print chunk.name
        except:
            errors += 1

    print 'Encountered {0} errors when trying to print object info.'.format(
        errors)


def estimateOldChunks(objects) :
    #This function will perform a rough estimate of the number of old chunks.
    sumOld = 0

    with open('tmp.out',  'wb') as f :

        for object in objects :
            sum = object.SimpleOldChunkCount()

            f.write(str(sum) + '\n')

            sumOld += sum

    print 'Number of old chunks: ', sumOld
    print 'Average num of old chunks: ', (sumOld / len(objects))


def extract_objects(blocks):
    """
    This function will scan through the list of Yaffs blocks and
    extract objects based on the found object header tags.
    """

    #The blocks should be sorted in by reverse sequence number as
    #the sequence number provides a temporal ordering
    sorted_blocks = sorted(blocks, reverse=True, key=lambda bl: bl.sequence_num)

    objects = {}

    print 'Extracting objects...'

    #scan through the list of blocks. Should be sorted in reverse sequence order.
    for block in sorted_blocks:
        #skip erased blocks
        if block.is_erased:
            continue

        #Add the chunks in reverse order they were written to the block
        #We use the list here to create a copy of the list.
        pairs_reversed = list(block.chunk_pairs)
        pairs_reversed.reverse()

        for tag, chunk in pairs_reversed:
            #Skip erased tags
            if tag.is_erased:
                continue

            if tag.object_id not in objects:
                objects[tag.object_id] = YaffsObject.YaffsObject(tag.object_id)

            if tag.isHeaderTag:
                chunk = YaffsChunk.YaffsHeader(chunk)

                if chunk.name == 'deleted':
                    tag.isDeleted = True

            #Pairs should be added in the reverse order of how they
            #were written, i.e., the most recent first.
            objects[tag.object_id].chunk_pairs.append((tag, chunk))

    split_objects = []

    for object_id in objects:
        splits = objects[object_id].splitByDeletions()
        split_objects.extend(splits)

    for obj in split_objects:
        obj.reconstruct()
        obj.splitByVersion()

    return split_objects


def extract_chunks(imagefile, chunk_size, oob_size, swap=False):
    """
    Extract the chunks from the image, but does not attempt to order them into
    blocks.
    """

    size = os.path.getsize(imagefile)

    #Check if image size is a multiple of the chunk plus oob size.
    if size % (chunk_size + oob_size) != 0:
        print 'Warning! File size is not a multiple of the chunk pairs.'

    chunk_pairs = []

    with open(imagefile, "rb") as f:
        #Check if we have reached the end of the file
        #only read in complete pairs
        while f.tell() <= size - (chunk_size + oob_size):
            #We aren't sure whether the image starts with the oob or the page bytes.
            if not swap:
                chunk = YaffsChunk.YaffsChunk(imagefile, f.tell(), chunk_size)

                #Seek from the current position to skip the chunk bytes
                f.seek(chunk_size, True)
                #oob = YaffsOobTag.YaffsOobTag(f.read(oob_size))
                oob_offset = f.tell()
                f.seek(oob_size, True)
            else:
                #oob = YaffsOobTag.YaffsOobTag(f.read(oob_size))
                oob_offset = f.tell()
                f.seek(oob_size, True)
                chunk = YaffsChunk.YaffsChunk(imagefile, f.tell(), chunk_size)
                f.seek(chunk_size, True)


            chunk_pairs.append((chunk, oob_offset))

    return chunk_pairs


def extract_ordered_blocks(imagefile, chunk_size, oob_size, block_size, tag_offset):
    """
    This method extracts ordered blocks from the yaffs image file.
    """
    chunk_pairs = extract_chunks(imagefile, chunk_size, oob_size, False)

    chunks = [c for c, o in chunk_pairs]
    oob_bytes = get_oob_bytes(imagefile, chunks, oob_size)
    oobs = [YaffsOobTag.YaffsOobTag(oob, tag_offset) for oob in oob_bytes]

    blocks = []

    current_block = None

    for oob, chunk in zip(oobs, chunks):
        if current_block is None or len(current_block.chunk_pairs) == block_size:
            current_block = YaffsBlock.YaffsBlock(oob.block_seq)
            current_block.is_erased = oob.is_erased
            blocks.append(current_block)

        #Add tag and chunk
        current_block.chunk_pairs.append((oob, chunk))
        oob.block_cls = current_block

        #Check if tag has the correct sequence number
        current_block.possible_parse_error |= (not oob.is_erased and
                                               oob.block_seq != current_block.sequence_num)

    sorted_blocks = sorted(blocks, reverse=True, key=lambda bl: bl.sequence_num)

    return sorted_blocks


def get_oob_bytes(imagepath, chunks, oob_size):
    oobs = []

    with open(imagepath, 'rb') as file:
        for chunk in chunks:
            file.seek(chunk.offset+chunk.length)
            oob = file.read(oob_size)
            oobs.append(oob)

    return oobs


if __name__ == '__main__':
    main()
