from djangy_server_shared import *
from nginx import *

TRUSTED_UIDS.extend(PROXYCACHE_TRUSTED_UIDS)

open_log_file(os.path.join(LOGS_DIR, 'proxycache.log'), 0600)
