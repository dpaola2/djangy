#!/usr/bin/env python

from shared import *

def main():
    check_trusted_uid(sys.argv[0])
    kwargs = check_and_return_keyword_args(sys.argv, ['application_name'])
    stop(**kwargs)

@lock_application
def stop(application_name):
    return stop_application(application_name)

if __name__ == '__main__':
    main()
