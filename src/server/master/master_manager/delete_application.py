#!/usr/bin/env python
#
# Delete an application.
#

from shared import *
import _mysql
from management_database.models import Application

def main():
    check_trusted_uid(program_name = sys.argv[0])
    kwargs = check_and_return_keyword_args(sys.argv, ['application_name'])
    application_name = kwargs['application_name']
    try:
        # Look up the application
        application = Application.get_by_name(application_name)
        # Disable the application to the outside world
        call_proxycache_managers_delete_application(application_name)
        # Stop running the application
        call_worker_managers_delete_application(application_name)
        # Remove the git repository
        try:
            shutil.rmtree(os.path.join(REPOS_DIR, application_name + ".git"))
        except:
            log_last_exception()
        # Remove the database
        db = _mysql.connect(
            host = application.db_host,
            user = DATABASE_ROOT_USER, 
            passwd = DATABASE_ROOT_PASSWORD)
        try: # try to remove the user if it already exists
            db.query(""" DROP USER '%s'@'%%';""" % application_name)
        except:
            pass
        try: # try to drop the database in case it exists
            db.query(""" DROP DATABASE %s;""" % application_name)
        except:
            pass
        # Mark the application as deleted
        application.mark_deleted()
    except:
        log_last_exception()
        print 'Remove failed for application "%s".' % application_name
        sys.exit(1)

if __name__ == '__main__':
    main()
