#!/usr/bin/env python
#
# Utility script to remove old, unused bundles from a worker_manager host.
#

import os, shutil
from shared import *

BUNDLES_ROOT = '/srv/bundles';

def main():
    current_bundle_names = set([x.application_name + '-' + x.bundle_version for x in LocalApplication.objects.all()])
    for bundle_name in os.listdir(BUNDLES_ROOT):
        if bundle_name not in current_bundle_names:
            print 'Removing %s ...' % bundle_name
            shutil.rmtree(os.path.join(BUNDLES_ROOT, bundle_name))

if __name__ == '__main__':
    main()
