#!/usr/bin/env python
#
# Dump an archive of a master node.  This Python file is self-contained, so
# you can copy it onto a machine without having to pull the whole git
# repository.
#
# Usage: dump_archive.py
# Creates an archive file called djangy_dump_YYYY-MM-DD_hh-mm-ss.fff.tar.gz
# in the current directory.
#
import os, os.path, re, shutil, subprocess, sys, tempfile, time

# This is the MySQL root password on the old master node whose state you're
# archiving, which might not be the same as the latest root password.
_MYSQL_ROOT_PASSWORD = 'password goes here'

def main():
    return dump_archive(os.path.abspath('.'))

################################################################################
# Decorators copied from core.py so that dump_archive.py is self-contained.

# Decorator to print out a status message boxing the output of a function. 
# Useful for long running functions or those that print output.
def print_when_used(func):
    def _line(char):
        return ''.join([char for i in range(0, 80/len(char))])
    def print_when_used(*args):
        print _line('=')
        print func.__name__ + str(args)
        print _line('- ')
        try:
            return func(*args)
        finally:
            print _line('-')
    return print_when_used

# Decorator to run a function in a temporary directory, and then delete the
# temporary directory when the function returns (or throws an exception).
def in_tempdir(func):
    def in_tempdir(*args, **kwargs):
        tempdir = tempfile.mkdtemp(prefix='djangy_install_')
        assert tempdir.startswith('/tmp/djangy_install_')
        old_dir = os.getcwd()
        try:
            os.chdir(tempdir)
            return func(*args, **kwargs)
        finally:
            os.chdir(old_dir)
            shutil.rmtree(tempdir)
    return in_tempdir

################################################################################

# Creates a timestamp of the form:
#   YYYY-MM-DD_hh-mm-ss.fff
def make_text_timestamp(numeric_time=None):
    if numeric_time == None:
        numeric_time = time.time()
    time_struct = time.gmtime(numeric_time)
    fractional_seconds = int((numeric_time % 1) * 1000)
    return '%04i-%02i-%02i_%02i-%02i-%02i.%03i' \
        % (time_struct.tm_year, time_struct.tm_mon, time_struct.tm_mday, \
           time_struct.tm_hour, time_struct.tm_min, time_struct.tm_sec, \
           fractional_seconds)

@in_tempdir
def dump_archive(dest_dir_path):
    dump_name = 'djangy_dump_%s' % make_text_timestamp()
    dest_file_path = os.path.join(dest_dir_path, '%s.tar.gz' % dump_name)
    # Create contents for archive
    os.mkdir(dump_name)
    create_mysql_dump(os.path.join(dump_name, 'all-databases.mysqldump'))
    create_archive(os.path.join(dump_name, 'git-repositories.tar.gz'), '/srv/git')
    # Create archive
    create_archive(dest_file_path, dump_name)
    return dest_file_path

@print_when_used
def create_mysql_dump(mysql_dump_file_path):
    # The MySQL dump could be pretty big, so it's easier to just use the
    # shell to redirect output.
    assert 0 == subprocess.call(['mysqldump -u root -p%s --all-databases > %s' % (_MYSQL_ROOT_PASSWORD, mysql_dump_file_path)], shell=True)
    print 'Done.'

@print_when_used
def create_archive(dest_tar_file_path, src_path):
    assert 0 == subprocess.call(['tar', '-czf', dest_tar_file_path, src_path])
    print 'Done.'


if __name__ == '__main__':
    main()
