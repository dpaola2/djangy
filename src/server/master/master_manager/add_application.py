#!/usr/bin/env python

from shared import *
import _mysql, re
from ConfigParser import RawConfigParser
from management_database.models import User, Application

def main():
    check_trusted_uid(sys.argv[0])
    kwargs = check_and_return_keyword_args(sys.argv, ['application_name', 'email', 'pubkey'])
    add_application(**kwargs)

def gen_uids_gid(app_id):
    setup_uid = (app_id * 3) + 100000
    return {
        'setup_uid': setup_uid,
        'web_uid'  : setup_uid + 1,
        'cron_uid' : setup_uid + 2,
        'app_gid'  : setup_uid
    }

def add_application(application_name, email, pubkey):
    """ Add the application specified by application_name and a corresponding database, owned by the user with the email address specified. """

    # Claim the application name
    ActiveApplicationName(name=application_name).save()

    user = User.get_by_email(email)

    # generate a secure password
    db_password = gen_password()

    # create the application row
    app = Application()
    app.name = application_name
    app.account = user
    app.db_name = application_name
    app.db_username = application_name
    app.db_password = db_password
    app.db_host = DEFAULT_DATABASE_HOST
    app.num_procs = 1
    app.save()

    # generate user and group ids to run as
    uids_gid = gen_uids_gid(app.id)
    app.setup_uid = uids_gid['setup_uid']
    app.web_uid   = uids_gid['web_uid']
    app.cron_uid  = uids_gid['cron_uid']
    app.app_gid   = uids_gid['app_gid']
    app.save()

    # enable git push
    create_git_repository(application_name)
    add_ssh_public_key(user, pubkey)

    # allocate a proxycache host for the application -- improve on this later
    ProxyCache(application = app, host = DEFAULT_PROXYCACHE_HOST).save()

    # assign virtualhost on which to listen for application
    VirtualHost(application = app, virtualhost = application_name + '.djangy.com').save()

    # allocate the application to a worker host
    # Note: this must happen after ProxyCache and VirtualHost are filled in. 
    allocate_workers(app)

    # create the database
    db = _mysql.connect(
        host = DEFAULT_DATABASE_HOST,
        user = DATABASE_ROOT_USER, 
        passwd = DATABASE_ROOT_PASSWORD)

    try: # try to remove the user if it already exists
        db.query(""" DROP USER '%s'@'%%';""" % application_name)
    except:
        pass

    db.query("""
        CREATE USER '%s'@'%%' IDENTIFIED BY '%s';""" % (application_name, db_password))

    try: # try to drop the database in case it exists
        db.query(""" DROP DATABASE %s;""" % application_name)
    except:
        pass

    db.query("""
        CREATE DATABASE %s;""" % application_name)

    db.query("""
        USE %s""" % application_name)

    db.query("""
        GRANT ALL ON %s.* TO '%s'@'%%';""" % (application_name, application_name))

    return True

if __name__ == '__main__':
    main()
