# Standard Python libraries
import os, re
# Djangy libraries installed in our virtualenv
from djangy_server_shared import *
from management_database.models import Application, Process, Chargable, Subscription
# Libraries within this package
import exceptions

open_log_file(os.path.join(LOGS_DIR, 'master_api.log'), 0600)

def retrieve_logs(application_name):
    return run_external_program([os.path.join(MASTER_SETUID_DIR, 'run_retrieve_logs'), 'application_name', application_name])['stdout_contents']

def name_available(name):
    """ Checks for application name availability. """
    if Application.get_by_name(name):
        return False
    else:
        return (re.match('^[A-Za-z][A-Za-z0-9]{4,14}$', name) != None) \
            and not (name in RESERVED_APPLICATION_NAMES)

def toggle_debug(application_name, debug):
    cmd = [os.path.join(MASTER_SETUID_DIR, 'run_allocate'), 'application_name', application_name, 'debug', str(debug)]
    run_external_program(cmd)

def update_application_allocation(application_name, changes):
    allocations = {
        'application_processes':'num_procs',
        'background_processes':'celery_procs'
    }
    try:
        application = Application.get_by_name(application_name)
        cmd = [os.path.join(MASTER_SETUID_DIR, 'run_allocate'), 'application_name', application_name]
        for key in changes.keys():
            if allocations.get(key):
                cmd += [str(allocations[key]), str(changes[key])]

        result = run_external_program(cmd)
        if external_program_encountered_error(result):
            raise exceptions.UpdateAllocationException(result['exit_code'], application_name)

        for key in changes.keys():
            if allocations.get(key):
                try:
                    application.report_allocation_change(Chargable.get_by_component(key), str(changes[key]))
                except Exception as e:
                    log_error_message(e)

    except Exception as e:
        log_last_exception()
        logging.error(e)
        return False
    return True

def _call_proxycache_manager(application_name):
    return run_external_program([os.path.join(MASTER_SETUID_DIR, 'run_configure_proxycache'), 'application_name', application_name])

def add_domain_name(application_name, domain_name):
    Application.get_by_name(application_name).add_domain_name(domain_name)
    result = _call_proxycache_manager(application_name)
    if external_program_encountered_error(result):
        raise exceptions.AddDomainException(result['exit_code'], application_name, domain_name)

def delete_domain_name(application_name, domain_name):
    Application.get_by_name(application_name).delete_domain_name(domain_name)
    result = _call_proxycache_manager(application_name)
    if external_program_encountered_error(result):
        raise exceptions.DeleteDomainException(result['exit_code'], application_name, domain_name)

def enable_server_cache(application_name):
    application = Application.get_by_name(application_name)
    application.enable_server_cache()
    result = _call_proxycache_manager(application_name)
    assert not external_program_encountered_error(result)

def disable_server_cache(application_name):
    application = Application.get_by_name(application_name)
    application.disable_server_cache()
    result = _call_proxycache_manager(application_name)
    assert not external_program_encountered_error(result)

def add_application(application_name, email, pubkey):
    result = run_external_program([ \
        os.path.join(MASTER_SETUID_DIR, 'run_add_application'), \
        'application_name', application_name, 'email', email, 'pubkey', pubkey])
    if external_program_encountered_error(result):
        raise exceptions.AddApplicationException(result['exit_code'], application_name, email, pubkey)

def remove_application(application_name):
    result = run_external_program([ \
        os.path.join(MASTER_SETUID_DIR, 'run_delete_application'), \
        'application_name', application_name])
    if external_program_encountered_error(result):
        raise exceptions.RemoveApplicationException(result['exit_code'], application_name)

def get_application_log(application_name, log_name='django.log'):
    result = run_external_program([ \
        os.path.join(MASTER_SETUID_DIR, 'run_get_application_log'), \
        'application_name', application_name, \
        'log_name', log_name])
    if external_program_encountered_error(result):
        return '[Log not found]'
    else:
        return result['stdout_contents']

def command(application_name, cmd, *args):
    result = run_external_program([ \
        os.path.join(MASTER_SETUID_DIR, 'run_command'), \
        'application_name', application_name, \
        'command', cmd] + list(args))
    return result['stdout_contents']

def add_ssh_public_key(email, ssh_public_key):
    result = run_external_program([ \
        os.path.join(MASTER_SETUID_DIR, 'run_add_ssh_public_key'), \
        'email', email, \
        'ssh_public_key', ssh_public_key])
    assert not external_program_encountered_error(result)

def remove_ssh_public_key(email, ssh_public_key_id):
    result = run_external_program([ \
        os.path.join(MASTER_SETUID_DIR, 'run_remove_ssh_public_key'), \
        'email', email, \
        'ssh_public_key_id', ssh_public_key_id])
    assert not external_program_encountered_error(result)
