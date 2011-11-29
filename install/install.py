#!/usr/bin/env python
import os, sys
import config
from core import *
from apache import *
from application_uids_gids import *
from git_serve import *
from nginx import *
from database import *

def equals_single_arg(arg):
    return arg.split('=', 1)[1]

def equals_multiple_args(arg):
    return arg.split('=', 1)[1].split(',')

# Command-line arguments
if len(sys.argv) >= 2:
    if (sys.argv[1] == 'install' or sys.argv[1] == 'upgrade'):
        config.ACTION = sys.argv[1]
    config.MASTER_NODE     = 'master'     in sys.argv[2:]
    config.WORKER_NODE     = 'worker'     in sys.argv[2:]
    config.PROXYCACHE_NODE = 'proxycache' in sys.argv[2:]
    for arg in sys.argv[2:]:
        if arg.startswith('--master-manager-host='):
            config.MASTER_MANAGER_HOST = equals_single_arg(arg)
        if arg.startswith('--default-database-host='):
            config.DEFAULT_DATABASE_HOST = equals_single_arg(arg)
        if arg.startswith('--default-proxycache-host='):
            config.DEFAULT_PROXYCACHE_HOST = equals_single_arg(arg)
        if arg.startswith('--to-south'):
            config.TO_SOUTH = True
        if arg.startswith('--workerhosts='):
            if config.ACTION != 'install':
                print '"--workerhosts=" argument is only valid for action "install"'
                sys.exit(1)
            config.WORKERHOSTS.extend(equals_multiple_args(arg))
        if arg.startswith('--production'):
            config.PRODUCTION = True
            config.DEVPAYMENTS_API_KEY = config.DEVPAYMENTS_PRODUCTION
if not config.ACTION or not config.MASTER_MANAGER_HOST or not config.DEFAULT_DATABASE_HOST or not config.DEFAULT_PROXYCACHE_HOST:
    print 'Usage: sudo install.py { install | upgrade } [master] [worker] [proxycache] --master-manager-host=<mh> --default-database-host=<dbh> --default-proxycache-host=<pch> [--workerhosts=<wh1>,<wh2>,...] [--production] [--to-south]'
    sys.exit(1)

# Find the source code
_DJANGY_CODE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Automate setup of mysql
run_with_stdin(['debconf-set-selections'], stdin='mysql-server-5.0 mysql-server/root_password password %s\n' % config.DB_ROOT_PASSWORD)
run_with_stdin(['debconf-set-selections'], stdin='mysql-server-5.0 mysql-server/root_password_again password %s\n' % config.DB_ROOT_PASSWORD)

require_ubuntu_packages('apache2', 'apache2-dev', 'build-essential', 'bzr',
    'cron', 'gcc', 'git-core', 'joe', 'libapache2-mod-wsgi',
    'libfreetype6-dev', 'libjpeg-dev', 'libyaml-dev', 'mercurial',
    'mysql-server', 'openssh-server', 'python', 'python-dev',
    'python-mysqldb', 'python-setuptools', 'python-sqlite', 'python-xapian',
    'python-yaml', 'rsync', 'sqlite3', 'subversion', 'vim')

require_python_packages('Django==1.2.1', 'Fabric==0.9.1', 'Mako==0.3.4',
    'PIL==1.1.7', 'South==0.7.2', 'django-sentry==1.0.9',
    'gunicorn==0.11.1', 'simplejson==2.1.1', 'virtualenv==1.4.9')

require_user('root', uid=0, gid=0, homedir='/root', create=False)
require_directory('/root', 'root', 'root', 0700)
require_directory('/root/.ssh', 'root', 'root', 0700)
require_file('/root/.ssh/id_rsa',          'root', 'root', 0600, contents=read_file('conf/ssh_keys/root_key'),     overwrite=True)
require_file('/root/.ssh/id_rsa.pub',      'root', 'root', 0600, contents=read_file('conf/ssh_keys/root_key.pub'), overwrite=True)
require_file('/root/.ssh/authorized_keys', 'root', 'root', 0600, contents=read_file('conf/ssh_keys/root_key.pub'), overwrite=True)
require_file('/root/.ssh/config',          'root', 'root', 0600, contents=read_file('conf/ssh_keys/ssh_config'),   overwrite=True)
if config.MASTER_NODE and config.PRODUCTION:
    require_file('/etc/ssh/ssh_host_dsa_key',     'root', 'root', 0600, contents=read_file('conf/etc_ssh/ssh_host_dsa_key'),     overwrite=True)
    require_file('/etc/ssh/ssh_host_dsa_key.pub', 'root', 'root', 0644, contents=read_file('conf/etc_ssh/ssh_host_dsa_key.pub'), overwrite=True)
    require_file('/etc/ssh/ssh_host_rsa_key',     'root', 'root', 0600, contents=read_file('conf/etc_ssh/ssh_host_rsa_key'),     overwrite=True)
    require_file('/etc/ssh/ssh_host_rsa_key.pub', 'root', 'root', 0644, contents=read_file('conf/etc_ssh/ssh_host_rsa_key.pub'), overwrite=True)
    require_file('/etc/crontab',                  'root', 'root', 0644, contents=read_file('conf/crontab'),                      overwrite=True)
require_group('www-data', create=False)
require_user('www-data', groupname='www-data', homedir='/var/www', create=False)

require_group('git')
require_user('git',        groupname='git',        homedir='/srv/git',                shell='/bin/sh', description='git version control')
require_group('proxycache')
require_user('proxycache', groupname='proxycache', homedir='/srv/proxycache_manager', shell='/bin/sh', description='proxy cache manager')

require_group('shell')
require_user('shell', groupname='shell', homedir='/srv/shell', shell='/bin/sh', description='shell account')
require_directory('/srv/shell',      'shell', 'shell', 0700)
require_directory('/srv/shell/.ssh', 'shell', 'shell', 0700)

require_group('djangy', member_usernames=['www-data', 'git', 'shell'])

if config.PRODUCTION:
    require_directory('/proc', 'root', 'admin', 0550, create=False)

require_directory('/srv',         'root', 'root', 0711)
require_directory('/srv/bundles', 'root', 'root', 0711)
if config.ACTION == 'install':
    assert not os.path.exists('/srv/djangy')
else:
    assert config.ACTION == 'upgrade'
require_remove('/srv/djangy')
require_directory('/srv/djangy',                         'root',       'djangy',     0710, initial_contents_path=_DJANGY_CODE_PATH)
require_file     ('/srv/djangy/src/server/shared/djangy_server_shared/installer_configured_constants.py', 'root', 'djangy', 0644, overwrite=True,
    contents = (('DEFAULT_DATABASE_HOST   = \'%s\'\n' % config.DEFAULT_DATABASE_HOST) +
                ('DEFAULT_PROXYCACHE_HOST = \'%s\'\n' % config.DEFAULT_PROXYCACHE_HOST) +
                ('MASTER_MANAGER_HOST     = \'%s\'\n' % config.MASTER_MANAGER_HOST) + 
                ('DEVPAYMENTS_API_KEY     = \'%s\'\n' % config.DEVPAYMENTS_API_KEY)))
if config.MASTER_NODE:
    require_directory('/srv/git',                        'git',        'git',        0710)
    require_directory('/srv/git/.ssh',                   'git',        'git',        0700)
    require_directory('/srv/git/repositories',           'git',        'git',        0710)

require_directory('/srv/logs',                           'root',       'root',       0711)
if config.MASTER_NODE:
    require_directory('/srv/logs/api.djangy.com',            'root',       'www-data',   0710)
    require_file     ('/srv/logs/api.djangy.com/django.log', 'www-data',   'www-data',   0600, initial_contents='')
    require_directory('/srv/logs/djangy.com',                'root',       'www-data',   0710)
    require_file     ('/srv/logs/djangy.com/django.log',     'www-data',   'www-data',   0600, initial_contents='')
    require_directory('/srv/logs/000-defaults',              'root',       'www-data',   0710)
    require_file     ('/srv/logs/000-defaults/access.log',   'www-data',   'www-data',   0600, initial_contents='')
    require_file     ('/srv/logs/000-defaults/error.log',    'www-data',   'www-data',   0600, initial_contents='')
    require_file     ('/srv/logs/master_api.log',            'www-data',   'www-data',   0600, initial_contents='')

if config.PROXYCACHE_NODE:
    if config.ACTION == 'install':
        assert not os.path.exists('/srv/proxycache_manager')
    require_directory('/srv/proxycache_manager',             'proxycache', 'proxycache', 0700)
require_directory('/srv/scratch',                        'root',       'root',       0700)
if config.WORKER_NODE:
    if config.ACTION == 'install':
        assert not os.path.exists('/srv/worker_manager')
    require_directory('/srv/worker_manager',                 'root',       'root',       0700)

@print_when_used
def require_make_djangy():
    with cd('/srv/djangy'):
        run('make', 'clean')
        run('make')

require_application_uids_gids()
require_make_djangy()
require_database()

if config.MASTER_NODE:
    require_git_serve()
else:
    require_no_git_serve()

if config.MASTER_NODE:
    require_apache()
else:
    require_no_apache()

if config.PROXYCACHE_NODE:
    require_nginx()
else:
    require_no_nginx()

# Create an upgrade script in /srv/upgrade
require_file('/srv/upgrade', 'root', 'root', 0700, contents="""#!/bin/bash
./install.py upgrade %(master)s %(worker)s %(proxycache)s \
--master-manager-host=%(master-manager-host)s \
--default-database-host=%(default-database-host)s \
--default-proxycache-host=%(default-proxycache-host)s \
%(production)s\
""" % {
    'master'                 : 'master'     if config.MASTER_NODE     else '',
    'worker'                 : 'worker'     if config.WORKER_NODE     else '',
    'proxycache'             : 'proxycache' if config.PROXYCACHE_NODE else '',
    'master-manager-host'    : config.MASTER_MANAGER_HOST,
    'default-database-host'  : config.DEFAULT_DATABASE_HOST,
    'default-proxycache-host': config.DEFAULT_PROXYCACHE_HOST,
    'production'             : 'production' if config.PRODUCTION      else ''
}, overwrite=True)

# Rebuild bundles and deploy applications...
