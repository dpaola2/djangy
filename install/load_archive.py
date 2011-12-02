#!/usr/bin/env python
#
# Install a Djangy system dump created by dump_archive.py
# Useful for deploying a new clone of a Djangy server.
#
# Author: Sameer Sundresh <sameer@sundresh.org>
#

import os, os.path, re, subprocess, sys, time
from core import *
import config

def main():
    if len(sys.argv) != 2:
        print 'Usage: load_archive.py djangy_dump_YYYY-MM-DD_hh-mm-ss.fff.tar.gz'
        sys.exit(1)
    src_file_path = os.path.abspath(sys.argv[1])
    assert os.path.isfile(src_file_path)
    assert not os.path.exists('/srv/git')
    load_archive(src_file_path)

@in_tempdir
def load_archive(src_file_path):
    run('tar', '-xzf', src_file_path)
    dir_contents = os.listdir('.')
    assert len(dir_contents) == 1 and os.path.isdir(dir_contents[0])
    os.chdir(dir_contents[0])
    load_mysql_dump(os.path.abspath('all-databases.mysqldump'))
    extract_git_repositories(os.path.abspath('git-repositories.tar.gz'))

@print_when_used
def load_mysql_dump(mysql_dump_file_path):
    run_with_stdin( ['mysql', '-u', 'root', '-p%s'      % config.DB_ROOT_PASSWORD],           stdin='DROP DATABASE djangy;')
    subprocess.call(['mysql    -u    root    -p%s < %s' % (config.DB_ROOT_PASSWORD, mysql_dump_file_path)], shell=True)
    run_with_stdin( ['mysql', '-u', 'root', '-p%s'      % config.DB_ROOT_PASSWORD, 'djangy'], stdin='DELETE FROM process; FLUSH PRIVILEGES;')
    print 'Done.'

@print_when_used
def extract_git_repositories(git_repositories_tar_file_path):
    git_repositories_tar_file_path = os.path.abspath(git_repositories_tar_file_path)
    os.chdir('/')
    run('tar', '-xzf', git_repositories_tar_file_path, 'srv/git')
    print 'Done.'

if __name__ == '__main__':
    main()
