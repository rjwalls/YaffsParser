import struct;

class YaffsOobTag:

    #oobBytes should be the raw bytes of the out of band area of NAND.
    def __init__(self, oobBytes):
        (self.blockStatus, self.blockSeq, self.objectId, self.chunkId, self.bytenum) = struct.unpack("<xsIIII%dx"%(len(oobBytes)-18), oobBytes);
        
        #check if the top byte is 0x80 or 0xC0 which denotes a header chunk
        topByte = self.chunkId >> 24
        
        self.isBadBlock = (self.blockStatus != '\xff')
        
        self.isHeaderTag = (topByte == 0x80 or topByte == 0xC0)
        
        #The top byte in objectId field is overloaded in the header tag to denote the type of object. We need to mask that out
        if self.isHeaderTag :
            self.objectId = self.objectId & 0x00ffffff
        
        #erased or empty block
        self.isErased = (self.blockSeq == 0xffffffff)
        
        #non-empty block, but the object has been deleted
        self.isDeleted = (self.chunkId == 0xc0000004)
