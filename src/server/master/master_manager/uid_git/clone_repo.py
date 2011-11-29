#!/usr/bin/env python
#
# Should be run as the git user/group.
#

from djangy_server_shared import *

def main():
    program_name = sys.argv[0]
    become_uid_gid(program_name, GIT_UID, GIT_GID)
    args = sys.argv[1:]
    if len(args) != 2:
        print_or_log_usage('Usage: %s <master_repo_path> <temp_repo_path>\n' % program_name)
        sys.exit(1)
    clone_repo(*args)

def clone_repo(master_repo_path, temp_repo_path):
    # git clone
    run_external_program(['git', 'clone', master_repo_path, temp_repo_path], cwd=temp_repo_path)
    if not os.path.exists(temp_repo_path):
        log_error_message('git clone failed')
        sys.exit(3)
    # read current version of git repository
    result = run_external_program(['git', 'show-ref', '--heads', '-s'], cwd=temp_repo_path)
    stdout = result['stdout_contents'].split('\n')
    if len(stdout) < 1:
        git_repo_version = ''
    else:
        git_repo_version = stdout[0]
    if not validate_git_repo_version(git_repo_version):
        log_error_message('git returned invalid application version (%s)' % git_repo_version)
        sys.exit(4)
    # output current version of git repository
    print git_repo_version
    sys.exit(0)

def validate_git_repo_version(git_repo_version):
    return (None != re.match('^[0-9a-f]{40}$', git_repo_version))

if __name__ == '__main__':
    main()
