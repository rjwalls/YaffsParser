__author__ = 'wallsr'


"""
This is a quick script for trying to grab the start of the contacts2.db
file by making some assumptions about the format of the oob.'

The current numbers are hardcoded for the Via Forensics Droid Eris image.
"""

import Scanner, YaffsParser
import sys

# I found this manually
object_id = '\xb4\x02\x00\x00'

chunk_id = '\x01\x00\x00\00'

image = sys.argv[1]

print image

chunk_pairs = YaffsParser.extract_chunks(image, 2048, 64)

f = open(image, 'rb')

for (chunk, oob_offset) in chunk_pairs:
    f.seek(oob_offset+34)
    if object_id == f.read(4) and chunk_id == f.read(4):
        print 'Found chunk 1'
        print chunk.get_bytes(3)


f.close()