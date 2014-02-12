import struct;

class YaffsOobTag:
    """
    oobBytes should be the raw bytes of the out of band area of NAND.
    """

    def __init__(self, oobBytes=None, tag_offset=1):
        if oobBytes is None:
            return

        #Reference to the parent block class for this Oobtag.
        self.block_cls = None
        self.tag_offset = tag_offset

        # The Layout of the oob is not controlled entirely by Yaffs so
        # the specific offsets for these fields may be different for different
        # phones.
        (self.block_status,
         self.block_seq,
         self.object_id,
         self.chunk_id,
         self.num_bytes) = struct.unpack("<%dxsIIII%dx"
                                         % (tag_offset, len(oobBytes)-17-tag_offset),
                                         oobBytes)
        
        #check if the top byte is 0x80 or 0xC0 which denotes a header chunk
        topByte = self.chunk_id >> 24
        
        self.isBadBlock = (self.block_status != '\xff')
        
        self.isHeaderTag = (topByte == 0x80 or topByte == 0xC0)
        self.is_shrink_header = (topByte == 0xC0)
        
        #The top byte in objectId field is overloaded in the header tag
        # to denote the type of object. We need to mask that out
        if self.isHeaderTag:
            self.object_id &= 0x00ffffff
            self.chunk_id = 0
        
        #erased or empty block
        self.is_erased = (self.block_seq == 0xffffffff)
        
        #non-empty block, but the object has been deleted
        self.isDeleted = (self.chunk_id == 0xc0000004)

        #This field is set by the Yaffs Object upon
        # reconstruction of the different versions.
        #It denotes that this chunk is used by the most recent
        #version of the Yaffs object.
        self.is_most_recent = False


    def __str__(self):
        return 'Block Seq: %d, Object Id: %d, Chunk Id: %d, Num. Bytes: %d' \
               % (self.block_seq, self.object_id, self.chunk_id, self.num_bytes)