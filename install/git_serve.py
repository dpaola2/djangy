import os, os.path, subprocess
from core import *

_POST_RECEIVE_HOOK_PATH='/srv/djangy/run/python-virtual/bin/post_receive.py'

@print_when_used
def require_no_git_serve():
    require_remove('/srv/git/.ssh')

@print_when_used
def require_git_serve():
    # Update system-wide post-receive hook template
    require_link('/usr/share/git-core/templates/hooks/post-receive', _POST_RECEIVE_HOOK_PATH)
    # Update post-receive hooks in all repositories
    for repo_name in os.listdir('/srv/git/repositories'):
        repo_post_receive = os.path.join('/srv/git/repositories', repo_name, 'hooks/post-receive')
        require_link(repo_post_receive, _POST_RECEIVE_HOOK_PATH)
    # Ownership permissions
    require_recursive('/srv/git', username='git', groupname='git')
