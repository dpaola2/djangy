#! /usr/bin/env python
#
# Download a file from the backups Amazon S3 bucket.
#
# Author: Dave Paola <dpaola2@gmail.com>
#

import S3, sys, config, os

def retrieve(filename):
    conn = S3.AWSAuthConnection(config.S3_ACCESS_KEY, config.S3_SECRET)
    assert 200 == conn.check_bucket_exists(config.S3_BUCKET).status

    result = conn.get(config.S3_BUCKET, filename)
    assert 200 == result.http_response.status

    f = open(filename, "w")
    f.write(result.object.data)
    f.close()

    print "File %s successfully retrieved (with same filename)." % filename

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: s3get.py <archive>"
        sys.exit(1)
    filename = sys.argv[1]
    retrieve(filename)
