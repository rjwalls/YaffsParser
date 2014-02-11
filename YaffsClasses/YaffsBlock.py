
class YaffsBlock:

    def __init__(self, seqNum):
        #create a list of tag, chunk pairs
        self.chunk_pairs = []
        #create a list of chunk oob tags
        self.chunkOobTags = []
        self.sequence_num = seqNum
        
        #We set this to true if the block does not have the
        #number of chunks we expect.
        self.possible_parse_error = False

        self.has_erased_chunks = False
        
        self.is_erased = False

    def __str__(self):
        return 'Sequence Num: %d, Chunk Pairs: %d, Is Erased: %s' \
               % (self.sequence_num, len(self.chunk_pairs), self.is_erased)
