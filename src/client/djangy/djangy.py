#! /usr/bin/env python

import getpass, os, re, socket, subprocess, sys, urllib, urllib2, xmlrpclib, platform
from hashlib import md5
from pkg_resources import parse_version
from find_git_repository import *
from ConfigParser import RawConfigParser
try:
    import json
except ImportError:
    import simplejson as json

GIT_HOST = 'api.djangy.com'
API_BASE_URL = 'https://api.djangy.com'
VERSION = '0.14'

HOME = None
if platform.system() == 'Windows':
    HOME = os.environ['USERPROFILE']
else:
    HOME = os.environ['HOME']
CONFIG_PATH = os.path.join(HOME, '.djangy')

COMMANDS = [
    'create',
    'logs',
    'manage.py',
]

HELP_MESSAGE = """ Djangy Commands:
                                # NOTE: all commands accept
                                # the [-a app_name] argument:
                                # $ djangy -a myproject create

djangy create                   # create a new djangy application

djangy manage.py <command>      # remotely execute manage.py command
djangy manage.py syncdb
djangy manage.py migrate
djangy manage.py shell

djangy logs                     # display recent log output (last 100 lines)
djangy help                     # display this message

# Example:

    django-startproject myproject
    cd myproject
    git init
    git add .
    git commit -m "my new project"
    djangy create
    git push djangy master

# http://www.djangy.com/docs/ | support@djangy.com
"""

#### Update checker ####

def check_for_update():
    try:
        socket.setdefaulttimeout(2) # 2 second default timeout
        client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
        version = client.package_releases('Djangy')[0]
        if parse_version(version) > parse_version(VERSION):
            print ''
            print 'Warning: There is an updated version of djangy available.'
            print '         Run easy_install -U Djangy to update.'
            print ''
    except Exception, e:
        print ''
        print 'Warning: Connection to pypi.python.org timed out, so we'
        print '         couldn\'t check if your djangy client is up-to-date.'
        print ''
        pass
    finally:
        socket.setdefaulttimeout(None)

#### Basic input ####

def prompt(text, blank_line=True):
    print ''
    print text + ' ',
    response = sys.stdin.readline().strip('\n')
    if blank_line:
        print ''
    return response

#### Communication with the API server ####

def request(command, email_address = None, hashed_password = None, pubkey = None, application_name = None, args = ' '):
    if not command in COMMANDS:
        print 'Invalid command.'
        sys.exit(1)
    data = {}
    if application_name: data['application_name'] = application_name
    if email_address: data['email'] = email_address
    if args: data['args'] = json.dumps(args)
    if pubkey: data['pubkey'] = pubkey
    if hashed_password: data['hashed_password'] = hashed_password
    url_values = urllib.urlencode(data)
    req = urllib2.Request('%s/%s' % (API_BASE_URL, command), url_values)
    try:
        response = urllib2.urlopen(req)
        print response.read()
        return True
    except urllib2.HTTPError as error:
        if error.code == 403:
            yn = prompt('Authentication error: would you like to re-enter your credentials (y/n)?')[0]
            if yn == 'y' or yn == 'Y':
                os.remove(CONFIG_PATH)
                set_retry()
            else:
                sys.exit(1)
        else:
            print error.read()
            sys.exit(1)
        return False

#### Git repository ####

def get_git_repository(command):
    try:
        git_repo_root = find_git_repository(os.getcwd())
        print 'Using git repository "%s"' % git_repo_root
        return git_repo_root
    except GitRepositoryNotFoundException as e:
        print 'Please run "djangy %s" from within a valid git repository.' % command
        sys.exit(1)

#### Application name ####

def validate_application_name(application_name):
    return re.match('^[A-Za-z][A-Za-z0-9]{4,14}$', application_name) != None

def warn_invalid_application_name(application_name):
    print 'Invalid application name "%s", please try again.' % application_name
    print 'Application name must be 5-15 characters long, A-Z a-z 0-9, starting with a letter.'

def ask_for_application_name():
    while True:
        application_name = prompt('Please enter your application name [Enter for %s]:' % os.path.basename(os.getcwd()))
        if application_name == '':
            # If the user just hit enter, default to the name of the git repo
            application_name = os.path.basename(os.getcwd())
        if validate_application_name(application_name):
            return application_name
        else:
            warn_invalid_application_name(application_name)

def load_application_name():
    parser = RawConfigParser()
    parser.read('djangy.config')
    try:
        return parser.get('application', 'application_name')
    except:
        return None

def save_application_name(application_name):
    # Only actually save if djangy.config doesn't exist.  We don't want to
    # potentially mess up a user-customized file.
    if not os.path.exists('djangy.config'):
        f = open('djangy.config', 'w')
        f.write('[application]\napplication_name=%s\nrootdir=%s\n' \
            % (application_name, os.path.basename(os.getcwd())))
        f.close()
        return True
    elif load_application_name() != application_name:
        print 'Warning: please update application_name in "%s"' % os.path.abspath('djangy.config')
        return False

def print_application_name(application_name, source_of_application_name):
    print 'Using application name "%s" from %s' % (application_name, source_of_application_name)

def get_application_name(application_name_arg=None, application_name_retry=None, write_djangy_config=True):
    if application_name_arg != None:
        application_name = application_name_arg
        print_application_name(application_name, '-a option')
        if not validate_application_name(application_name):
            warn_invalid_application_name(application_name)
            sys.exit(1)
        if write_djangy_config:
            save_application_name(application_name)
        return application_name
    application_name = load_application_name()
    if application_name != None:
        print_application_name(application_name, '"%s"' % os.path.abspath('djangy.config'))
        if not validate_application_name(application_name):
            warn_invalid_application_name(application_name)
            sys.exit(1)
    else:
        if application_name_retry != None:
            # We're retrying due to authentication failure, but the user
            # already entered an application name
            application_name = application_name_retry
        else:
            application_name = ask_for_application_name()
        print_application_name(application_name, 'user input')
        if write_djangy_config:
            save_application_name(application_name)
    return application_name


#### User credentials: email address and password ####

def validate_email_address(email_address):
    return re.match('^.+\\@[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,6}|[0-9]{1,3})$', email_address) != None

def ask_for_email_address():
    num_failures = 0
    while True:
        email_address = prompt('Enter your email address:', blank_line=False)
        if validate_email_address(email_address):
            return email_address
        else:
            num_failures = num_failures + 1
            print 'Invalid email address, please try again.'
            if num_failures > 1:
                print '(or email support@djangy.com if "%s" is correct.)' % email_address

def ask_for_password(email_address):
    hashed_password = md5('%s:%s' % (email_address, getpass.getpass('Please enter your password: '))).hexdigest()
    print ''
    return hashed_password

def ask_for_credentials():
    email_address = ask_for_email_address()
    hashed_password = ask_for_password(email_address)
    return (email_address, hashed_password)

def load_credentials():
    data = [d.strip('\n') for d in open(CONFIG_PATH).readlines()]
    if len(data) != 2:
        return None
    email_address = data[0]
    if not validate_email_address(email_address):
        return None
    hashed_password = data[1]
    return (email_address, hashed_password)

def save_credentials(email_address, hashed_password):
    f = open(CONFIG_PATH, 'w')
    f.write('%s\n%s' % (email_address, hashed_password))
    f.close()
    print 'Saved credentials.'
    print 'To change your email address or password, remove "%s"' % CONFIG_PATH

def get_credentials():
    try:
        return load_credentials()
    except:
        (email_address, hashed_password) = ask_for_credentials()
        save_credentials(email_address, hashed_password)
        return (email_address, hashed_password)

#### User public key ####

def validate_pubkey(pubkey_path):
    if os.path.isfile(pubkey_path):
        return True
    return False

def get_pubkey():
    # try to find public key path
    pubkey_path = None
    if os.path.exists('%s/.ssh/id_rsa.pub' % HOME):
        pubkey_path = '%s/.ssh/id_rsa.pub' % HOME
    else:
        is_valid_pubkey = False
        while not is_valid_pubkey:
            pubkey_path = os.path.abspath(prompt('Please enter the path to your ssh public key:'))
            if validate_pubkey(pubkey_path):
                is_valid_pubkey = True
            else:
                print 'Unable to locate ssh public key at path "%s"' % pubkey_path
    print 'Using public key file "%s"' % pubkey_path
    return open(pubkey_path).read()

#### Commands ####

_retry = True

def run_command(command, application_name_arg, args):
    global _retry
    application_name = application_name_arg
    while _retry:
        _retry = False
        email_address, hashed_password = get_credentials()
        application_name = get_application_name(application_name_arg=application_name_arg, \
            application_name_retry=application_name, write_djangy_config=(command != 'create'))
        if command == 'create':
            create(application_name, email_address, hashed_password)
        elif command == 'manage.py':
            manage_py(application_name, email_address, hashed_password, args)
        else:
            simple_command(command, application_name, email_address, hashed_password)

def set_retry():
    global _retry
    _retry = True

def create(application_name, email_address, hashed_password):
    pubkey = get_pubkey()
    if request('create', application_name = application_name, email_address = email_address, hashed_password = hashed_password, pubkey = pubkey):
        init_default_files(application_name)
        init_git_remote(application_name)

def init_default_files(application_name):
    files_created = []
    if os.path.exists('djangy.config'):
        if load_application_name() != application_name:
            print 'Please update application_name in "%s"' % os.path.abspath('djangy.config')
    else:
        if save_application_name(application_name):
            files_created.append('djangy.config')
    if not os.path.exists('djangy.eggs'):
        f = open('djangy.eggs', 'w')
        f.write('Django\nSouth\n')
        f.close()
        files_created.append('djangy.eggs')
    if not os.path.exists('djangy.pip'):
        f = open('djangy.pip', 'w')
        f.write('')
        f.close()
        files_created.append('djangy.pip')
    if len(files_created) > 0:
        n = len(files_created)
        git_add_and_commit(files_created)

def format_and_list(list, when_empty=''):
    list = map(lambda x: '"%s"' % x, list)
    if len(list) > 0:
        if len(list) == 1:
            return list[0]
        else:
            return (', '.join(list[:-1]) + ' and ' + list[-1])
    else:
        return when_empty

def singular_plural(n, singular, plural):
    if n > 1:
        return plural
    else:
        return singular

def init_git_remote(application_name):
    """Add the "djangy" remote"""
    subprocess.call(['git remote add djangy git@%s:%s.git > /dev/null 2>&1' % (GIT_HOST, application_name)], shell=True)
    print ""
    print 'You can now run "git push djangy master"'

def git_add_and_commit(files):
    if len(files) < 1:
        return False
    status = subprocess.call(['git', 'add'] + files)
    if status == 0:
        status = subprocess.call(['git', 'commit', '-m', 'added %s to repository' % format_and_list(files)])
        if status == 0:
            return True
    return False

def manage_py(application_name, email_address, hashed_password, args):
    print ""
    command = "ssh -oPasswordAuthentication=no shell@api.djangy.com %s manage.py %s" % (application_name, " ".join(args))
    os.system(command)

def simple_command(command, application_name, email_address, hashed_password):
    request(command, application_name = application_name, email_address = email_address, hashed_password = hashed_password)

#### Main ####

def main():
    # Parse command line arguments
    command = ''
    application_name = None
    args = sys.argv[1:]
    try:
        if args[0][0:2] == '-a':
            application_name = args[0][2:]
            if application_name != '':
                args = args[1:]
            else:
                application_name = args[1]
                args = args[2:]
        command = args[0]
        args    = args[1:]
    except:
        pass

    if command in COMMANDS:
        check_for_update()
        # Go to the root directory of the repository so that any files we
        # create are stored at the root level, and so the djangy.config and
        # djangy.eggs files can be created with the right contents/location.
        os.chdir(get_git_repository(command));
        run_command(command, application_name, args)
    elif command == 'help':
        print HELP_MESSAGE
    else:
        print HELP_MESSAGE
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
