#! /usr/bin/env python
#
# Perform a backup of the Djangy system state.
#
# Author: Dave Paola <dpaola2@gmail.com>
#

import subprocess, dump_archive, os
from s3put import *

# Makes a dump of the master node and uploads it to S3

def main():
    print "Dumping archive...",
    filename = dump_archive.main()
    print "Done."
    print "Uploading to S3...",
    upload(filename)
    print "Done."
    print "Cleaning up...",
    os.remove(filename)
    print "Done."

if __name__ == '__main__':
    main()
