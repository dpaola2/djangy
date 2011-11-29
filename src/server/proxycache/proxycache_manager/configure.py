#!/usr/bin/env python
#
# Configure the nginx proxy cache for a given application.
# Example usage:
#   configure.py application_name testapp http_virtual_hosts 'testapp.djangy.com www.testapp.com' worker_servers 'worker3.internal.djangy.com:8080' cache_index_size_kb 16 cache_size_kb 1024
#

import os
from shared import *
from mako.template import Template
from mako.lookup import TemplateLookup
import clear_cache

def main():
    try:
        check_trusted_uid(sys.argv[0])
        kwargs = check_and_return_keyword_args(sys.argv, ['application_name', \
            'http_virtual_hosts', 'worker_servers', 'cache_index_size_kb', 'cache_size_kb'])

        configure(**kwargs)
    except:
        log_last_exception()

def configure(application_name, http_virtual_hosts, worker_servers, cache_index_size_kb, cache_size_kb):
    create_config_file(application_name, http_virtual_hosts.split(','), \
        worker_servers.split(','), int(cache_index_size_kb), int(cache_size_kb))
    clear_cache.clear_cache(application_name)
    reload_nginx_conf()

def create_config_file(application_name, http_virtual_hosts, \
    worker_servers, cache_index_size_kb, cache_size_kb):

    # Create Nginx config file in nginx/conf/applications/
    #   http_virtual_hosts -- list of virtual host names
    #   worker_servers -- list of 'host:port' for workers
    #   cache_index_size -- in memory
    #   cache_size -- on disk/in disk cache
    print 'Generating nginx configuration file...',
    nginx_conf_path = os.path.join(NGINX_APP_CONF_DIR, '%s.conf' % application_name)

    # Remove the old config file
    try:
        os.remove(nginx_conf_path)
    except:
        pass

    if http_virtual_hosts != [] and worker_servers != []:
        # Create new config file
        upstream_servers = '\n    '.join(map(lambda x: 'server %s;' % x, worker_servers))
        generate_config_file('generic_nginx_conf', nginx_conf_path,
                             application_name    = application_name, \
                             http_virtual_hosts  = ' '.join(http_virtual_hosts), \
                             upstream_servers    = upstream_servers, \
                             cache_index_size_kb = cache_index_size_kb, \
                             cache_size_kb       = cache_size_kb)
        # Set permissions
        os.chown(nginx_conf_path, PROXYCACHE_UID, PROXYCACHE_GID)
        os.chmod(nginx_conf_path, 0600)

    print 'Done.'
    print ''

### Copied from master_manager.deploy ###
def generate_config_file(__template_name__, __config_file_path__, **kwargs):
    """Generate a bundle config file from a template, supplying arguments
    from kwargs."""

    # Load the template
    lookup = TemplateLookup(directories = [PROXYCACHE_TEMPLATE_DIR])
    template = lookup.get_template(__template_name__)
    # Instantiate the template
    instance = template.render(**kwargs)
    # Write the instantiated template to the bundle
    f = open(__config_file_path__, 'w')
    f.write(instance)
    f.close()

if __name__ == '__main__':
    main()
