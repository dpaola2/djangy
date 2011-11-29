from management_database import Process, WorkerHost
import copy, random
from django.db.models import Sum
from djangy_server_shared.constants import *
from djangy_server_shared import log_info_message
from call_remote import *

def _random_worker_port():
    return random.randrange(WORKER_PORT_LOWER, WORKER_PORT_UPPER)

def _random_unique_worker_port_on_host(host):
    port = _random_worker_port()
    while Process.objects.filter(host=host).filter(port=port).exists():
        port = _random_worker_port()
    return port

def allocate_workers(application):
    # Theoretically, we should only allow one application to compute
    # reallocation at a time, to prevent accidentally overloading workers. 
    # In practice, that seems overly conservative.

    log_info_message('allocate_workers("%s", %i, %i)' % (application.name, application.num_procs, application.celery_procs))

    gunicorn_updated_worker_hosts = _compute_reallocation_to_worker_hosts_update_db(application, 'gunicorn', application.num_procs)
    celery_updated_worker_hosts   = _compute_reallocation_to_worker_hosts_update_db(application, 'celery'  , application.celery_procs)
    updated_worker_hosts = list(set(gunicorn_updated_worker_hosts).union(set(celery_updated_worker_hosts)))

    # Update the worker_managers whose allocations have changed
    call_worker_managers_allocate(application.name, updated_worker_hosts)
    # Update the proxycache_managers
    call_proxycache_managers_configure(application.name)

def _compute_reallocation_to_worker_hosts_update_db(application, proc_type, new_num_procs):
    # Compute the allocation of workers to hosts
    worker_hosts__num_procs = _compute_reallocation_to_worker_hosts_read_db(application, proc_type, new_num_procs)
    # Update the Process table
    updated_worker_hosts = []

    for (worker_host, num_procs) in worker_hosts__num_procs.items():
        try:
            proc = Process.objects.get(application=application, proc_type=proc_type, host=worker_host)
            if num_procs == 0:
                proc.delete()
            elif proc.num_procs != num_procs:
                proc.num_procs = num_procs
                proc.save()
            updated_worker_hosts.append(worker_host)
        except:
            if num_procs != 0:
                port = _random_unique_worker_port_on_host(worker_host)
                proc = Process(application=application, proc_type=proc_type, host=worker_host, port=port, num_procs=num_procs)
                proc.save()
                updated_worker_hosts.append(worker_host)

    return updated_worker_hosts

# Reads the database and returns information about how processes are
# allocated to worker hosts, structured as below.
# Returns :: { <worker_host> : { 'max_procs' : int, 'total_procs': int, 'application_procs' : int } }
def _read_worker_hosts_from_db(application, proc_type):
    # worker_host -> max_procs
    worker_host__max_procs = dict((row['host'], row['max_procs']) for row in WorkerHost.objects.values('host', 'max_procs').distinct())
    # worker_host -> total num_procs
    worker_host__total_procs = dict((row['host'], row['num_procs']) for row in Process.objects.values('host').annotate(num_procs=Sum('num_procs')))
    # worker_host -> application's num_procs
    worker_host__application_procs = dict((row['host'], row['num_procs']) for row in Process.objects.filter(application=application, proc_type=proc_type).values('host', 'num_procs'))

    worker_hosts = { }
    for h in worker_host__max_procs:
        max_procs = worker_host__max_procs[h]
        total_procs = worker_host__total_procs.get(h, 0)
        application_procs = worker_host__application_procs.get(h, 0)
        worker_hosts[h] = {'max_procs': max_procs, 'total_procs': total_procs, 'application_procs': application_procs}

    return worker_hosts

# Call this method to compute an updated allocation of an application's
# processes to hosts.  Does not touch the database or workers, simply
# computes and returns a result.
#
# Tries to spread out an application's processes evenly across all available
# worker hosts, but does not rebalance existing processes.  In other words,
# if N processes need to be added, they will be added to whichever hosts
# have additional capacity and currently have the fewest processe for this
# application.  Similarly, if N processes need to be removed, they will be
# removed from those hosts which have the most processes for this
# application.
#
# application :: management_database.models.Application instance
# new_num_procs :: int -- the number of processes that should be running
#     this application after reallocation (not the number of new processes)
# Returns :: { <worker_host> : int }
#
# Note: if an entry in the return value is 0, we need to contact the
# worker_manager to tell it to stop running this application, and when we
# update the proxycache_manager, we should no longer list that worker.
def _compute_reallocation_to_worker_hosts_read_db(application, proc_type, new_num_procs):
    existing_num_procs = Process.objects.filter(application=application, proc_type=proc_type).aggregate(num_procs=Sum('num_procs'))['num_procs']
    if not existing_num_procs:
        existing_num_procs = 0
    worker_hosts = _read_worker_hosts_from_db(application, proc_type)
    # host -> application's num_procs
    process_allocation = { }
    # Project out the current allocations of processes to hosts
    for h in worker_hosts:
        application_procs = worker_hosts[h]['application_procs']
        if application_procs > 0:
            process_allocation[h] = application_procs
    # More procs?  Compute the added processes to hosts.
    if new_num_procs > existing_num_procs:
        added_num_procs = new_num_procs - existing_num_procs
        added_procs = _compute_allocation_to_worker_hosts(added_num_procs, worker_hosts)
        for h in added_procs:
            process_allocation[h] = process_allocation.get(h, 0) + added_procs[h]
    # Fewer procs?  Compute the removed processes from hosts.
    elif new_num_procs < existing_num_procs:
        removed_num_procs = existing_num_procs - new_num_procs
        removed_procs = _compute_deallocation_from_worker_hosts(removed_num_procs, worker_hosts)
        for h in removed_procs:
            if process_allocation.get(h):
                process_allocation[h] -= removed_procs[h]

    return process_allocation

# Call this method to compute which hosts to allocate num_procs more
# processes for application to.  Does not touch the database or workers,
# simply computes and returns a result.  Tries to spread out an
# application's processes evenly across all available worker hosts.
#
# num_procs_to_add :: int
# worker_hosts :: { <worker_host> : { 'max_procs' : int, 'total_procs': int, 'application_procs' : int } }
# Returns :: { <worker_host> : <num_procs_to_add> }
def _compute_allocation_to_worker_hosts(num_procs_to_add, worker_hosts):
    worker_hosts = copy.deepcopy(worker_hosts)

    # Remove hosts that are maxed out
    maxed_out_worker_hosts = []
    for h in worker_hosts:
        if worker_hosts[h]['total_procs'] >= worker_hosts[h]['max_procs']:
            maxed_out_worker_hosts.append(h)
    for h in maxed_out_worker_hosts:
        del worker_hosts[h]

    # Additional processes added to hosts :: host -> int
    added_procs = { }

    # Helper function: find the host with capacity for at least one more
    # process, that has the fewest number of processes for this application,
    # using total number of processes as a tie-breaker.
    def find_min_host():
        worker_hosts_list = list(worker_hosts)
        # The following line will raise an exception if we're out of capacity.
        min_host = worker_hosts_list[0]
        min_value = worker_hosts[min_host]
        for h in worker_hosts_list[1:]:
            value = worker_hosts[h]
            if (value['application_procs'] < min_value['application_procs']) \
               or (value['application_procs'] == min_value['application_procs'] \
                   and value['total_procs'] < min_value['total_procs']):
                min_host = h
                min_value = value
        return min_host

    # Helper function: update state, adding one process to worker_host
    def add_to_host(worker_host):
        added_procs[worker_host] = added_procs.get(worker_host, 0) + 1
        value = worker_hosts[worker_host]
        value['total_procs'] += 1
        value['application_procs'] += 1
        # Remove host if maxed out
        if value['total_procs'] >= value['max_procs']:
            del worker_hosts[worker_host]

    for i in range(0, num_procs_to_add):
        h = find_min_host()
        add_to_host(h)

    return added_procs

# Call this method to deallocate up to num_procs worker processes for
# application.  If application has fewer than num_procs worker processes,
# that's ok, we'll just deallocate as many as we can.  Does not touch the
# database or workers, simply computes and returns a result.  Tries to leave
# the remaining processes evenly distributed across worker hosts.
#
# num_procs_to_remove :: int
# worker_hosts :: { <worker_host> : { 'max_procs' : int, 'total_procs': int, 'application_procs' : int } }
# Returns :: { <worker_host> : <num_procs_to_remove> }
def _compute_deallocation_from_worker_hosts(num_procs_to_remove, worker_hosts):
    worker_hosts = copy.deepcopy(worker_hosts)

    # Remove hosts that don't contain application processes
    unused_worker_hosts = []
    for h in worker_hosts:
        if worker_hosts[h]['application_procs'] <= 0:
            unused_worker_hosts.append(h)
    for h in unused_worker_hosts:
        del worker_hosts[h]

    # Processes removed from hosts :: host -> int
    removed_procs = { }

    # Helper function: find the host with the most processes from this
    # application, using total number of processes as a tie-breaker.
    def find_max_host():
        worker_hosts_list = list(worker_hosts)
        if worker_hosts_list == []:
            return None
        max_host = worker_hosts_list[0]
        max_value = worker_hosts[max_host]
        for h in worker_hosts_list[1:]:
            value = worker_hosts[h]
            if (value['application_procs'] > max_value['application_procs']) \
               or (value['application_procs'] == max_value['application_procs'] \
                   and value['total_procs'] > max_value['total_procs']):
                max_host = h
                max_value = value
        return max_host

    # Helper function: update state, removing one process from worker_host
    def remove_from_host(worker_host):
        removed_procs[worker_host] = removed_procs.get(worker_host, 0) + 1
        value = worker_hosts[worker_host]
        value['total_procs'] -= 1
        value['application_procs'] -= 1
        # Remove host if it contains no more application processes
        if value['application_procs'] <= 0:
            del worker_hosts[worker_host]

    for i in range(0, num_procs_to_remove):
        h = find_max_host()
        if h:
            remove_from_host(h)

    return removed_procs
