#!/usr/bin/env python
#
# python application_name <x> [num_procs <x>] [proc_num_threads <x>] [proc_mem_mb <x>] [proc_stack_mb <x>] [debug <x>]
#

from shared import *
from management_database.models import Application, Process
from django.core.exceptions import ObjectDoesNotExist

def main():
    check_trusted_uid(sys.argv[0])
    kwargs = check_and_return_keyword_args(sys.argv, ['application_name'], \
        ['num_procs', 'proc_num_threads', 'proc_mem_mb', \
        'proc_stack_mb', 'debug', 'celery_procs'])
    try:
        allocate_application(**kwargs)
    except:
        log_last_exception()
        print 'Allocation failed for application "%s".' % kwargs['application_name']
        sys.exit(1)

def allocate_application(application_name, num_procs=None, proc_num_threads=None, proc_mem_mb=None, proc_stack_mb=None, debug=None, celery_procs=None):
    application_info = Application.get_by_name(application_name)

    if num_procs != None:
        application_info.num_procs = int(num_procs)
    if celery_procs != None:
        application_info.celery_procs = int(celery_procs)
    # Adjust allocation parameters relevant to each individual process of an
    # application: num threads, total memory, stack size, debug
    if proc_num_threads:
        application_info.proc_num_threads = int(proc_num_threads)
    if proc_mem_mb:
        application_info.proc_mem_mb = int(proc_mem_mb)
    if proc_stack_mb:
        application_info.proc_stack_mb = int(proc_stack_mb)
    if debug:
        application_info.debug = (debug == 'True')

    # Save the updated settings
    application_info.save()

    # Num processes is done differently because it requires
    # reallocation of processes to hosts, and must directly
    # contact hosts from which a process is removed.
    if (num_procs != None) or (celery_procs != None):
        allocate_workers(application_info)
    else:
        # Apply the settings to all deployed workers
        call_worker_managers_allocate(application_name)
        # (Don't need to update proxycache_managers)
        #call_proxycache_managers_configure(application_name)

if __name__ == '__main__':
    main()
