#! /usr/bin/env python

import S3, sys, config, os
from core import read_file

def upload(filename):
    conn = S3.AWSAuthConnection(config.S3_ACCESS_KEY, config.S3_SECRET)
    result = conn.check_bucket_exists(config.S3_BUCKET)
    if result.status != 200:
        result = conn.create_located_bucket(config.S3_BUCKET, S3.Location.DEFAULT)

    assert 200 == conn.put(config.S3_BUCKET, os.path.basename(filename), read_file(filename)).http_response.status

    print "File %s successfully backed up to S3 (with same filename)." % filename

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: s3put.py <archive>"
        sys.exit(1)
    filename = sys.argv[1]
    upload(filename)
