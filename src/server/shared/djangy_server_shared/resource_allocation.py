class ResourceAllocation(object):
    def __init__(self, num_procs, proc_num_threads, proc_mem_mb, proc_stack_mb, debug, http_virtual_hosts, host, port, celery_procs):
        self.num_procs          = num_procs
        self.proc_num_threads   = proc_num_threads
        self.proc_mem_mb        = proc_mem_mb
        self.proc_stack_mb      = proc_stack_mb
        self.debug              = debug
        self.http_virtual_hosts = http_virtual_hosts
        self.host               = host
        self.port               = port
        self.celery_procs       = celery_procs

    def to_command_line(self):
        return ['num_procs',          str(self.num_procs), \
                'proc_num_threads',   str(self.proc_num_threads), \
                'proc_mem_mb',        str(self.proc_mem_mb), \
                'proc_stack_mb',      str(self.proc_stack_mb), \
                'debug',              str(self.debug), \
                'http_virtual_hosts', ','.join(http_virtual_hosts), \
                'host',               self.host, \
                'port',               str(self.port), \
                'celery_procs',       str(self.celery_procs)]

    @staticmethod
    def from_command_line_dict(dict):
        return ResourceAllocation(
            num_procs          = int(dict['num_procs']),
            proc_num_threads   = int(dict['proc_num_threads']),
            proc_mem_mb        = int(dict['proc_mem_mb']),
            proc_stack_mb      = int(dict['proc_stack_mb']),
            debug              = (dict['debug'] == 'True'),
            http_virtual_hosts = dict['http_virtual_hosts'].split(','),
            host               = dict['host'],
            port               = int(dict['port']),
            celery_procs       = int(dict['celery_procs']))
