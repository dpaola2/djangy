#!/srv/djangy/run/python-virtual/bin/python

import warnings
warnings.simplefilter("ignore")

import os, re, sys

excluded_repos = [
    'gitosis-admin',
    'djangy',
    'test',
]

if __name__ == '__main__':
    # In practice, I've observed GIT_DIR to be '.', but it could potentially
    # be something else.  So we convert it to an absolute path and then
    # remove it from the environment, because it tends to confuse other
    # git operations performed later.
    if os.environ.has_key('GIT_DIR'):
        git_repository_path = os.path.abspath(os.environ['GIT_DIR'])
        os.environ.pop('GIT_DIR')
    else:
        git_repository_path = os.getcwd()
    # Make sure we were passed an official git project repository
    match = re.match('^/srv/git/repositories/([A-Za-z][A-Za-z0-9]*)\.git$', git_repository_path);
    if match == None:
        sys.exit(1)
    application_name = match.group(1)
    # Ignore special repositories that aren't supposed to use the post-receive hook
    if application_name in excluded_repos:
        sys.exit(0)
    # Update the deployment of this application
    args = ['/srv/djangy/run/master_manager/setuid/run_deploy', 'application_name', application_name]
    os.execv(args[0], args)
