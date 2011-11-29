#!/usr/bin/env python
#
# Erase the nginx cache for a given application
# Example usage:
#   clear_cache.py application_name testapp
#

from shared import *
import os, os.path, shutil

def main():
    try:
        check_trusted_uid(sys.argv[0])
        kwargs = check_and_return_keyword_args(sys.argv, ['application_name'])
        clear_cache(**kwargs)
    except:
        log_last_exception()

def clear_cache(application_name):
    if is_valid_application_name(application_name):
        try:
            shutil.rmtree(os.path.join(NGINX_CACHE_DIR, application_name))
        except:
            # Cache may not yet exist
            pass

if __name__ == '__main__':
    main()
