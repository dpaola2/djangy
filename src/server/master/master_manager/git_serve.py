#!/srv/djangy/run/python-virtual/bin/python
#
# Note: doesn't import shared.ssh_and_git because this runs as the "git"
# user, which doesn't have access to write to /srv/logs/master.log...
#

from djangy_server_shared import constants
from management_database import *
import os, re, sys

def main():
    try:
        git_serve(int(sys.argv[1]))
    except:
        sys.stderr.write('Access denied.  Please email support@djangy.com for help.\n')

def git_serve(ssh_public_key_id):
    """ Serve an incoming git push/pull request.  Should only be called via ~git/.ssh/authorized_keys """
    assert os.getuid() == constants.GIT_UID
    # Usage: git_serve <id>
    # git_serve() should only be called via ~git/.ssh/authorized_keys
    # Each line of authorized_keys specifies a particular SshPublicKey.id
    # from the database as an argument to git_serve.
    users = SshPublicKey.get_users_by_public_key_id(ssh_public_key_id)
    # Look at the command git wanted to run.
    # It should be one of git-upload-pack or git-receive-pack.
    # (or their variants, 'git upload-pack' and 'git receive-pack')
    # The argument to the command is <application_name>.git
    ssh_original_command = os.environ['SSH_ORIGINAL_COMMAND']
    matches = re.match('^\s*(git(-|\s+)(?P<command>upload-pack|receive-pack))' \
        + '\s+\'(?P<application_name>[A-Za-z0-9]{1,15})\.git\'\s*$', ssh_original_command)
    command = 'git-' + matches.group('command')
    application_name = matches.group('application_name')
    # Look up the requested application, and make sure that at least one
    # user associated with the SSH key that was used has access to it.
    application = Application.get_by_name(application_name)
    if application.accessible_by_any_of(users):
        # Finally, run the git server-side command
        os.execvp('git', ['git', 'shell', '-c', "%s '/srv/git/repositories/%s.git'" % (command, application_name)])

if __name__ == '__main__':
    main()
