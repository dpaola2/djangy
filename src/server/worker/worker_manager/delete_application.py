#!/usr/bin/env python
#
# Stops and removes application from LocalApplication table but doesn't
# remove bundles or logs.
#

from shared import *

def main():
    try:
        check_trusted_uid(program_name = sys.argv[0])
        kwargs = check_and_return_keyword_args(sys.argv, ['application_name'])

        application_name = kwargs['application_name']

        delete_application(application_name)
    except:
        log_last_exception()

@lock_application
def delete_application(application_name):
    stop_application(application_name)
    application_info = LocalApplication.objects.get(application_name = application_name)
    application_info.delete()

if __name__ == '__main__':
    main()
