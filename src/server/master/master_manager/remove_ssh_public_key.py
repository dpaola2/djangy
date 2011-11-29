#!/usr/bin/env python

from shared import *

def main():
    check_trusted_uid(sys.argv[0])
    kwargs = check_and_return_keyword_args(sys.argv, ['email', 'ssh_public_key_id'])
    user = User.get_by_email(kwargs['email'])
    user.remove_ssh_public_key(kwargs['ssh_public_key_id'])
    regenerate_ssh_authorized_keys()

if __name__ == '__main__':
    main()
