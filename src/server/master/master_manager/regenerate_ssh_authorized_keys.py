#!/usr/bin/env python

from shared import *

def main():
    check_trusted_uid(sys.argv[0])
    kwargs = check_and_return_keyword_args(sys.argv, [])
    regenerate_ssh_authorized_keys()

if __name__ == '__main__':
    main()
