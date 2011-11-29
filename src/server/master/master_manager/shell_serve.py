#!/srv/djangy/run/python-virtual/bin/python
#
# Note: doesn't import shared.ssh_and_git because this runs as the "shell"
# user, which doesn't have access to write to /srv/logs/master.log...
#

from djangy_server_shared import become_application_setup_uid_gid, constants, find_django_project
from management_database import *
import os, re, subprocess, sys

def main():
    try:
        shell_serve(int(sys.argv[1]))
    except:
        sys.stderr.write('Access denied.  Please email support@djangy.com for help.\n')

def shell_serve(ssh_public_key_id):
    """ Serve an incoming manage.py request.  Should only be called via ~shell/.ssh/authorized_keys """
    # Get all users who have the specified public key
    users = SshPublicKey.get_users_by_public_key_id(ssh_public_key_id)
    # SSH_ORIGINAL_COMMAND format:
    # <application_name> manage.py [args...]
    ssh_original_command = os.environ['SSH_ORIGINAL_COMMAND']
    matches = re.match('^\s*(?P<application_name>[A-Za-z0-9]+)\s+manage\.py\s+(?P<args>.*?)\s*$', ssh_original_command)
    assert matches
    application_name = matches.group('application_name')
    args = matches.group('args')
    # blocked commands
    if args.split()[0] in constants.BLOCKED_COMMANDS:
        sys.stderr.write('For security reasons, that command has been disallowed.  Contact support@djangy.com for help.\n')
        return None
    # Look up the requested application, and make sure that at least one
    # user associated with the SSH key that was used has access to it.
    application = Application.get_by_name(application_name)
    if application.accessible_by_any_of(users):
        # Look up bundle information
        bundle_version      = application.bundle_version
        bundle_name         = '%s-%s' % (application_name, bundle_version)
        bundle_path         = os.path.join(constants.BUNDLES_DIR, bundle_name)
        setup_uid           = application.setup_uid
        app_gid             = application.app_gid
        bin_path            = os.path.join(bundle_path, 'python-virtual/bin')
        python_path         = os.path.join(bin_path, 'python')
        # It might be preferable to read the bundle configuration instead, to be consistent...
        django_project_path = find_django_project(os.path.join(bundle_path, 'application'))
        # Get around buffered stdout
        os.dup2(2, 1)
        # Run the command:
        os.chdir(django_project_path)
        become_application_setup_uid_gid('shell_serve', setup_uid, app_gid)
        command = '%s -u manage.py %s' % (python_path, args)
        os.execve('/bin/bash', ['bash', '-c', command], {'PATH':'/bin:/usr/bin:%s' % bin_path})

if __name__ == '__main__':
    main()
