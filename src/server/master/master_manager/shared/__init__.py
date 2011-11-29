from djangy_server_shared import *
from management_database import *

from allocate_workers import *
from call_remote import *
from ssh_and_git import *

TRUSTED_UIDS.extend(MASTER_TRUSTED_UIDS)

open_log_file(os.path.join(LOGS_DIR, 'master.log'), 0600)

