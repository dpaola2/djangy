#!/usr/bin/env python

from ConfigParser import RawConfigParser
from shared import *

def main():
    check_trusted_uid(sys.argv[0])
    kwargs = check_and_return_keyword_args(sys.argv, ['application_name'])
    retrieve_logs(**kwargs)

def retrieve_logs(application_name):
    stdout_contents_dict = call_worker_managers_retrieve_logs(application_name)
    try:
        print stdout_contents_dict.values()[0]
    except:
        pass

if __name__ == '__main__':
    main()
