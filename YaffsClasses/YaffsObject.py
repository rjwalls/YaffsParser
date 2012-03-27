import math

class YaffsObject:

    def __init__(self, objId):
    
        #tuple of type tag, chunk
        self.chunkPairs = []
        self.objectId = objId
        self.versions = []
        
        #[(tag,chunk)...] tuple lists keyed by chunkId
        self.chunkDict = {}
        self.isDeleted = False
        self.hasNoHeader = False
    
        return
    
    #This is old logic, but a quick simple first step to get an idea
    #of how many old chunks are on Nand
    def SimpleOldChunkCount(self) :
        if self.isDeleted :
            return len(self.chunkPairs)
    
        chunkIds = [];
        old = 0;
        
        #the oobTags should already be sorted given the way they are read in.
        for tag, chunk in self.chunkPairs :            
            if not(tag.chunkId in chunkIds) :
                chunkIds.append(tag.chunkId)
            else :
                old += 1
                
        return old
        
    def splitByDeletions(self) :
        #This method will split the object based on the deletion headers.
        #We need to do this because object ids are reassigned after the old object has been deleted.
        
        splitObjects = []
        
        isFirstIteration = True
        
        obj = None
        
        #iterate through all chunkPairs
        for tag, chunk in self.chunkPairs :
        
            #if the the tag is a deleted header, then we know this is the start of a new object. Also do this even if the object does not properly start with a header
            isNewObject = (tag.isHeaderTag and tag.isDeleted)
            
            if isNewObject or isFirstIteration :
                obj = YaffsObject(self.objectId)
                splitObjects.append(obj)
                isFirstIteration = False
            
            obj.chunkPairs.append((tag,chunk))
            
        return splitObjects
        
    def splitByVersion(self) :
        #This method will split the object by the version.
        #TODO: It wont handle shrink headers yet.
        #TODO: Doesn't handle issues that arise from missing chunks
        #TODO: Probably want to remove this method and rewrite the reconstruct method.
        
        
        self.versions = []
        chunks = None
        
        for tag, chunk in self.chunkPairs :
            if tag.isHeaderTag :
                chunks = {}
                chunks[0] = (tag, chunk)
                
                self.versions.append(chunks)
                
            #if this is not a header, add it to every known version that doesn't have a chunk with this id
            else :
                for version in self.versions :
                    if not(tag.chunkId in version) :
                        version[tag.chunkId] = (tag, chunk)
        
        
        if False and len(self.versions) > 1 :
            print 'Object %d has %d versions' % (self.objectId, len(self.versions))
            print 'They have the following chunk counts per version'
        
            for version in self.versions :
                print len(version), version[0][1].name
                

            
        
    def reconstruct(self) :
        #This method should be called after all chunks for the object have been located. 
        #It will order all previous chunks by chunk id
        
        
        #print 'Reconstructing object %d from %d chunks.' % (self.objectId, len(self.chunkPairs))
        
        for tag, chunk in self.chunkPairs :
        
            if tag.isHeaderTag :
                                
                chunk.ParseHeaderChunk()
            
                if not(0 in self.chunkDict):
                    self.chunkDict[0] = [(tag, chunk)]
                else :
                    self.chunkDict[0].append((tag,chunk))
                
            if not tag.isHeaderTag :
                if not(tag.chunkId in self.chunkDict):
                    self.chunkDict[tag.chunkId] = [(tag, chunk)]
                else:
                    self.chunkDict[tag.chunkId].append((tag,chunk))
        
        if not 0 in self.chunkDict :
            #print 'Object has no header tag!'
            self.hasNoHeader = True
        else :
            tag, chunk = self.chunkDict[0][0]
            self.isDeleted = tag.isDeleted
            
        
        return
            
            
    def writeVersion(self, versionNum) :
        header, hChunk = self.versions[versionNum][0]
        
        numChunks = math.ceil( float(hChunk.fsize) / hChunk.length)
        
        remaining = hChunk.fsize;
    
        with open(hChunk.name, "wb") as f:
                    
            for index in range(int(numChunks)):
                cTag, cChunk = self.versions[versionNum][index+1]
                    
                bytes = cChunk.GetBytes();
                    
                if remaining >= len(bytes) :
                    f.write(bytes)
                    remaining -= len(bytes)
                else :
                    f.write(bytes[0:remaining])
                    remaining = 0
    
        pass
            
    def write(self) :
    
        tag, chunk = self.chunkDict[0][0];
    
        numChunks = math.ceil( float(chunk.fsize) / chunk.length )
        
        remaining = chunk.fsize;
            
        with open('out.png', "wb") as f:
                    
            for index in range(int(numChunks)):
                cTag, cChunk = chunkDict[index+1][0]
                    
                bytes = cChunk.GetBytes();
                    
                if remaining >= len(bytes) :
                    f.write(bytes)
                    remaining -= len(bytes)
                else :
                    f.write(bytes[0:remaining])
                    remaining = 0
                        
        
            
        
        