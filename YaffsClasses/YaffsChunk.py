import struct

class YaffsChunk:
    
    def __init__(self, imageFilePath, startOffset, chunkLength):
        self.imageFile = imageFilePath
        self.offset = startOffset
        self.length = chunkLength
        
        
    def GetBytes(self) :
        with open(self.imageFile, "rb") as f:
            f.seek(self.offset)
            
            chunkBytes = f.read(self.length)
            
            return chunkBytes;
            
    def ParseHeaderChunk(self) :
        chunk = self.GetBytes()
        
        (self.objType, self.parentId, self.ffValue, self.name, self.fmode, self.uid, self.gid, self.atime, self.mtime, self.ctime, self.fsize, padding) = struct.unpack("<IIH255s3xIIIIIII216x%ds"%(len(chunk)-0x200), chunk);
        
        #let's remove those extra null bytes that we read in.
        self.name = self.name.strip('\x00')
        
        