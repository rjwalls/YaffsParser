
class YaffsBlock:

    def __init__(self, seqNum):
        #create a list of tag, chunk pairs
        self.chunkPairs = []
        #create a list of chunk oob tags
        self.chunkOobTags = []
        self.sequenceNum = seqNum
        
        #We set this to true if the block does not have the
        #number of chunks we expect.
        self.possibleParseError = False
        
        self.isErased = False
        
