#! /usr/bin/env python

import S3, sys, config, os

def list_files():
    conn = S3.AWSAuthConnection(config.S3_ACCESS_KEY, config.S3_SECRET)
    result = conn.check_bucket_exists(config.S3_BUCKET)
    if result.status != 200:
        result = conn.create_located_bucket(config.S3_BUCKET, S3.Location.DEFAULT)

    result = conn.list_bucket(config.S3_BUCKET)
    assert 200 == result.http_response.status
    print "Size\t\tKey"
    for entry in result.entries:
        print "%s\t%s" % (entry.size, entry.key)

if __name__ == '__main__':
    list_files()
