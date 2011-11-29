#!/usr/bin/env python

from shared import *
from mako.lookup import TemplateLookup
from django.core.exceptions import ObjectDoesNotExist
import re

def main():
    try:
        check_trusted_uid(sys.argv[0])
        kwargs = check_and_return_keyword_args(sys.argv, ['application_name', 'bundle_version',
            'num_procs', 'proc_num_threads', 'proc_mem_mb', 'proc_stack_mb', 'debug', 'http_virtual_hosts',
            'host', 'port', 'celery_procs'])

        application_name    = kwargs['application_name']
        bundle_version      = kwargs['bundle_version']
        resource_allocation = ResourceAllocation.from_command_line_dict(kwargs)

        set_application_allocation(application_name, resource_allocation)
        deploy_application(application_name    = application_name,
                           bundle_version      = bundle_version,
                           resource_allocation = resource_allocation)
    except:
        log_last_exception()

def set_application_allocation(application_name, resource_allocation):
    # Try to find an existing application
    try:
        application_info = LocalApplication.objects.get(application_name = application_name)
        # Uses manual locking rather than @lock_application because we have
        # to gracefully handle the case of creating a new object.
        lock = LocalApplicationLocks.lock(application_name)
    except ObjectDoesNotExist:
        # Or create a new one
        # XXX race condition if two LocalApplications with the same application_name are created concurrently...
        application_info = LocalApplication(application_name = application_name, is_stopped = False)
        lock = None

    ra = resource_allocation

    # Set fields
    application_info.num_procs        = ra.num_procs
    application_info.proc_num_threads = ra.proc_num_threads
    application_info.proc_mem_mb      = ra.proc_mem_mb
    application_info.proc_stack_mb    = ra.proc_stack_mb
    application_info.port             = ra.port
    application_info.celery_procs     = ra.celery_procs

    application_info.save()

    print lock
    LocalApplicationLocks.unlock(lock)

@lock_application
def deploy_application(application_name, bundle_version, resource_allocation):
    # Note that because this function is wrapped in @_lock_application,
    # it will raise an exception if called before set_application_allocation()

    # Compose bundle_name
    bundle_name = application_name + '-' + bundle_version

    # Copy bundle
    application_info = LocalApplication.objects.get(application_name=application_name)
    old_bundle_version = application_info.bundle_version
    bundle_info = copy_bundle_from_remote_host(application_name, bundle_version, old_bundle_version)

    # Stop old version of application
    should_restart = stop_application(application_name)
    # Either delete an application with zero processes or restart one with nonzero.
    if resource_allocation.num_procs == 0 and resource_allocation.celery_procs == 0:
        application_info.delete()
    else:
        try:
            # Create configuration files from templates
            create_config_files(application_name, bundle_version, bundle_name, bundle_info, resource_allocation)
            # Update current bundle version in database
            application_info.bundle_version = bundle_version
            application_info.save()
            # Create log files
            create_log_files(bundle_name, bundle_info.web_uid, bundle_info.app_gid)
        finally:
            # Start new version of application
            if should_restart:
                start_application(application_name)

    # If it all worked, we can delete the old bundle now...
    # For now, we just mark it by creating a file called 'old'
    if old_bundle_version and old_bundle_version != bundle_version:
        try:
            make_file(os.path.join(BUNDLES_DEST_DIR, application_name + '-' + old_bundle_version, 'old'), 0600)
        except:
            # Old bundle doesn't exist
            log_last_exception()

# Note: we should make as much of this as possible run without root
# permissions.  The tricky part is we need to know what permissions are
# needed, because the remote bundle's bundle_info.config file specifies
# its UIDs and GID...
def copy_bundle_from_remote_host(application_name, bundle_version, old_bundle_version):
    bundle_name           = application_name + '-' + bundle_version
    local_bundle_path     = os.path.join(BUNDLES_DEST_DIR,  bundle_name)
    remote_bundle_path    = BUNDLES_SRC_HOST + ':' + os.path.join(BUNDLES_SRC_DIR, bundle_name)
    #remote_bundle_path    = os.path.join(BUNDLES_SRC_DIR, bundle_name)
    if old_bundle_version != None:
        old_bundle_name       = application_name + '-' + old_bundle_version
        local_old_bundle_path = os.path.join(BUNDLES_DEST_DIR,  old_bundle_name)
    else:
        old_bundle_name       = ''
        local_old_bundle_path = ''

    # Check if bundle already exists
    if os.path.exists(local_bundle_path):
        # Assume the bundle is ok--but log a warning!
        log_warning_message('Warning: bundle "%s" already exists' % bundle_name)
        return BundleInfo.load_from_file(os.path.join(local_bundle_path, 'config', 'bundle_info.config'))

    # Copy bundle:
    # 1. Create a temporary directory to copy the new bundle into
    local_temp_bundle_path = tempfile.mkdtemp(dir=BUNDLES_DEST_DIR, prefix='tmp-' + bundle_name + '-', suffix='.download')

    # 2. Make a hard link "copy" of the existing bundle (speeds up rsync)
    if local_old_bundle_path != None and local_old_bundle_path != '':
        sys.stdout.flush()
        result = run_external_program(['cp', '-alT', local_old_bundle_path, local_temp_bundle_path])
        if external_program_encountered_error(result):
            log_error_message('Error copying old bundle "%s" as baseline for new bundle "%s"' % (old_bundle_name, bundle_name))

    # 3. Use rsync to copy over the changes.  Trailing / on remote_bundle_path is critical.
    sys.stdout.flush()
    result = run_external_program(['rsync', '-a', '--delete', remote_bundle_path + '/', local_temp_bundle_path])
    if external_program_encountered_error(result):
        log_error_message('Error downloading bundle "%s"' % bundle_name)

    # 4. Change ownership from bundles to setup_uid:app_gid
    bundle_info = BundleInfo.load_from_file(os.path.join(local_temp_bundle_path, 'config', 'bundle_info.config'))
    recursive_chown_chmod(local_temp_bundle_path, 0, bundle_info.app_gid, '0750')

    # 5. Rename temporary directory to final bundle directory
    try:
        os.rename(local_temp_bundle_path, local_bundle_path)
    except OSError as e:
        # This might happen if another process created the bundle while we
        # were busy.  Assume the bundle is ok--but log a warning!
        log_last_exception('custom_message', 'Warning: error copying downloaded bundle "%s"' % bundle_name)
        # TODO: it would be nice if we could mark the above as a warning.

    return bundle_info

def create_config_files(application_name, bundle_version, bundle_name, bundle_info, resource_allocation):
    bi = bundle_info
    ra = resource_allocation

    # Compute bundle path
    bundle_path = os.path.join(BUNDLES_DEST_DIR, bundle_name)
    config_path = os.path.join(bundle_path, 'config')

    (django_project_parent_path, django_project_module_name) = os.path.split(bi.django_project_path)

    # Remove old config files (if any)
    remove_no_exception(os.path.join(config_path, 'gunicorn.conf'))
    remove_no_exception(os.path.join(config_path, 'runnable.py'))
    remove_no_exception(os.path.join(bi.django_project_path, 'settings.py'))
    remove_no_exception(os.path.join(bi.django_project_path, 'settings/__init__.py'))

    os.umask(0227)

    # Create production settings.py file in <bundle path>/application/.../settings.py
    # (code also exists in master_manager.deploy)
    print 'Creating production settings.py file...',
    if os.path.isdir(os.path.join(bi.django_project_path, 'settings')):
        settings_path = os.path.join(bi.django_project_path, 'settings', '__init__.py')
    else:
        settings_path = os.path.join(bi.django_project_path, 'settings.py')
    generate_config_file('generic_settings', settings_path,
                         user_settings_module_name  = bi.user_settings_module_name,
                         db_host                    = bi.db_host,
                         db_port                    = bi.db_port,
                         db_name                    = bi.db_name,
                         db_username                = bi.db_username,
                         db_password                = bi.db_password,
                         bundle_name                = bundle_name,
                         application_name           = application_name,
                         celery_procs               = ra.celery_procs,
                         debug                      = ra.debug)
    os.chown(settings_path, 0, bi.app_gid)
    os.chmod(settings_path, 0750)
    print 'Done.'
    print ''

    # Create Django WSGI file in <django_project_path>/runnable_<bundle_version>.py
    print 'Generating django wsgi script for your project...',
    django_wsgi_path = os.path.join(config_path, 'runnable_%s.py' % bundle_version)
    if is_nonempty_file(os.path.join(bi.django_project_path, '__init__.py')):
        settings_module = '%s.settings' % os.path.basename(bi.django_project_path)
    else:
        settings_module = 'settings'
    # XXX - Try reenabling RLIMIT_NOFILE in generic_django_wsgi
    generate_config_file('generic_django_wsgi', django_wsgi_path, \
                         django_project_path        = escape(bi.django_project_path), \
                         django_project_parent_path = escape(django_project_parent_path), \
                         application_name           = application_name, \
                         bundle_name                = bundle_name, \
                         rlimit_data                = str(ra.proc_mem_mb - ra.proc_stack_mb), \
                         rlimit_stack               = str(ra.proc_stack_mb), \
                         rlimit_rss                 = str(ra.proc_mem_mb), \
                         rlimit_nproc               = str(ra.proc_num_threads * ra.num_procs), \
                         settings_module            = settings_module)
    os.chown(django_wsgi_path, 0, bi.app_gid)
    os.chmod(django_wsgi_path, 0750)
    print 'Done.'
    print ''

    # Create Gunicorn config file in <bundle path>/config/gunicorn.conf
    print 'Generating gunicorn configuration file...',
    gunicorn_conf_path   = os.path.join(config_path, 'gunicorn.conf')
    generate_config_file('generic_gunicorn_conf', gunicorn_conf_path,
                         application_name           = application_name, \
                         bundle_name                = bundle_name, \
                         web_uid                    = str(bi.web_uid), \
                         app_gid                    = str(bi.app_gid), \
                         num_processes              = str(ra.num_procs), \
                         host                       = ra.host, \
                         port                       = ra.port)
    os.chown(gunicorn_conf_path, 0, bi.app_gid)
    os.chmod(gunicorn_conf_path, 0750)
    print 'Done.'
    print ''

def is_nonempty_file(path):
    if not os.path.isfile(path):
        return False
    return os.stat(path).st_size > 0

def escape(text):
    text1 = re.sub('(\'|\"|\\\\)', '\\\\\\1', text)
    text2 = re.sub('\n', '\\\\n', text1)
    return text2

def remove_no_exception(path):
    try:
        os.remove(path)
    except:
        pass

### Copied from master_manager.deploy ###
def generate_config_file(__template_name__, __config_file_path__, **kwargs):
    """Generate a bundle config file from a template, supplying arguments
    from kwargs."""

    # Load the template
    lookup = TemplateLookup(directories = [WORKER_TEMPLATE_DIR])
    template = lookup.get_template(__template_name__)
    # Instantiate the template
    instance = template.render(**kwargs)
    # Write the instantiated template to the bundle
    f = open(__config_file_path__, 'w')
    f.write(instance)
    f.close()

def relink(src_path, link_path):
    """Equivalent to ln -sf: create a symbolic link, overriding any existing
    target link or file."""
    try:
        os.remove(link_path)
    except OSError as e:
        # Old link didn't exist, not a problem.
        pass
    os.symlink(src_path, link_path)

def create_log_files(bundle_name, web_uid, app_gid):
    """Create the /srv/logs/<bundle_name> directory and initially empty
    django and web server log files."""
    logdir_path = os.path.join(LOGS_DIR, bundle_name)
    try:
        os.mkdir(logdir_path, 0770)
        os.chown(logdir_path, 0, app_gid)
        os.chmod(logdir_path, 0770)
    except OSError as e:
        # Should log this--ok if it's just because the file exists.
        if not os.path.exists(logdir_path):
            log_last_exception('custom_message', 'Error: could not create log directory "%s"' % logdir_path)
            return
    for log_name in LOGS:
        logfile_path = os.path.join(logdir_path, log_name)
        try:
            make_file(logfile_path, 0660)
            os.chown(logfile_path, web_uid, app_gid)
            os.chmod(logfile_path, 0660)
        except OSError as e:
            log_last_exception('custom_message', 'Error: could not create log file "%s"' % logfile_path)

def make_file(path, mode):
    os.close(os.open(path, os.O_CREAT, mode))

if __name__ == '__main__':
    main()
