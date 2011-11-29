import os.path
import config
from core import *

_PYTHON = '/srv/djangy/run/python-virtual/bin/python'

def require_database():
    if config.MASTER_NODE:
        _configure_mysql_server()
    else:
        run_ignore_failure('service', 'mysql', 'stop')
    if config.MASTER_NODE:
        _create_databases(config.MASTER_DATABASES)
    _syncdb_and_migrate()
    if config.ACTION == 'install' and config.MASTER_NODE:
        _load_admins()
        _load_docs()
    if config.MASTER_NODE:
        _load_chargables()
        _load_subscription_types()
        if len(config.WORKERHOSTS) > 0:
            _load_workerhosts()

@print_when_used
def _configure_mysql_server():
    try:
        require_file('/etc/mysql/my.cnf', 'root', 'root', 0644, contents=read_file('conf/mysql/my.cnf.new'))
    except:
        require_file('/etc/mysql/my.cnf', 'root', 'root', 0644, contents=read_file('conf/mysql/my.cnf.orig'))
        require_file('/etc/mysql/my.cnf', 'root', 'root', 0644, contents=read_file('conf/mysql/my.cnf.new'), overwrite=True)
        run('service', 'mysql', 'restart')

@print_when_used
def _create_databases(databases):
    for user, password, db in databases:
        cmd1 = 'CREATE DATABASE IF NOT EXISTS %s;' % db
        cmd2 = 'GRANT ALL ON %s.* TO %s@\'%%\' IDENTIFIED BY \'%s\';' % (db, user, password)
        run_with_stdin(['mysql', '-u', 'root', '-p%s' % config.DB_ROOT_PASSWORD], stdin=cmd1+cmd2)

def _syncdb_and_migrate():
    if config.WORKER_NODE:
        _syncdb('/srv/djangy/src/server/worker/worker_manager/orm')
        if config.TO_SOUTH:
            _migrate('/srv/djangy/src/server/worker/worker_manager/orm', 'orm', '0001', '--fake')
        _migrate('/srv/djangy/src/server/worker/worker_manager/orm', 'orm')

    if config.MASTER_NODE:
        _syncdb('/srv/djangy/src/server/master/web_ui/application/web_ui')
        _syncdb('/srv/djangy/src/server/master/web_api/application/web_api')
        _syncdb('/srv/djangy/src/server/master/management_database/management_database')

    if config.MASTER_NODE:
        _migrate('/srv/djangy/src/server/master/management_database/management_database', 'management_database')
        _migrate('/srv/djangy/src/server/master/web_ui/application/web_ui',               'main')
        _migrate('/srv/djangy/src/server/master/web_ui/application/web_ui',               'docs')
        _migrate('/srv/djangy/src/server/master/web_ui/application/web_ui',               'management_database', 'zero')

@print_when_used
def _syncdb(dir_path):
    with cd(dir_path):
        run(_PYTHON, 'manage.py', 'syncdb', '--noinput')
    print 'Done.'

@print_when_used
def _migrate(dir_path, application_name, *args):
    with cd(dir_path):
        command = [_PYTHON, 'manage.py', 'migrate', application_name] + list(args)
        run(*command)
    print 'Done.'

@print_when_used
def _load_admins():
    with cd('/srv/djangy/src/server/master/management_database/management_database'):
        run(_PYTHON, 'manage.py', 'loaddata', 'loadadmins.yaml')
    print 'Done.'

@print_when_used
def _load_chargables():
    with cd('/srv/djangy/src/server/master/management_database/management_database'):
        run(_PYTHON, 'manage.py', 'loaddata', 'loadchargables.yaml')
    print 'Done.'

@print_when_used
def _load_subscription_types():
    with cd('/srv/djangy/src/server/master/management_database/management_database'):
        run(_PYTHON, 'manage.py', 'loaddata', 'loadsubscriptiontypes.yaml')
    print 'Done.'

@print_when_used
def _load_docs():
    with cd('/srv/djangy/src/server/master/web_ui/application/web_ui'):
        run(_PYTHON, 'manage.py', 'loaddata', 'docs/wiki_docs.yaml')
    print 'Done.'

@in_tempdir
@print_when_used
def _load_workerhosts():
    file = open('load_workerhosts.yaml', 'w')
    pk = 1
    for workerhost in config.WORKERHOSTS:
        file.write('- model: management_database.WorkerHost\n')
        file.write('  pk: %i\n' % pk)
        file.write('  fields:\n')
        file.write('    host: %s\n' % workerhost)
        file.write('    max_procs: 100\n\n')
        pk = pk+1
    file.close()
    yaml_path = os.path.abspath('load_workerhosts.yaml')
    with cd('/srv/djangy/src/server/master/management_database/management_database'):
        run(_PYTHON, 'manage.py', 'loaddata', yaml_path)
    print 'Done.'
