from djangy_server_shared import *

def reload_nginx_conf():
    result = run_external_program([NGINX_BIN_PATH, '-t'])
    if result['exit_code'] != 0: # (note that 'nginx -t' outputs on stderr on success as well as failure)
        # Error should already be logged by run_external_program
        return
    run_external_program([NGINX_BIN_PATH, '-s', 'reload'])
