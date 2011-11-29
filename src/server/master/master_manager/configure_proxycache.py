#!/usr/bin/env python
#
# python configure_proxycache.py application_name <x>
#

from shared import *
from management_database.models import Application, VirtualHost

def main():
    check_trusted_uid(sys.argv[0])
    kwargs = check_and_return_keyword_args(sys.argv, ['application_name'])
    try:
        call_proxycache_managers_configure(kwargs['application_name'])
    except:
        log_last_exception()
        print 'Configuring proxycache for application "%s" failed.' % kwargs['application_name']
        sys.exit(1)

if __name__ == '__main__':
    main()
