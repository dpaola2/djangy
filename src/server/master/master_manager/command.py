#!/usr/bin/env python
#
# Run a simple manage.py command as an application's setup_uid.
#

from shared import *

ALLOWED_CMDS = [
    'syncdb',
    'migrate',
    'createsuperuser'
]

def main():
    check_trusted_uid(sys.argv[0])

    # Check command line arguments
    if not (len(sys.argv) >= 5 \
    and sys.argv[1] == 'application_name' \
    and is_valid_django_app_name(sys.argv[2]) \
    and sys.argv[3] == 'command'
    and (sys.argv[4] in ALLOWED_CMDS)):
        print_or_log_usage("Usage: %s application_name <x> command <x> [...]" % sys.argv[0])
        sys.exit(1)

    # Extract command line arguments
    application_name = sys.argv[2]
    command = ['python', 'manage.py'] + sys.argv[4:]
    stdin_contents = None

    # handle the special case of adding a superuser (piping python code to python manage.py shell)
    if sys.argv[4] == 'createsuperuser':
        command = ['python', 'manage.py', 'shell']
        username = 'admin'
        email = ''
        password = gen_password()

        stdin_contents = """
from django.contrib.auth.models import User
try:
    found = User.objects.get(username='admin')
    found.delete()
except Exception, e:
    pass

User.objects.create_superuser('%s', '%s', '%s')

""" % (username, email, password)
        status = run_command(application_name, command, stdin_contents = stdin_contents, pass_stdout = False)
        if status == 0:
            print "Superuser '%s' created with password: '%s'" % (username, password)
        sys.exit(status)

    # Run the actual command as the application's setup_uid
    sys.exit(run_command(application_name, command, stdin_contents = stdin_contents))

def run_command(application_name, args, stdin_contents = None, pass_stdout = True):
    try:
        check_application_name(application_name)
        # Look up application info in the database
        application_info = Application.get_by_name(application_name)
        bundle_version   = application_info.bundle_version
        setup_uid        = application_info.setup_uid
        app_gid          = application_info.app_gid
        # Validate UID/GID
        check_setup_uid(setup_uid)
        check_app_gid(app_gid)
        # Compute the bundle path
        bundle_name         = '%s-%s' % (application_name, bundle_version)
        bundle_path         = os.path.join(BUNDLES_DIR, bundle_name)
        # Find the django project within the repository; this is where
        # manage.py needs to be run from
        django_project_path = find_django_project(os.path.join(bundle_path, 'application'))
        # Run the command
        result              = run_external_program(list(args), \
                                  cwd=django_project_path, pass_stdout=pass_stdout, stderr_to_stdout=True, \
                                  preexec_fn=gen_preexec(bundle_name, setup_uid, app_gid), stdin_contents = stdin_contents)
        return result['exit_code']
    except Exception as e:
        log_last_exception()
        print str(e)
        sys.exit(2)

def gen_preexec(bundle_name, uid, gid):
    """Generate a preexec_fn to be passed to run_external_program() which (a) sets up the environment, and (b) sets the uid/gid"""
    def command_preexec_fn():
        os.environ.clear()
        virtual_env_dir = os.path.join(BUNDLES_DIR, '%s/python-virtual' % bundle_name)
        os.environ['PATH'] = '%s:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' % os.path.join(virtual_env_dir, 'bin')
        os.environ['VIRTUAL_ENV'] = virtual_env_dir
        set_uid_gid(uid, gid)
    return command_preexec_fn

if __name__ == '__main__':
    main()
