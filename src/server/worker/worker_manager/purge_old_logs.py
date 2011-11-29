#!/usr/bin/env python
#
# Utility script to remove old, unused bundles from a worker_manager host.
#

import os, shutil
from shared import *

LOGS_ROOT = '/srv/logs';

def main():
    current_bundle_names = set([x.application_name + '-' + x.bundle_version for x in LocalApplication.objects.all()])
    for log_name in os.listdir(LOGS_ROOT):
        log_path = os.path.join(LOGS_ROOT, log_name)
        if log_name.find('-v1g') >= 0 and os.path.isdir(log_path) and log_name not in current_bundle_names:
            print 'Removing %s ...' % log_name
            shutil.rmtree(log_path)

if __name__ == '__main__':
    main()
