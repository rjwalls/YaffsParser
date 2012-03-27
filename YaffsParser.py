# Scans the YAFFS2 image and rebuilds the filesystem.

import argparse;
import datetime;
import sys;
import os;
from sets import Set;

from YaffsClasses import *;

SCRIPT_NAME = "YaffsParser";
VERSION = "0.0"

DEFAULT_PAGESIZE = 2048;
DEFAULT_PAGES_PER_BLOCK = 64;
DEFAULT_OOB = 64;

def main():
    
    print "="*40;
    print SCRIPT_NAME;
    print "v%s"%VERSION;
    print "By Robert Walls";
    print "Copyright 2012";
    print "="*40;
    
    parser = argparse.ArgumentParser(description="Scans the YAFFS2 image and attempts to rebuild the filesystem.");
    
    parser.add_argument("imagefile", help="The path to the YAFFS2 image.", type=str);
    
    parser.add_argument("-p", help="The NAND page size (e.g. 2048 bytes). Default: %d"%DEFAULT_PAGESIZE, type=int, default=DEFAULT_PAGESIZE, dest="pagesize");
    
    parser.add_argument('-o', help="The NAND OOB (Out of Band) size. Default: %d"%DEFAULT_OOB, type=int, default=DEFAULT_OOB,dest="oobsize");
    
    parser.add_argument('-b', help="The NAND Block size in chunks per block. Default: %d"%DEFAULT_PAGES_PER_BLOCK, type=int, default=DEFAULT_PAGES_PER_BLOCK,dest="blocksize");
    
    args = parser.parse_args();
    
    print args.imagefile, args.pagesize, args.oobsize;
    
    print "Script started: ", datetime.datetime.now();
    
    #read in and order all of the blocks
    sortedBlocks = extractOrderedBlocks(args.imagefile, args.pagesize, args.oobsize, args.blocksize)
    
    objects = extractObjects(sortedBlocks)
    
    estimateOldChunks(objects)
    
    #objects_deleted = [object for object in objects if object.isDeleted]
    
    #printObjectInfo(objects_deleted)
    
    testVersionSplit(objects)
    
    #testWriteVersion(objects)
    
    #printAllObjectNames(objects)
    
    #testExtractSpecificFile(objects)
    
    return;
    
def testExtractSpecificFile(objects):
    
    for object in objects:
        if not object.hasNoHeader :
            if object.versions[0][0][1].name == 'contacts2.db':
                print 'found object'
                object.writeVersion(0)
    
def printAllObjectNames(objects) :
    names = []
    
    for object in objects:
        for version in object.versions:
            if version[0]:
                names.append(version[0][1].name)
    
    #Remove duplicates and sort
    names = sorted(Set(names))
    
    for name in names:
        print name

def testWriteVersion(objects) :

    for object in objects :
        if object.objectId == 2889:
            print 'testing write of version'
            object.writeVersion(2)
    
def testVersionSplit(objects) :

    for object in objects :
            object.splitByVersion()

def printObjectInfo(objects) :

    for object in objects :
        print object.objectId
    
        for (headerTag, chunk) in object.chunkDict[0] :
            print chunk.name

        
    
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
    
def extractObjects(sortedBlocks) :
    objects = {}
    
    print 'Extracting objects.'
    
    #scan through the list of blocks. Should be sorted in reverse sequence order.
    for block in sortedBlocks:
        
        #skip erased blocks
        if block.isErased :
            continue
    
        #Add the chunks in reverse order they were written to the block
        pairsRev = block.chunkPairs
        pairsRev.reverse()
        
        for tag, chunk in pairsRev :
        
            if not(tag.objectId in objects) :
                objects[tag.objectId] = YaffsObject.YaffsObject(tag.objectId)
                
            objects[tag.objectId].chunkPairs.append((tag,chunk))
        
            None
    
    objectsSplit = []
    
    for id in objects :
        splits = objects[id].splitByDeletions()
        
        for split in splits :
            objectsSplit.append(split)
    
    for object in objectsSplit :
        object.reconstruct()
    
    for id in objects :
        objects[id].reconstruct()
    
    print 'Found %d objects' %len(objects)
    
    print 'Found %d deleted objects.' %len([object for id, object in objects.iteritems() if object.isDeleted])
    
    print 'Found %d objects after spliting.' %len(objectsSplit)
    
    print 'Found %d deleted objects after splitting.' %len([object for object in objectsSplit if object.isDeleted])
    
    return objectsSplit
    
def extractOrderedBlocks(imagefile, pagesize, oobsize, blocksize):

    print 'File size: ', os.path.getsize(imagefile)

    blocks = []
    count = 0;

    with open(imagefile, "rb") as f:
        pageBytes = f.read(pagesize);
        oobBytes = f.read(oobsize);
        
        count = 0;
        
        currentBlock = None;
        
        while len(oobBytes) == oobsize:
            
            oob = YaffsOobTag.YaffsOobTag(oobBytes);
            chunk = YaffsChunk.YaffsChunk(imagefile, f.tell() - pagesize - oobsize, pagesize)
            
            #check if we hit a new block
            if count % blocksize == 0 :
                currentBlock = YaffsBlock.YaffsBlock(oob.blockSeq)
                
                currentBlock.isErased = oob.isErased
                
                blocks.append(currentBlock)
            
            #Add tag and chunk
            currentBlock.chunkPairs.append((oob, chunk))
            
            #Check if tag has the correct sequence number
            currentBlock.possibleParseError = ( oob.blockSeq != currentBlock.sequenceNum )              
            
            pageBytes = f.read(pagesize);
            oobBytes = f.read(oobsize);
            
            #check to see if we have reached the end of the file.
            if len(oobBytes) != oobsize:
                break;
                
            count += 1;
            
            
    sortedBlocks = sorted(blocks, reverse = True, key=lambda block: block.sequenceNum);
        
    print 'Scanned %d chunks.'%(count+1);
    print 'Found %d blocks.'%len(sortedBlocks)
            
    print 'Found %d good blocks.'%len([block for block in sortedBlocks if not (block.isErased or block.possibleParseError)])
    
    print 'Found %d erarsed blocks.' %len([block for block in sortedBlocks if block.isErased])
    
    #This can happen if the phone is turned off while writing.
    print 'Found %d blocks with mismatched sequence numbers' %len([block for block in sortedBlocks if block.possibleParseError])
    


    return sortedBlocks;
   


if __name__ == '__main__':
    main()