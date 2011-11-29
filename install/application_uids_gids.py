import re
from core import *

_UID_GID_BASE = 100000

def _is_application_uid(uid):
    return (uid >= _UID_GID_BASE)

_username_regex = re.compile('^([swc])([1-9][0-9]*)$')

def _assert_valid_application_user(username, uid, gid, homedir, shell):
    match = _username_regex.match(username)
    user_type = match.group(1)
    n = int(match.group(2))
    if user_type == 's':
        assert uid == _setup_uid(n)
    elif user_type == 'w':
        assert uid == _web_uid(n)
    elif user_type == 'c':
        assert uid == _cron_uid(n)
    else:
        assert False
    assert gid     == _application_gid(n)
    assert homedir == '/'
    assert shell   == '/bin/sh'

def _setup_uid(n):
    return 3*(n-1) + _UID_GID_BASE

def _web_uid(n):
    return _setup_uid(n) + 1

def _cron_uid(n):
    return _setup_uid(n) + 2

def _is_application_gid(gid):
    return (gid >= _UID_GID_BASE)

_groupname_regex = re.compile('^g([1-9][0-9]*)$')

def _assert_valid_application_group(groupname, gid, member_usernames):
    n = int(_groupname_regex.match(groupname).group(1))
    assert gid == _application_gid(n)
    assert member_usernames == set(['www-data'])

def _application_gid(n):
    return 3*(n-1) + _UID_GID_BASE

def _get_existing_application_uids():
    file = open('/etc/passwd', 'r')
    existing_application_uids = set()
    for line in file.readlines():
        try:
            line = line[:-1]
            (username, x, uid, gid, description, homedir, shell) = line.split(':')
            uid = int(uid)
            gid = int(gid)
            if _is_application_uid(uid):
                _assert_valid_application_user(username, uid, gid, homedir, shell)
                existing_application_uids.add(uid)
            else:
                assert None == _username_regex.match(username)
        except ValueError:
            print 'malformed /etc/passwd entry "%s"' % line
    file.close()
    return existing_application_uids

def _get_existing_application_gids():
    file = open('/etc/group', 'r')
    existing_application_groups = set()
    for line in file.readlines():
        try:
            line = line[:-1]
            (groupname, x, gid, member_usernames) = line.split(':')
            gid = int(gid)
            if _is_application_gid(gid):
                _assert_valid_application_group(groupname, gid, set(member_usernames.split(',')))
                existing_application_groups.add(gid)
            else:
                assert None == _groupname_regex.match(groupname)
        except ValueError:
            print 'malformed /etc/group entry "%s"' % line
    file.close()
    return existing_application_groups

# Returns (etc_passwd_entries, etc_shadow_entries, etc_group_entries)
def _get_application_entries():
    existing_application_uids = _get_existing_application_uids()
    existing_application_gids = _get_existing_application_gids()
    etc_passwd_entries = []
    etc_shadow_entries = []
    etc_group_entries  = []
    for n in range(1, 20000+1):
        gid       = _application_gid(n)
        setup_uid = _setup_uid(n)
        web_uid   = _web_uid(n)
        cron_uid  = _cron_uid(n)
        if setup_uid not in existing_application_uids:
            etc_passwd_entries.append('s%i:x:%i:%i::/:/bin/sh' % (n, setup_uid, gid))
            etc_shadow_entries.append('s%i:*:0:0:99999:7:::' % n)
        if web_uid not in existing_application_uids:
            etc_passwd_entries.append('w%i:x:%i:%i::/:/bin/sh' % (n, web_uid,   gid))
            etc_shadow_entries.append('w%i:*:0:0:99999:7:::' % n)
        if cron_uid not in existing_application_uids:
            etc_passwd_entries.append('c%i:x:%i:%i::/:/bin/sh' % (n, cron_uid,  gid))
            etc_shadow_entries.append('c%i:*:0:0:99999:7:::' % n)
        if gid not in existing_application_gids:
            etc_group_entries.append('g%i:x:%i:www-data' % (n, gid))
    return (etc_passwd_entries, etc_shadow_entries, etc_group_entries)

def _file_append_entries(file_path, entries):
    if len(entries) > 0:
        print "Adding %i entries to %s" % (len(entries), file_path)
        buf = '\n'.join(entries + [''])
        file = open(file_path, 'a')
        file.write(buf)
        file.close()
    else:
        print "%s already populated" % file_path

@print_when_used
def require_application_uids_gids():
    (etc_passwd_entries, etc_shadow_entries, etc_group_entries) = _get_application_entries()
    _file_append_entries('/etc/passwd', etc_passwd_entries)
    _file_append_entries('/etc/shadow', etc_shadow_entries)
    _file_append_entries('/etc/group',  etc_group_entries)
