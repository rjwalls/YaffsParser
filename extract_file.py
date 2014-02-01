__author__ = 'wallsr'


import sys
import Scanner
from YaffsClasses.YaffsOobTag import YaffsOobTag

image = sys.argv[1]
filename = sys.argv[2].strip()

print 'Looking for ' + filename

chunk_size = 2048
oob_size = 64
oob_tag_offset = 29

headers = Scanner.get_headers(image, chunk_size, oob_size)

headers = [h for h in headers if h.name == filename]

print 'Found %d header chunks' % len(headers)

oob_bytes = Scanner.get_oob_bytes(image, headers, oob_size)

oobs = [YaffsOobTag(oob, oob_tag_offset)
        for oob in oob_bytes]

id_set = set([o.object_id for o in oobs])

print 'Found object ids:', id_set




