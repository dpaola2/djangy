#!/usr/bin/env python
#
# Remove a given application from the nginx proxy cache
# Example usage:
#   remove_application.py application_name testapp
#

import os
from shared import *
from mako.template import Template
from mako.lookup import TemplateLookup

def main():
    try:
        check_trusted_uid(sys.argv[0])
        kwargs = check_and_return_keyword_args(sys.argv, ['application_name'])

        delete_application(**kwargs)
    except:
        log_last_exception()

def delete_application(application_name):
    print 'Removing nginx configuration file for %s...' % application_name
    nginx_conf_path = os.path.join(NGINX_APP_CONF_DIR, '%s.conf' % application_name)

    # Remove the old config file
    try:
        os.remove(nginx_conf_path)
    except:
        pass

    # Remove the cache
    print 'Removing nginx cache for %s...' % application_name
    clear_cache.clear_cache(application_name)

    reload_nginx_conf()

if __name__ == '__main__':
    main()
