#!/usr/bin/env python
#
# Runs virtualenv create commands as an application setup UID.  This program
# is called as root, and then sets its own UID.  This allows us to protect
# the create_virtualenv.py script from end-user code.
#

from djangy_server_shared import *

def main():
    kwargs = check_and_return_keyword_args(sys.argv, ['application_name', 'bundle_name', 'setup_uid', 'app_gid'])
    become_application_setup_uid_gid(sys.argv[0], int(kwargs['setup_uid']), int(kwargs['app_gid']))
    os.umask(0027)
    os.environ['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
    del os.environ['VIRTUAL_ENV']
    create_virtualenv(**kwargs)

def create_virtualenv(application_name, bundle_name, setup_uid, app_gid):
    if os.getuid() == 0 or os.getuid() != int(setup_uid):
        print 'ERROR: setup_bundle must be run as setup_uid'
        sys.exit(2)

    bundle_path = os.path.join(BUNDLES_DIR, bundle_name)

    # Create virtualenv in <bundle path>/python-virtual
    print 'Installing dependencies...\n',
    virtualenv_path = os.path.join(bundle_path, 'python-virtual')
    generate_virtual_environment(bundle_path, virtualenv_path)
    print 'Done.'
    print ''

def generate_virtual_environment(bundle_path, virtualenv_path):
    # Create the virtualenv
    sys.stdout.flush()
    run_external_program(['virtualenv', virtualenv_path])
    # Install eggs using easy_install
    easy_install_eggs(bundle_path, virtualenv_path)
    # Install other required python packages using pip
    pip_install_requirements(bundle_path, virtualenv_path)

def easy_install_eggs(bundle_path, virtualenv_path):
    print '  Dependencies from djangy.eggs using easy_install:'
    # read the djangy.eggs file (if it exists) and install all the packages mentioned
    deps_path = os.path.join(bundle_path, 'config', 'djangy.eggs')
    deps = []
    if os.path.exists(deps_path):
        deps = [d.strip('\n') for d in open(deps_path, 'r').readlines()]
    elif not os.path.exists(os.path.join(bundle_path, 'config', 'djangy.pip')):
        deps = ['Django', 'South']
    if 'gunicorn' not in deps:
        deps += ['gunicorn']
    easy_install = os.path.join(virtualenv_path, 'bin', 'easy_install')
    install_deps([easy_install, '-Z'], deps)

def pip_install_requirements(bundle_path, virtualenv_path):
    print '  Dependencies from djangy.pip using pip:'
    # read the djangy.pip file (if it exists) and install all the packages mentioned
    deps_path = os.path.join(bundle_path, 'config', 'djangy.pip')
    if os.path.exists(deps_path):
        deps = [d.strip('\n') for d in open(deps_path, 'r').readlines()]
    else:
        deps = []
    pip_path = os.path.join(virtualenv_path, 'bin', 'pip')
    install_deps([pip_path, 'install'], deps)

def install_deps(install_command, deps):
    sys.stdout.flush()
    num_deps = 0
    for dep in deps:
        # Get the raw dependency, no comment.
        dep = dep.strip()
        # Install the dependency, but skip blank or comment lines
        if dep != '' and dep[0] != '#':
            num_deps = num_deps + 1
            print '    Installing %s...' % dep,
            sys.stdout.flush()
            result = run_external_program(install_command + dep.split())
            if result['exit_code'] == 0:
                print 'Success.'
            else:
                print 'FAILED!'
    if num_deps == 0:
        print '    None found.'
    sys.stdout.flush()

if __name__ == '__main__':
    main()
