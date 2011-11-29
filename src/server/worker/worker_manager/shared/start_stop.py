from shared import *
from socket import gethostname
import os, sys, pwd

def start_application(application_name):
    # Set the started status in the local database
    application_info = LocalApplication.objects.get(application_name=application_name)
    application_info.is_stopped = False
    application_info.save()
    # Start the application in gunicorn
    bundle_version = application_info.bundle_version
    bundle_name = application_name + "-" + bundle_version
    bundle_path = os.path.join('/srv/bundles', bundle_name)
    config_path = os.path.join(bundle_path, 'config')
    virtualenv_path = os.path.join(bundle_path, 'python-virtual')
    bundle_info = BundleInfo.load_from_file(os.path.join(config_path, 'bundle_info.config'))
    def become_web_uid():
        os.environ.clear()
        os.environ['PATH'] = '%s:/usr/bin:/bin' % os.path.join(virtualenv_path, 'bin')
        os.environ['VIRTUAL_ENV'] = virtualenv_path
        os.chdir(config_path)
        os.setgid(bundle_info.app_gid)
        os.setuid(bundle_info.web_uid)
    def become_cron_uid():
        os.environ.clear()
        os.environ['PATH'] = '%s:/usr/bin:/bin' % os.path.join(virtualenv_path, 'bin')
        os.environ['VIRTUAL_ENV'] = virtualenv_path
        os.chdir(bundle_info.django_project_path)
        os.setgid(bundle_info.app_gid)
        os.setuid(bundle_info.cron_uid)
    # Start gunicorn process
    sys.stdout.flush()
    run_external_program(['gunicorn', '-c', os.path.join(config_path, 'gunicorn.conf'), 'runnable_%s:application' % bundle_version], \
        cwd = config_path, \
        preexec_fn = become_web_uid)
    try:
        celery_procs = int(application_info.celery_procs)
        # only start celery if there is more than one process being allocated
        assert celery_procs > 0
    except:
        return
    pid = os.fork()
    if pid == 0:
        # child process
        os.closerange(1, 1024)
        become_cron_uid()
        hostname = "%s.%s" % (application_name, gethostname())
        os.execvp('python', [
            'python', 
            os.path.join(bundle_info.django_project_path, 'manage.py'), 
            'celeryd', 
            '-n', hostname, 
        ])


def stop_application(application_name):
    # Set the stopped status in the local database
    application_info = LocalApplication.objects.get(application_name=application_name)
    if application_info.is_stopped:
        return False
    application_info.is_stopped = True
    application_info.save()
    if not application_info.bundle_version:
        # There is no current running version
        return True
    try:
        bundle_name = application_name + "-" + application_info.bundle_version
        bundle_path = os.path.join('/srv/bundles', bundle_name)
        config_path = os.path.join(bundle_path, 'config')
        bundle_info = BundleInfo.load_from_file(os.path.join(config_path, 'bundle_info.config'))
        # Stop the running gunicorn process
        web_user = pwd.getpwuid(int(bundle_info.web_uid)).pw_name
        cron_user = pwd.getpwuid(int(bundle_info.cron_uid)).pw_name
        # send SIGKILL
        sys.stdout.flush()
        run_external_program(['killall', '-s', 'SIGKILL', '-u', str(web_user)])
        run_external_program(['killall', '-s', 'SIGKILL', '-u', str(cron_user)])
    except:
        # Database had a stale entry
        log_last_exception()
    return True
