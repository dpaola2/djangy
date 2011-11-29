import os, os.path
from core import *

_NGINX_VERSION = 'nginx-0.8.52'
_NGINX_INSTALL_PATH = os.path.join('/srv/proxycache_manager', _NGINX_VERSION)
_NGINX_BIN_PATH = '/srv/proxycache_manager/nginx/sbin/nginx'

def require_no_nginx():
    if os.path.isfile(_NGINX_BIN_PATH):
        run_ignore_failure(_NGINX_BIN_PATH, '-s', 'quit')

def require_nginx():
    require_group('proxycache')
    require_user('proxycache', groupname='proxycache', homedir='/srv/proxycache_manager', shell='/bin/sh', description='proxy cache manager')
    require_directory('/srv/proxycache_manager', 'proxycache', 'proxycache', 0700)
    require_install_nginx()
    require_configure_nginx()
    start_nginx()

def require_install_nginx():
    if not os.path.exists(_NGINX_INSTALL_PATH):
        _install_nginx()

@in_tempdir
@print_when_used
def _install_nginx():
    # Cache this file locally?
    run('wget', 'http://sysoev.ru/nginx/%s.tar.gz' % _NGINX_VERSION)
    run('tar', '-xzf', '%s.tar.gz' % _NGINX_VERSION)
    os.chdir(_NGINX_VERSION)
    run('./configure', '--prefix=%s' % _NGINX_INSTALL_PATH)
    run('make')
    require_directory(_NGINX_INSTALL_PATH, 'proxycache', 'proxycache', 0700)
    run('make', 'install')

def require_configure_nginx():
    require_remove(os.path.join(_NGINX_INSTALL_PATH, 'conf/nginx.conf.default'))
    require_directory(_NGINX_INSTALL_PATH, 'proxycache', 'proxycache', 0700)
    require_directory(os.path.join(_NGINX_INSTALL_PATH, 'conf/applications'), 'proxycache', 'proxycache', 0700)
    require_directory(os.path.join(_NGINX_INSTALL_PATH, 'cache'), 'proxycache', 'proxycache', 0700)
    require_file(os.path.join(_NGINX_INSTALL_PATH, 'conf/nginx.conf'), 'proxycache', 'proxycache', 0600, contents=read_file('conf/proxycache_manager/nginx.conf'), overwrite=True)
    require_link('/srv/proxycache_manager/nginx', _NGINX_INSTALL_PATH)
    require_recursive(_NGINX_INSTALL_PATH, username='proxycache', groupname='proxycache')
    require_file('/etc/rc.local', 'root', 'root', 0700, contents=read_file('conf/rc.local'), overwrite=True)
    require_file('/srv/proxycache_manager/502.html', 'proxycache', 'proxycache', 0400, contents=read_file('conf/proxycache_manager/502.html'), overwrite=True)

@print_when_used
def start_nginx():
    print "Stopping old nginx..."
    run_ignore_failure(_NGINX_BIN_PATH, '-s', 'quit')
    print "Starting new nginx..."
    run(_NGINX_BIN_PATH)


#    chmod -R g-rwx,o-rwx $PROXYCACHE_MANAGER_PATH
