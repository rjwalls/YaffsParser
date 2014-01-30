import struct;

class YaffsOobTag:
    """
    oobBytes should be the raw bytes of the out of band area of NAND.
    """

    def __init__(self, oobBytes=None, tag_offset=1):
        if oobBytes is None:
            return

        #TODO: The Layout of the oob is not controlled entirely by Yaffs so
        # the specific offsets for these fields may be different for different
        # phones.
        (self.blockStatus,
         self.blockSeq,
         self.object_id,
         self.chunkId,
         self.bytenum) = struct.unpack("<%dxsIIII%dx" % (tag_offset, len(oobBytes)-17-tag_offset),
                                       oobBytes)
        
        #check if the top byte is 0x80 or 0xC0 which denotes a header chunk
        topByte = self.chunkId >> 24
        
        self.isBadBlock = (self.blockStatus != '\xff')
        
        self.isHeaderTag = (topByte == 0x80 or topByte == 0xC0)
        
        #The top byte in objectId field is overloaded in the header tag
        # to denote the type of object. We need to mask that out
        if self.isHeaderTag:
            self.object_id = self.object_id & 0x00ffffff
        
        #erased or empty block
        self.isErased = (self.blockSeq == 0xffffffff)
        
        #non-empty block, but the object has been deleted
        self.isDeleted = (self.chunkId == 0xc0000004)
