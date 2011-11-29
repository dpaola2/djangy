#!/usr/bin/env python

from ConfigParser import RawConfigParser
from mako.lookup import TemplateLookup
from shared import *

def main():
    check_trusted_uid(sys.argv[0])
    kwargs = check_and_return_keyword_args(sys.argv, ['application_name'])
    deploy(**kwargs)

def deploy(application_name):
    print ''
    print ''
    print 'Welcome to Djangy!'
    print ''
    print 'Deploying project %s.' % application_name
    print ''

    try:
        bundle_version = create_latest_bundle_via_db(application_name)
        print 'Deploying to worker hosts...',
        call_worker_managers_allocate(application_name)
        call_proxycache_managers_configure(application_name)
        log_info_message("Successfully deployed application '%s'!" % application_name)
        print 'Done.'
        print ''
    except BundleAlreadyExistsException as e:
        log_last_exception()
        print 'WARNING: ' + str(e)
        print 'Commit and push some changes to force redeployment.'
        print ''
    except ApplicationNotInDatabaseException as e:
        log_last_exception()
        print 'ERROR: ' + str(e)
        print ''
    except InvalidApplicationNameException as e:
        log_last_exception()
        print 'ERROR: ' + str(e)
        print ''
    except DjangoProjectNotFoundException as e:
        log_last_exception()
        print 'ERROR: No django project found in the git repository.'
        print ''
    except:
        log_last_exception()
        print 'Internal error, please contact support@djangy.com'
        print ''

def create_latest_bundle_via_db(application_name):
    """Create a bundle from the latest version of an application.  Fetches
    details like administrative email address and database credentials from
    the management database."""

    check_application_name(application_name)

    # Extract application info from management database
    try:
        application_info = Application.get_by_name(application_name)
        user_info        = application_info.account
        bundle_params = {
            'application_name': application_name,
            'admin_email'     : user_info.email,
            'db_host'         : application_info.db_host,
            'db_port'         : application_info.db_port,
            'db_name'         : application_info.db_name,
            'db_username'     : application_info.db_username,
            'db_password'     : application_info.db_password,
            'setup_uid'       : application_info.setup_uid,
            'web_uid'         : application_info.web_uid,
            'cron_uid'        : application_info.cron_uid,
            'app_gid'         : application_info.app_gid,
            'celery_procs'    : application_info.celery_procs,
        }
        # Also need to query DB for which hosts to run on; and
        # resource allocations may be heterogenous across hosts
        check_setup_uid(bundle_params['setup_uid'])
        check_web_uid  (bundle_params['web_uid'  ])
        check_cron_uid (bundle_params['cron_uid' ])
        check_app_gid  (bundle_params['app_gid'  ])
    except Exception as e:
        log_last_exception()
        print str(e)
        # Couldn't find application_name in the management database!
        raise ApplicationNotInDatabaseException(application_name)

    # Create the bundle.
    bundle_version = create_latest_bundle(**bundle_params)

    # Update latest bundle version in the database.
    application_info.bundle_version = bundle_version
    application_info.save()

    return bundle_version

def create_latest_bundle(application_name, admin_email, db_host, db_port, db_name, db_username, db_password, \
                         setup_uid, web_uid, cron_uid, app_gid, celery_procs):
    """Create a bundle from the latest version of an application.  Requires
    administrative email address and database credentials as arguments."""

    # Put application code in <bundle path>/application
    # and user-supplied config files in <bundle path>/config
    print 'Cloning git repository...',
    (bundle_version, bundle_name, bundle_application_path) = clone_repo_to_bundle(application_name)
    print 'Done.'
    print ''

    bundle_path = os.path.join(BUNDLES_DIR, bundle_name)
    recursive_chown_chmod(bundle_path, 0, app_gid, '0750')

    # Find the Django project directory
    django_project_path = find_django_project(os.path.join(bundle_path, 'application'))
    django_project_module_name = os.path.basename(django_project_path)

    # Rename the user's settings module to something that's unlikely to conflict
    if os.path.isfile(os.path.join(django_project_path, 'settings', '__init__.py')):
        user_settings_module_name = '__init__%s' % bundle_version
        os.rename(os.path.join(django_project_path, 'settings', '__init__.py'), \
                  os.path.join(django_project_path, 'settings', user_settings_module_name + '.py'))
    elif os.path.isfile(os.path.join(django_project_path, 'settings.py')):
        user_settings_module_name = 'settings_%s' % bundle_version
        os.rename(os.path.join(django_project_path, 'settings.py'), \
                  os.path.join(django_project_path, user_settings_module_name + '.py'))

    # Create production settings.py file in <bundle path>/application/.../settings.py
    # (code also exists in worker_manager.deploy)
    print 'Creating production settings.py file...',
    if os.path.isdir(os.path.join(django_project_path, 'settings')):
        settings_path = os.path.join(django_project_path, 'settings', '__init__.py')
    else:
        settings_path = os.path.join(django_project_path, 'settings.py')
    generate_config_file('generic_settings', settings_path,
                         user_settings_module_name  = user_settings_module_name,
                         django_project_module_name = django_project_module_name,
                         db_host                    = db_host,
                         db_port                    = db_port,
                         db_name                    = db_name,
                         db_username                = db_username,
                         db_password                = db_password,
                         bundle_name                = bundle_name,
                         debug                      = False,
                         celery_procs               = None,
                         application_name           = application_name)
    os.chown(settings_path, 0, app_gid)
    os.chmod(settings_path, 0750)
    print 'Done.'
    print ''

    # The create_virtualenv.py program calls setuid() to run as setup_uid
    python_virtual_path = os.path.join(bundle_path, 'python-virtual')
    os.mkdir(python_virtual_path, 0770)
    os.chown(python_virtual_path, 0, app_gid)
    os.chmod(python_virtual_path, 0770)
    sys.stdout.flush()
    run_external_program([PYTHON_BIN_PATH, os.path.join(MASTER_MANAGER_SRC_DIR, 'uid_application_setup/create_virtualenv.py'), \
        'application_name', application_name, 'bundle_name', bundle_name, \
        'setup_uid', str(setup_uid), 'app_gid', str(app_gid)], \
        pass_stdout=True, cwd=bundle_application_path)

    os.umask(0227)

    # Save the bundle info used by worker_manager to generate config files
    print 'Saving bundle info...',
    django_admin_media_path = get_django_admin_media_path(bundle_path)
    admin_media_prefix='/admin_media'
    BundleInfo( \
        django_project_path       = django_project_path, \
        django_admin_media_path   = django_admin_media_path, \
        admin_media_prefix        = admin_media_prefix, \
        admin_email               = admin_email, \
        setup_uid                 = setup_uid, \
        web_uid                   = web_uid, \
        cron_uid                  = cron_uid, \
        app_gid                   = app_gid, \
        user_settings_module_name = user_settings_module_name, \
        db_host                   = db_host, \
        db_port                   = db_port, \
        db_name                   = db_name, \
        db_username               = db_username, \
        db_password               = db_password
        ).save_to_file(os.path.join(bundle_path, 'config', 'bundle_info.config'))
    print 'Done.'
    print ''

    recursive_chown_chmod(bundle_path, 0, app_gid, '0750')
    # TODO: don't chmod everything +x, only what needs it.

    return bundle_version

### Also exists in worker_manager.deploy ###
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

def get_django_admin_media_path(bundle_path):
    try:
        # Currently assumes python2.6
        f = open(os.path.join(bundle_path, 'python-virtual/lib/python2.6/site-packages/easy-install.pth'))
        contents = f.read()
        f.close()
        django_path = re.search('^(.*/Django-.*\.egg)$', contents, flags=re.MULTILINE).group(0)
        admin_media_path = os.path.join(django_path, 'django/contrib/admin/media')
        return admin_media_path
    except:
        return os.path.join(bundle_path, 'directory_that_does_not_exist')

def clone_repo_to_bundle(application_name):
    """Try to clone an application's git repository and put the latest code
    into a new bundle.  Throws BundleAlreadyExistsException if a bundle
    directory already exists for the latest version in the repository."""

    # Create temporary directory in which to git clone
    master_repo_path = os.path.join(REPOS_DIR, application_name + '.git')
    temp_repo_path = tempfile.mkdtemp('.git', 'tmp-', BUNDLES_DIR)
    os.chown(temp_repo_path, GIT_UID, GIT_UID)
    os.chmod(temp_repo_path, 0700)
    # git clone and read current version of git repository
    result = run_external_program([PYTHON_BIN_PATH, os.path.join(MASTER_MANAGER_SRC_DIR, 'uid_git/clone_repo.py'), master_repo_path, temp_repo_path])
    stdout = result['stdout_contents'].split('\n')
    if len(stdout) < 1:
        git_repo_version = ''
    else:
        git_repo_version = stdout[0]
    # Validate git_repo_version
    if result['exit_code'] != 0 or not validate_git_repo_version(git_repo_version):
        raise GitCloneException(application_name, temp_repo_path)
    # Compute bundle path
    bundle_version = BUNDLE_VERSION_PREFIX + git_repo_version
    bundle_name = application_name + '-' + bundle_version
    bundle_path = os.path.join(BUNDLES_DIR, bundle_name)
    # Check if bundle already exists
    if os.path.exists(bundle_path):
        shutil.rmtree(temp_repo_path)
        raise BundleAlreadyExistsException(bundle_name)
    # Make bundle directory
    bundle_config_path = os.path.join(bundle_path, 'config')
    os.makedirs(bundle_config_path)
    os.chmod(bundle_path, 0700)
    # Move checked-out repo to bundle
    bundle_application_path = get_bundle_application_path(application_name, temp_repo_path, bundle_path)
    os.makedirs(bundle_application_path)
    os.rename(temp_repo_path, bundle_application_path)
    # Copy the user-supplied configuration files to a deterministic location
    copy_normal_file(os.path.join(bundle_application_path, 'djangy.config'), os.path.join(bundle_config_path, 'djangy.config'))
    copy_normal_file(os.path.join(bundle_application_path, 'djangy.eggs'  ), os.path.join(bundle_config_path, 'djangy.eggs'  ))
    copy_normal_file(os.path.join(bundle_application_path, 'djangy.pip'   ), os.path.join(bundle_config_path, 'djangy.pip'   ))
    # Remove .git history which is not relevant in bundle
    shutil.rmtree(os.path.join(bundle_application_path, '.git'))
    # Note: bundle permissions must be adjusted by caller
    return (bundle_version, bundle_name, bundle_application_path)

def validate_git_repo_version(git_repo_version):
    return (None != re.match('^[0-9a-f]{40}$', git_repo_version))

def get_bundle_application_path(application_name, repo_path, bundle_path):
    """Given the path to a copy of the code for an application and the path
    to the bundle in which it needs to be inserted, determine the path where
    the code needs to be moved to.  The simple case is
    (bundle_path)/application/(application_name), but if the user provides a
    djangy.config file in the root of the repository, they can override
    that, e.g., (bundle_path)/application/mydir"""
    # Default: (bundle_path)/application/(application_name)
    bundle_application_path = os.path.join(bundle_path, 'application', application_name)
    # But if djangy.config file exists, look for:
    #     [application]
    #     rootdir=(some directory)
    djangy_config_path = os.path.join(repo_path, 'djangy.config')
    if is_normal_file(djangy_config_path):
        parser = RawConfigParser()
        parser.read(djangy_config_path)
        try:
            # Normalize the path relative to a hypothetical root directory,
            # then remove the leftmost / to make the path relative again.
            rootdir = os.path.normpath(os.path.join('/', parser.get('application', 'rootdir')))[1:]
            # Put the path inside the bundle's application directory;
            # normalizing will remove a rightmost / if rootdir == ''
            bundle_application_path = os.path.normpath(os.path.join(bundle_path, 'application', rootdir))
        except:
            pass
    return bundle_application_path

def is_normal_file(path):
    return not os.path.islink(path) and os.path.isfile(path)

def copy_normal_file(src_path, dest_path):
    if is_normal_file(src_path) and \
    not os.path.exists(dest_path):
        shutil.copyfile(src_path, dest_path)

if __name__ == '__main__':
    main()
