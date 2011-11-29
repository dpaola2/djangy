#!/usr/bin/env python

from shared import *

def main():
    check_trusted_uid(sys.argv[0])
    kwargs = check_and_return_keyword_args(sys.argv, ['email', 'ssh_public_key'])
    user = User.get_by_email(kwargs['email'])
    add_ssh_public_key(user, kwargs['ssh_public_key'])

if __name__ == '__main__':
    main()
