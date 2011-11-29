#!/usr/bin/env python
#
# Placeholder -- should import settings.py from the django project and print
# out ADMIN_MEDIA_PREFIX.  Needs to run as setup_uid and in the application's
# virtual environment.
#

from djangy_server_shared import *

def main():
    kwargs = check_and_return_keyword_args(sys.argv, ['setup_uid', 'app_gid', 'virtual_env_path', 'django_project_path'])
    os.chdir('/')
    become_application_setup_uid_gid(sys.argv[0], int(kwargs['setup_uid']), int(kwargs['app_gid']))
    os.chdir(kwargs['django_project_path'])
