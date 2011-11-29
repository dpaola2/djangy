#!/usr/bin/env python
#
# Utility script to remove old, unused bundles from a master_manager host.
#

import os, shutil
from management_database import *

BUNDLES_ROOT = '/srv/bundles';

def main():
    current_bundle_names = set([x.name + '-' + x.bundle_version for x in Application.objects.filter(deleted=None)])
    for bundle_name in os.listdir(BUNDLES_ROOT):
        if bundle_name not in current_bundle_names:
            print 'Removing %s ...' % bundle_name
            shutil.rmtree(os.path.join(BUNDLES_ROOT, bundle_name))

if __name__ == '__main__':
    main()
