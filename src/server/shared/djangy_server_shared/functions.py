import binascii, os, re, sys
from constants import *
from exceptions import *
from json_log import *
from run_external_program import *

def may_not_be_run_as(program_name, uid, gid):
    print_or_log_usage('%s may not be run by uid %i gid %i' % (program_name, uid, gid))
    sys.exit(1)

def check_trusted_uid(program_name):
    if not os.getuid() in TRUSTED_UIDS:
        may_not_be_run_as(program_name, os.getuid(), os.getgid())
    set_uid_gid(0, 0)

def check_setup_uid(setup_uid):
    if setup_uid < 100000 \
    or (setup_uid - 100000) % 3 != 0:
        raise CheckApplicationUidGidException('setup_uid', setup_uid)

def check_web_uid(web_uid):
    if web_uid < 100000 \
    or (web_uid - 100000) % 3 != 1:
        raise CheckApplicationUidGidException('web_uid', web_uid)

def check_cron_uid(cron_uid):
    if cron_uid < 100000 \
    or (cron_uid - 100000) % 3 != 2:
        raise CheckApplicationUidGidException('cron_uid', cron_uid)

def check_app_gid(app_gid):
    if app_gid < 100000 \
    or (app_gid - 100000) % 3 != 0:
        raise CheckApplicationUidGidException('app_gid', app_gid)

def become_application_setup_uid_gid(program_name, setup_uid, app_gid):
    try:
        check_setup_uid(setup_uid)
        check_app_gid(app_gid)
        set_uid_gid(setup_uid, setup_uid)
    except Exception as e:
        may_not_be_run_as(program_name, setup_uid, app_gid)

def become_uid_gid(program_name, uid, gid, groups=[]):
    try:
        set_uid_gid(uid, gid, groups)
    except Exception as e:
        may_not_be_run_as(program_name, os.getuid(), os.getgid())

def check_positional_args(args, expected_num_args, help_string):
    if len(args) != expected_num_args+1:
        print_or_log_usage('Usage: %s %s' % (args[0], help_string))
        sys.exit(1)

def check_and_return_keyword_args(args, required_keys, optional_keys=None):
    try:
        return arg_list_to_dict(args[1:], required_keys, optional_keys)
    except ArgumentException as e:
        required_keys_message = ' '.join(map(lambda key: key + ' <x>', required_keys))
        if optional_keys:
            optional_keys_message = ' '.join(map(lambda key: '[%s <x>]' % key, optional_keys))
            print_or_log_usage('Usage: %s %s %s' % (args[0], required_keys_message, optional_keys_message))
        else:
            print_or_log_usage('Usage: %s %s' % (args[0], required_keys_message))
        sys.exit(1)

def arg_list_to_dict(args, required_keys, optional_keys=None):
    """Converts a list of alternating key-value pairs to a dictionary. 
    Checks that the dictionary keys are equal to a given list of expected
    keys."""
    dict = {}
    required_keys_used = []
    if optional_keys:
        allowed_keys = required_keys + optional_keys
    else:
        allowed_keys = required_keys
    for i in range(0, len(args)/2*2, 2):
        key   = args[i]
        value = args[i+1]
        if dict.has_key(key):
            raise RepeatedArgumentException()
        if not key in allowed_keys:
            raise UnexpectedArgumentException(key)
        dict[key] = value
        if key in required_keys:
            required_keys_used.append(key)
    if sort(required_keys_used) != sort(required_keys):
        raise MissingArgumentException()
    return dict

def sort(list):
    sorted_list = list + []
    sorted_list.sort()
    return sorted_list

def set_uid_gid(uid, gid, groups=[]):
    os.setgid(gid)
    os.setegid(gid)
    os.setgroups(groups)
    os.setuid(uid)
    os.seteuid(uid)
    if os.getgid() != gid or os.getegid() != gid \
    or os.getuid() != uid or os.geteuid() != uid \
    or (os.getgroups() != [] and os.getgroups != [gid]):
        raise SetUidGidFailedException()

# Validation for djangy projects/applications
def is_valid_application_name(application_name):
    return (re.match('^[A-Za-z][A-Za-z0-9]*$', application_name) != None)

def check_application_name(application_name):
    if not is_valid_application_name(application_name):
        raise InvalidApplicationNameException()

# Validation for django apps within a djangy project/application
def is_valid_django_app_name(django_app_name):
    return (re.match('^[A-Za-z_][A-Za-z0-9_]*$', django_app_name) != None)

def recursive_chown_chmod(bundle_path, uid, gid, mode):
    # Make sure we're not changing BUNDLES_DIR itself!
    if bundle_path.strip(' /') == '':
        raise InvalidBundleException()
    # chown/chmod bundle to setup_uid
    run_external_program(['chown', '-R', str(uid) + ':' + str(gid), bundle_path], cwd=bundle_path)
    run_external_program(['chmod', '-R', mode, bundle_path], cwd=bundle_path)

def gen_password():
    """ Generate a random 24-character password. """
    password1 = binascii.b2a_base64(os.urandom(9))[:-1]
    password2 = binascii.b2a_base64(os.urandom(9))[:-1]
    if len(password1) != 12 or len(password2) != 12 or password1 == password2:
        raise PasswordGenerationException()
    return password1 + password2
