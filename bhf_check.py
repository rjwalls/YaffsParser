__author__ = 'wallsr'

import hashlib
import os
import sys

# The last image is the one to be filtered,the rest are
#simply to be added to the hash library
images = sys.argv[1:]

filter_image = images.pop()


hash_library = set()

for image in images:
    with open(image, 'rb') as f:
        while f.read(1) != '':
            f.seek(-1, True)
            block = f.read(1024)
            hasher = hashlib.sha1()
            hasher.update(block)
            hash_library.add(hasher.digest())

num_blocks = os.path.getsize(filter_image) / 1024
print 'Number of blocks: %d' % num_blocks

#The set of hashes on the filter phone
hash_set = set()

with open(filter_image, 'rb') as f:
    while f.read(1) != '':
        f.seek(-1, True)
        block = f.read(1024)
        hasher = hashlib.sha1()
        hasher.update(block)
        hash = hasher.digest()
        hash_set.add(hash)

#The unique hash on the filter phone, but not in the library
unique_hashes = hash_set - hash_library

print 'Number of unique hashes: %d' % len(unique_hashes)

print 'Filtered %.2f percent' % (float(num_blocks - len(unique_hashes)) * 100 / num_blocks)