import grp, os, pwd
import installer_configured_constants

# Users and groups
# DJANGY_USERNAME         = 'djangy'
# TODO: we should create a 'djangy' user which has ssh access to
# worker_manager and proxycache_manager hosts and can only run
# the worker_manager and proxycache_manager methods, but can't
# do just arbitrary things on its own.  (Right now we ssh as root.)
DJANGY_GROUPNAME        = 'djangy'
GIT_USERNAME            = 'git'
GIT_GROUPNAME           = 'git'
PROXYCACHE_USERNAME     = 'proxycache'
PROXYCACHE_GROUPNAME    = 'proxycache'
SHELL_USERNAME          = 'shell'
SHELL_GROUPNAME         = 'shell'
WWW_DATA_USERNAME       = 'www-data'
WWW_DATA_GROUPNAME      = 'www-data'

# UIDs and GIDs -- computed from users and groups
# DJANGY_UID              = pwd.getpwnam(DJANGY_USERNAME).pw_uid
DJANGY_GID              = grp.getgrnam(DJANGY_GROUPNAME).gr_gid
GIT_UID                 = pwd.getpwnam(GIT_USERNAME).pw_uid
GIT_GID                 = grp.getgrnam(GIT_GROUPNAME).gr_gid
PROXYCACHE_UID          = pwd.getpwnam(PROXYCACHE_USERNAME ).pw_uid
PROXYCACHE_GID          = grp.getgrnam(PROXYCACHE_GROUPNAME).gr_gid
SHELL_UID               = pwd.getpwnam(SHELL_USERNAME ).pw_uid
SHELL_GID               = grp.getgrnam(SHELL_GROUPNAME).gr_gid
ROOT_UID                = 0
ROOT_GID                = 0
WWW_DATA_UID            = pwd.getpwnam(WWW_DATA_USERNAME).pw_uid
WWW_DATA_GID            = grp.getgrnam(WWW_DATA_GROUPNAME).gr_gid

# Other shared constants
INSTALL_ROOT_DIR        = '/srv'
BUNDLES_DIR             = os.path.join(INSTALL_ROOT_DIR, 'bundles')
DJANGY_DIR              = os.path.join(INSTALL_ROOT_DIR, 'djangy')
LOGS_DIR                = os.path.join(INSTALL_ROOT_DIR, 'logs')
PYTHON_BIN_PATH         = os.path.join(DJANGY_DIR, 'run/python-virtual/bin/python')
BUNDLE_VERSION_PREFIX   = 'v1g'

#GITOSIS_ADMIN_DIR       = os.path.join(INSTALL_ROOT_DIR, 'scratch')
#GITOSIS_ADMIN_REPO      = 'git@%s:gitosis-admin.git' % installer_configured_constants.MASTER_MANAGER_HOST

DATABASE_ROOT_USER      = 'root'
DATABASE_ROOT_PASSWORD  = 'password goes here'

DEFAULT_DATABASE_HOST   = installer_configured_constants.DEFAULT_DATABASE_HOST # XXX
DEFAULT_PROXYCACHE_HOST = installer_configured_constants.DEFAULT_PROXYCACHE_HOST # XXX

TRUSTED_UIDS            = []

# Master constants
MASTER_TRUSTED_UIDS     = [ROOT_UID, GIT_UID, WWW_DATA_UID]

MASTER_SETUID_DIR       = os.path.join(DJANGY_DIR, 'run/master_manager/setuid')
MASTER_MANAGER_SRC_DIR  = os.path.join(DJANGY_DIR, 'src/server/master/master_manager')
GIT_SSH_DIR             = os.path.join(INSTALL_ROOT_DIR, 'git/.ssh')
SHELL_SSH_DIR           = os.path.join(INSTALL_ROOT_DIR, 'shell/.ssh')
AUTHORIZED_KEYS_MODE    = 0644
REPOS_DIR               = os.path.join(INSTALL_ROOT_DIR, 'git/repositories')
MASTER_MANAGER_HOST     = installer_configured_constants.MASTER_MANAGER_HOST # XXX - used to define BUNDLES_SRC_HOST for worker_manager below
DEVPAYMENTS_API_KEY     = installer_configured_constants.DEVPAYMENTS_API_KEY

GIT_SERVE_PATH          = '/srv/djangy/run/python-virtual/bin/git_serve.py'
SHELL_SERVE_PATH        = '/srv/djangy/run/master_manager/setuid/run_shell_serve'

# XXX deprecate chargify constants
CHARGIFY_SUBDOMAIN = 'subdomain goes here'
CHARGIFY_API_KEY = 'password goes here'
CHARGIFY_PRODUCT_ID = 14215
CHARGIFY_COMPONENTS = [
    ('worker_processes',1537)
]

# List of specific names applications can't have
RESERVED_APPLICATION_NAMES = [ 'djangy', 'www', 'www-s', 'https', 'ssl', 'secure', 'api', 'mail', 'localhost', 'web' ]

# blocked remote manage.py commands
BLOCKED_COMMANDS = [
    'runserver',
    'dbshell',
    'test',
    'testserver',
    'runfcgi',
    'changepassword',
    'compilemessages',
    'makemessages',
    'schemamigration',
    'datamigration'
]

# Worker constants
WORKER_TRUSTED_UIDS     = [ROOT_UID]

WORKER_SETUID_DIR       = os.path.join(DJANGY_DIR, 'run/worker_manager/setuid')
WORKER_MANAGER_SRC_DIR  = os.path.join(DJANGY_DIR, 'src/server/worker/worker_manager')
WORKER_MANAGER_VAR_DIR  = os.path.join(INSTALL_ROOT_DIR, 'worker_manager')
WORKER_TEMPLATE_DIR     = os.path.join(WORKER_MANAGER_SRC_DIR, 'templates')

BUNDLES_SRC_HOST        = MASTER_MANAGER_HOST
BUNDLES_SRC_DIR         = BUNDLES_DIR
BUNDLES_DEST_DIR        = BUNDLES_DIR

APACHE_SITES_AVAILABLE  = '/etc/apache2/sites-available'

LOGS                    = ['django.log', 'error.log', 'access.log', 'celery.log']

MAX_PROCS_PER_WORKER    = 100
WORKER_PORT_LOWER       = 20000
WORKER_PORT_UPPER       = 40000
DEFAULT_WORKER_PORT     = 20000

# Proxycache constants
PROXYCACHE_TRUSTED_UIDS = [ROOT_UID]

PROXYCACHE_SETUID_DIR   = os.path.join(DJANGY_DIR, 'run/proxycache_manager/setuid')
PROXYCACHE_TEMPLATE_DIR = os.path.join(DJANGY_DIR, 'src/server/proxycache/proxycache_manager/templates')

NGINX_DIR               = os.path.join(INSTALL_ROOT_DIR, 'proxycache_manager/nginx')
NGINX_BIN_PATH          = os.path.join(NGINX_DIR, 'sbin/nginx')
NGINX_APP_CONF_DIR      = os.path.join(NGINX_DIR, 'conf/applications')
NGINX_CACHE_DIR         = os.path.join(NGINX_DIR, 'cache')
