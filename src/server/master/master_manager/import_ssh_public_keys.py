#!/usr/bin/env python
#
# Utility script for importing gitosis-style SSH public keys.
#
# Must be run from a directory containing <email>.pub files or you can
# specify the path to such a directory on the command line.
#
# Will reject files containing things that don't look like SSH public keys.
#

from shared import *
import os, sys

def main():
    if len(sys.argv) > 1:
        os.chdir(sys.argv[1])
    import_ssh_public_keys()

def import_ssh_public_keys():
    for filename in os.listdir('.'):
        if filename.endswith('.pub'):
            email = filename[:-4]
            try:
                user = User.get_by_email(email)
                add_ssh_public_key(user, read_contents(filename))
                print 'Added %s' % email
            except Exception as e:
                sys.stderr.write('Skipping %s (Error: %s)\n' % (filename, str(e)))
        else:
            sys.stderr.write('Skipping %s\n' % filename)

def read_contents(filename):
    f = open(filename)
    contents = f.read()
    f.close()
    return contents

if __name__ == '__main__':
    main()
