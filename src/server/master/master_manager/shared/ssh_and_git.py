from djangy_server_shared import *
from management_database import *
import os, os.path, re

def add_ssh_public_key(user, pubkey):
    """ Add a user's SSH public key to mangement_database and git access. """
    (ssh_public_key, comment) = parse_ssh_public_key(pubkey)
    # Update the management_database
    user.add_ssh_public_key(ssh_public_key, comment)
    # Update ~git/.ssh/authorized_keys
    regenerate_ssh_authorized_keys()

def parse_ssh_public_key(pubkey):
    """ Parse an SSH public key into the key proper and the optional
        comment.  Throws an exception when given a malformed key.  """
    pubkey2 = pubkey.replace('\r', '')
    matches = re.match('^(?P<ssh_public_key>(?:ssh-dss|ssh-rsa)\s+[A-Za-z0-9/+]+=*)\s+(?P<comment>.*)$', pubkey2, re.DOTALL)
    if matches:
        return (matches.group('ssh_public_key'), matches.group('comment'))
    key_data_matches = re.match('\s*---- BEGIN SSH2 PUBLIC KEY ----\s*\n(?:[^:\n]*:[^\n]*\n)*(?P<key_data>[A-Za-z0-9/+\s\n]+=*)\s*\n\s*---- END SSH2 PUBLIC KEY ----\s*', pubkey2, re.DOTALL)
    key_type_matches = re.match('.*?\s*Comment\s*:\s*(?P<comment>(?:(?P<rsa>[Rr][Ss][Aa])|(?P<dsa>[Dd][Ss][Aa])|(?P<dss>[Dd][Ss][Ss])|[^\n])*)\s*\n.*?', pubkey2, re.DOTALL)
    if key_data_matches:
        if key_type_matches.group('rsa'):
            key_type = 'rsa'
        elif key_type_matches.group('dsa'):
            key_type = 'dss'
        elif key_type_matches.group('dss'):
            key_type = 'dss'
        else:
            key_type = 'rsa'
        key_data = key_data_matches.group('key_data').replace('\n', '')
        ssh_public_key = 'ssh-%s %s' % (key_type, key_data)
        if key_type_matches.group('comment'):
            return (ssh_public_key, key_type_matches.group('comment'))
        else:
            return (ssh_public_key, '')
    return ('', 'Invalid SSH public key: %s' % pubkey)

def create_git_repository(application_name):
    """ Create a new git repository for a given application.  Performs no validation. """
    # Location of the repository: /srv/git/repositories/<application_name>.git
    repo_path = os.path.join(REPOS_DIR, application_name + '.git')
    # We will run "git init" as the git user/group
    def become_git_user():
        set_uid_gid(GIT_UID, GIT_GID)
    # Run "git init"
    run_external_program(['git', 'init', '--bare', repo_path], cwd='/', preexec_fn=become_git_user)

def regenerate_ssh_authorized_keys():
    """ Regenerate /srv/git/.ssh/authorized_keys and /srv/shell/.ssh/authorized_keys from the management_database. """
    # Programs that will be run when the user connects via ssh
    git_serve_path = GIT_SERVE_PATH
    shell_serve_path = SHELL_SERVE_PATH
    # Generate authorized_keys
    git_authorized_keys = generate_ssh_authorized_keys_contents(git_serve_path)
    shell_authorized_keys = generate_ssh_authorized_keys_contents(shell_serve_path)
    # Write out authorized_keys
    write_to_file(os.path.join(GIT_SSH_DIR, 'authorized_keys'), git_authorized_keys, GIT_UID, GIT_GID, AUTHORIZED_KEYS_MODE)
    write_to_file(os.path.join(SHELL_SSH_DIR, 'authorized_keys'), shell_authorized_keys, SHELL_UID, SHELL_GID, AUTHORIZED_KEYS_MODE)

def generate_ssh_authorized_keys_contents(command_path):
    # Options to lock down ssh access
    options = 'no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty'
    # Create lines in authorized_keys for each ssh public key in the datbasee
    keys = filter(lambda y: y.ssh_public_key.strip() != '', SshPublicKey.objects.all())
    lines = ['command="%s %i",%s %s' % (command_path, x.id, options, x.ssh_public_key) for x in keys]
    authorized_keys_contents = '\n'.join(lines) + '\n'
    return authorized_keys_contents

def write_to_file(path, contents, uid, gid, mode):
    f = open(path, 'w')
    f.write(contents)
    f.close()
    os.chown(path, uid, gid)
    os.chmod(path, mode)
