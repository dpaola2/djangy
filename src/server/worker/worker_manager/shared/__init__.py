import grp, pwd, os, subprocess, sys, tempfile
os.environ['DJANGO_SETTINGS_MODULE'] = 'orm.settings'
from orm.models import *
from djangy_server_shared import *
from lock_application import *
from start_stop import *

TRUSTED_UIDS.extend(WORKER_TRUSTED_UIDS)

open_log_file(os.path.join(LOGS_DIR, 'worker.log'), 0600)
