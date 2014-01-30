import struct
import string


class YaffsChunk:
    
    def __init__(self, image_file_path, offset, length):
        self.image_file = image_file_path
        self.offset = offset
        self.length = length

    def get_bytes(self, n=None):
        with open(self.image_file, "rb") as f:
            f.seek(self.offset)

            if n is not None:
                return f.read(n)

            return f.read(self.length)


class YaffsHeader(YaffsChunk):
    def __init__(self, chunk):
        YaffsChunk.__init__(self, chunk.image_file, chunk.offset, chunk.length)

        chunk_bytes = self.get_bytes()

        if chunk.length < 512:
            #If the chunk is too small then the struct.unpack will raise an exception.
            raise Exception("Chunks cannot be less than 512 bytes in length.")

        #< Little endian
        #H unsigned short
        (self.obj_type,
         self.parent_id,
         self.ff_value,
         self.name,
         self.fmode,
         self.uid,
         self.gid,
         self.atime,
         self.mtime,
         self.ctime,
         self.fsize,
         padding) = struct.unpack("<IIH255s3xIIIIIII216x%ds" % (len(chunk_bytes)-0x200), chunk_bytes)


        #let's remove those extra null bytes that we read in.
        self.name = self.name.strip('\x00')

    def is_valid(self):
        """
        This method uses heuristics to check if we think this chunk is a valid Yaffs
        header chunk.

        Heuristics: Is the object type correct? Is the name printable?
        """
        #Check if the object type is correct
        if self.obj_type != 1:
            return False

        #Check if the object name is printable
        if not all(c in string.printable for c in self.name):
            return False

        return True

