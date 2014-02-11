# Scans the YAFFS2 image and rebuilds the filesystem.

import argparse
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


def main():

    print "=" * 40
    print SCRIPT_NAME
    print "v%s" % VERSION
    print "By Robert Walls"
    print "Copyright 2014"
    print "=" * 40

    parser = argparse.ArgumentParser(description="Scans the YAFFS2 image and attempts to rebuild the filesystem.");

    parser.add_argument("imagefile", help="The path to the YAFFS2 image.", type=str);

    parser.add_argument("-p", help="The NAND page size (e.g. 2048 bytes). Default: %d"%DEFAULT_PAGESIZE, type=int, default=DEFAULT_PAGESIZE, dest="pagesize");

    parser.add_argument('-o', help="The NAND OOB (Out of Band) size. Default: %d"%DEFAULT_OOB, type=int, default=DEFAULT_OOB,dest="oobsize");

    parser.add_argument('-b', help="The NAND Block size in chunks per block. Default: %d"%DEFAULT_PAGES_PER_BLOCK, type=int, default=DEFAULT_PAGES_PER_BLOCK,dest="blocksize");

    args = parser.parse_args()

    print args.imagefile, args.pagesize, args.oobsize, DEFAULT_OOB_TAG_OFFSET

    print "Script started: ", datetime.datetime.now()

    #read in and order all of the blocks
    sorted_blocks = extract_ordered_blocks(args.imagefile, args.pagesize, args.oobsize, args.blocksize, tag_offset=DEFAULT_OOB_TAG_OFFSET)

    objects = extract_objects(sorted_blocks)

    for object in objects:
        if object.object_id == 692:
            object.splitByVersion()
            pass

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
    This function will scan through the image file and
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
        pairsRev = block.chunk_pairs
        pairsRev.reverse()

        for tag, chunk in pairsRev:
            #Skip erased tags
            if tag.is_erased:
                continue

            if tag.object_id not in objects:
                objects[tag.object_id] = YaffsObject.YaffsObject(tag.object_id)

            if tag.isHeaderTag:
                chunk = YaffsChunk.YaffsHeader(chunk)

            #Pairs should be added in the reverse order of how they
            #were written, i.e., the most recent first.
            objects[tag.object_id].chunk_pairs.append((tag, chunk))

    objectsSplit = []

    for id in objects:
        splits = objects[id].splitByDeletions()

        for split in splits:
            objectsSplit.append(split)

    for object in objectsSplit:
        object.reconstruct()

    for id in objects:
        objects[id].reconstruct()

    for id in objects:
        objects[id].splitByVersion()

    print 'Found %d objects' %len(objects)
    print 'Found %d deleted objects.' %len([object for id, object in objects.iteritems() if object.isDeleted])

    print 'Found {0} objects with a header.'.format(len([x for x in objects if 0 in objects[x].chunkDict]))

    print 'Found %d objects after spliting.' %len(objectsSplit)

    print 'Found %d deleted objects after splitting.' %len([object for object in objectsSplit if object.isDeleted])

    return objectsSplit


def extract_chunks(imagefile, chunk_size, oob_size, swap=False):
    """
    Extract the chunks from the image, but do not attempt to order them into
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


def extract_ordered_blocks(imagefile, chunk_size, oob_size, block_size, swap=False, tag_offset=29):
    """

    """

    print 'File size: ', os.path.getsize(imagefile)

    chunk_pairs = extract_chunks(imagefile, chunk_size, oob_size, swap)

    print 'Found %d chunks.' % len(chunk_pairs)

    chunks = [c for c, o in chunk_pairs]
    oob_bytes = Scanner.get_oob_bytes(imagefile, chunks, oob_size)
    oobs = [YaffsOobTag.YaffsOobTag(oob, tag_offset) for oob in oob_bytes]

    blocks = []

    current_block = None
    current_seqnum = None

    for oob, chunk in zip(oobs, chunks):
        if current_block is None or len(current_block.chunk_pairs) == block_size:
            current_block = YaffsBlock.YaffsBlock(oob.block_seq)
            current_seqnum = oob.block_seq
            current_block.is_erased = oob.is_erased
            blocks.append(current_block)

        #Add tag and chunk
        current_block.chunk_pairs.append((oob, chunk))

        current_block.has_erased_chunks |= oob.is_erased

        #Check if tag has the correct sequence number
        current_block.possible_parse_error |= (not oob.is_erased and
                                               oob.block_seq != current_block.sequence_num)

    sorted_blocks = sorted(blocks, reverse=True, key=lambda bl: bl.sequence_num)

    print 'Found %d blocks.' % len(sorted_blocks)

    print 'Found %d good blocks.' \
          % len([block for block in sorted_blocks if not (block.is_erased or block.possible_parse_error)])

    print 'Found %d erased blocks.' \
          % len([block for block in sorted_blocks if block.is_erased])

    print 'Found %d blocks with erased chunks.' \
          % len([b for b in sorted_blocks if block.has_erased_chunks])

    #This can happen if the phone is turned off while writing.
    print 'Found %d blocks with mismatched sequence numbers' \
          % len([block for block in sorted_blocks if block.possible_parse_error])

    return sorted_blocks


if __name__ == '__main__':
    main()
