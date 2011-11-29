import os.path, sys
from djangy_server_shared import *
from management_database import *

def _call_remote(hosts, make_command):
    # Run commands in parallel on all designated hosts
    # Note: command arguments will be parsed by shell, and must not contain spaces
    num_success = 0
    num_failure = 0
    stdout_contents_dict = { }
    programs = []
    for h in hosts:
        p = ExternalProgram(['ssh', h] + make_command(h))
        p.host = h
        programs.append(p)
    sys.stdout.flush()
    for p in programs:
        if p:
            p.start()
    for p in programs:
        if p:
            result = p.finish()
            if external_program_encountered_error(result):
                num_failure = num_failure + 1
            else:
                num_success = num_success + 1
            stdout_contents_dict[p.host] = result['stdout_contents']
        else:
            num_failure = num_failure + 1

    return (num_success, num_failure, stdout_contents_dict)

def call_worker_managers_retrieve_logs(application_name, hosts=None):
    def make_retrieve_command(application_info, host):
        command = [os.path.join(WORKER_SETUID_DIR, 'run_retrieve_logs'),
            'application_name', application_info.name,
            'bundle_version', application_info.bundle_version
        ]
        return command

    (num_success, num_failure, stdout_contents_dict) = _call_worker_managers(application_name, make_retrieve_command, hosts)
    return stdout_contents_dict

def call_worker_managers_allocate(application_name, hosts=None):
    def make_allocate_command(application_info, host):
        try:
            p = Process.objects.get(application=application_info, proc_type='gunicorn', host=host)
            num_procs = p.num_procs
            port = p.port
        except:
            num_procs = 0
            port = 0
        try:
            p = Process.objects.get(application=application_info, proc_type='celery', host=host)
            celery_procs = p.num_procs
        except:
            celery_procs = 0
        virtualhosts = VirtualHost.get_virtualhosts_by_application_name(application_name)
        http_virtual_hosts = ','.join(virtualhosts)
        command = [os.path.join(WORKER_SETUID_DIR, 'run_deploy'), \
            'application_name', application_info.name, \
            'bundle_version', application_info.bundle_version, \
            'num_procs', str(num_procs), \
            'proc_num_threads', str(application_info.proc_num_threads), \
            'proc_mem_mb', str(application_info.proc_mem_mb), \
            'proc_stack_mb', str(application_info.proc_stack_mb), \
            'debug', str(application_info.debug), \
            'http_virtual_hosts', http_virtual_hosts, \
            'host', host, \
            'port', str(port),
            'celery_procs', str(celery_procs)]
        return command

    _call_worker_managers(application_name, make_allocate_command, hosts)

def call_worker_managers_delete_application(application_name, hosts=None):
    def make_delete_application_command(application_info, host):
        command = [os.path.join(WORKER_SETUID_DIR, 'run_delete_application'), \
            'application_name', application_info.name]
        return command

    _call_worker_managers(application_name, make_delete_application_command, hosts)

def _call_worker_managers(application_name, make_command, hosts=None):
    # Load global application info
    application = Application.get_by_name(application_name)
    bundle_version = application.bundle_version
    if bundle_version == None or bundle_version == '':
        return

    def make_command2(host):
        return make_command(application, host)

    # Load relevant hosts from database if none specified
    if hosts == None:
        hosts = [h for (h, p) in Process.get_hosts_ports_by_application(application)]

    (num_success, num_failure, stdout_contents_dict) = _call_remote(hosts, make_command2)
    if num_failure > 0:
        print ('%i success, %i failure' % (num_success, num_failure)),

    return (num_success, num_failure, stdout_contents_dict)

def call_proxycache_managers_configure(application_name):
    application        = Application.get_by_name(application_name)
    # Hosts running proxycache serving this application
    proxycache_hosts   = ProxyCache.get_proxycache_hosts_by_application(application)
    # Virtual hosts used by this application
    virtualhosts       = VirtualHost.get_virtualhosts_by_application(application)
    # Real hosts and port numbers running instances of this application
    worker_hosts_ports = Process.get_hosts_ports_by_application(application)

    http_virtual_hosts = ','.join(virtualhosts)
    worker_servers = ','.join(['%s:%s' % (h, p) for (h, p) in worker_hosts_ports])

    command = [os.path.join(PROXYCACHE_SETUID_DIR, 'run_configure'), \
        'application_name',    application_name, \
        'http_virtual_hosts',  http_virtual_hosts, \
        'worker_servers',      worker_servers, \
        'cache_index_size_kb', str(application.cache_index_size_kb), \
        'cache_size_kb',       str(application.cache_size_kb)]

    (num_success, num_failure, stdout_contents_dict) = _call_remote(proxycache_hosts, lambda h: command)
    if num_failure > 0:
        print ('%i success, %i failure' % (num_success, num_failure)),

def call_proxycache_managers_delete_application(application_name):
    # Hosts running proxycache serving this application
    proxycache_hosts   = ProxyCache.get_proxycache_hosts_by_application_name(application_name)

    command = [os.path.join(PROXYCACHE_SETUID_DIR, 'run_delete_application'), 'application_name', application_name]

    (num_success, num_failure, stdout_contents_dict) = _call_remote(proxycache_hosts, lambda h: command)
    if num_failure > 0:
        print ('%i success, %i failure' % (num_success, num_failure)),
