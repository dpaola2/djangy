import grp, os, os.path, pwd, shutil, subprocess, tempfile


# Decorator to print out a status message boxing the output of a function. 
# Useful for long running functions or those that print output.
def print_when_used(func):
    def _line(char):
        return ''.join([char for i in range(0, 80/len(char))])
    def print_when_used(*args):
        print _line('=')
        print func.__name__ + str(args)
        print _line('- ')
        try:
            return func(*args)
        finally:
            print _line('-')
    return print_when_used

# Decorator to run a function in a temporary directory, and then delete the
# temporary directory when the function returns (or throws an exception).
def in_tempdir(func):
    def in_tempdir(*args, **kwargs):
        tempdir = tempfile.mkdtemp(prefix='djangy_install_')
        assert tempdir.startswith('/tmp/djangy_install_')
        old_dir = os.getcwd()
        try:
            os.chdir(tempdir)
            return func(*args, **kwargs)
        finally:
            os.chdir(old_dir)
            shutil.rmtree(tempdir)
    return in_tempdir

# Decorator to run a function in a given (static) directory
def in_dir(dir):
    def in_dir(func):
        def in_dir(*args, **kwargs):
            old_dir = os.getcwd()
            os.chdir(dir)
            try:
                return func(*args, **kwargs)
            finally:
                os.chdir(old_dir)
        return in_dir
    return in_dir

# For use as "with cd(dir): ..."
class cd(object):
    def __init__(self, dir_path):
        self._dir_path = dir_path
    def __enter__(self):
        self._old_dir_path = os.getcwd()
        os.chdir(self._dir_path)
    def __exit__(self, type, value, traceback):
        os.chdir(self._old_dir_path)

# Run an external program, fail if it returns non-zero
def run(*args):
    assert 0 == subprocess.call(list(args))

# Run an external program supplying stdin contents, fail if it returns non-zero
def run_with_stdin(args, stdin=None):
    p = subprocess.Popen(args, stdin=subprocess.PIPE)
    p.stdin.write(stdin)
    p.stdin.close()
    assert 0 == p.wait()

# Run an external program, ignore its return value
def run_ignore_failure(*args):
    subprocess.call(list(args))

# Check that a user exists, with the given settings.
# Settings with value None are not checked.
def user_exists(username=None, uid=None, gid=None, homedir=None, shell=None):
    try:
        passwd = pwd.getpwnam(username)
    except:
        try:
            passwd = pwd.getpwuid(uid)
        except:
            return False

    return not (
        (uid      and passwd.pw_uid   != uid     ) or
        (gid      and passwd.pw_gid   != gid     ) or
        (homedir  and passwd.pw_dir   != homedir ) or
        (shell    and passwd.pw_shell != shell   ))

# Check that a group exists, with the given settings.
# Settings with value None are not checked.
def group_exists(groupname=None, gid=None, member_usernames=None):
    try:
        group = grp.getgrnam(groupname)
    except:
        try:
            group = grp.getgrgid(gid)
        except:
            return False

    return not (
        (gid              and group.gr_gid      != gid                  ) or
        (member_usernames and set(group.gr_mem) != set(member_usernames)))

# Try to allocate a fresh UID.
# Raises UidAllocationException.
def _get_fresh_uid():
    for uid in range(100, 1000):
        try:
            pwd.getpwuid(uid)
        except KeyError:
            return uid
    raise UidAllocationException()

# Try to allocate a fresh GID.
# Raises UidAllocationException.
def _get_fresh_gid():
    for gid in range(100, 1000):
        try:
            grp.getgrgid(gid)
        except KeyError:
            return gid
    raise GidAllocationException()

# Called by require_user() to update /etc/passwd and /etc/shadow
# Called by require_group() to update /etc/group
def _append_to_file(file_path, line):
    file = open(file_path, 'a')
    file.write(line + '\n')
    file.close()

# Called by require_file() to create a file that doesn't exist but
# whose contents are specified.
def _create_file(file_path, contents):
    file = open(file_path, 'w')
    file.write(contents)
    file.close()

# Called by require_file() to read and check a file's contents.
# Also called by install.py
def read_file(file_path):
    file = open(file_path, 'r')
    contents = file.read()
    file.close()
    return contents

# Check that a user exists with the given settings, creating one if
# necessary and possible.  Raises RequireUserException
def require_user(username, gid=None, groupname=None, uid=None, homedir=None, shell=None, description=None, create=True):
    # Canonicalize arguments
    if gid == None:
        gid = grp.getgrnam(groupname).gr_gid
    # Create user if it doesn't exist
    if create and not user_exists(username=username):
        if uid != None:
            if user_exists(uid=uid):
                raise RequireUserException(username)
        else:
            uid = _get_fresh_uid()
        etc_passwd_line = '%s:x:%i:%i:%s:%s:%s' % (username, uid, gid, description or '', homedir or '/', shell)
        etc_shadow_line = '%s:*:14907:0:99999:7:::' % username
        _append_to_file('/etc/passwd', etc_passwd_line)
        _append_to_file('/etc/shadow', etc_shadow_line)
    # Check user has correct settings
    if not user_exists(username=username, uid=uid, gid=gid, homedir=homedir, shell=shell):
        raise RequireUserException(username)

# Check that a group exists with the given settings, creating one if
# necessary and possible.  member_usernames must match exactly.
# Raises RequireGroupException
def require_group(groupname, gid=None, member_usernames=[], create=True):
    # Create group if it doesn't exist
    if create and not group_exists(groupname=groupname):
        if gid != None:
            if group_exists(gid=gid):
                raise RequireGroupException(groupname)
        else:
            gid = _get_fresh_gid()
        etc_group_line = '%s:x:%i:%s' % (groupname, gid, ','.join(member_usernames))
        _append_to_file('/etc/group', etc_group_line)
    # Check group has correct settings
    if not group_exists(groupname=groupname, gid=gid, member_usernames=member_usernames):
        raise RequireGroupException(groupname)

@print_when_used
def _copy_directory(dir_path, initial_contents_path):
    run('cp', '-r', initial_contents_path, dir_path)
    print 'Done.'

# Check that a directory exists with the given settings, creating one if
# necessary and possible.
def require_directory(dir_path, username, groupname, mode, initial_contents_path=None, create=True):
    # Canonicalize arguments
    dir_path = os.path.abspath(dir_path)
    uid = pwd.getpwnam(username).pw_uid
    gid = grp.getgrnam(groupname).gr_gid
    # Create directory if it doesn't exist
    if create and not os.path.isdir(dir_path):
        if initial_contents_path:
            _copy_directory(dir_path, initial_contents_path)
        else:
            os.mkdir(dir_path, mode)
    # Ensure correct access permissions
    os.chown(dir_path, uid, gid)
    os.chmod(dir_path, mode)

# Check that a given file exists with the given settings.  If the
# initial_contents are specified and file does not exist, then it is
# created.
# Raises RequireFileException
def require_file(file_path, username, groupname, mode, contents=None, initial_contents=None, overwrite=False):
    # Canonicalize arguments
    file_path = os.path.abspath(file_path)
    uid = pwd.getpwnam(username).pw_uid
    gid = grp.getgrnam(groupname).gr_gid
    if initial_contents == None:
        initial_contents = contents
    # Create file if it doesn't exist or overwrite==True
    if type(initial_contents) == str and (overwrite and os.path.isfile(file_path) or not os.path.exists(file_path)):
        _create_file(file_path, initial_contents)
    # Check file exists
    if not os.path.isfile(file_path) or (contents != None and read_file(file_path) != contents):
        raise RequireFileException(file_path)
    # Ensure correct access permissions
    os.chown(file_path, uid, gid)
    os.chmod(file_path, mode)

# Check that a given link exists and points to a given source path, creating
# the link if possible and neccessary.  Raises RequireLinkException
def require_link(link_path, source_path):
    # Canonicalize arguments
    link_path   = os.path.abspath(link_path)
    source_path = os.path.abspath(source_path)
    # Create link if it doesn't exist or is already a link
    if os.path.islink(link_path):
        os.remove(link_path)
    if not os.path.exists(link_path):
        os.symlink(source_path, link_path)
    else:
        raise RequireLinkException(link_path)

# Make sure that a given file or directory has been removed.
def require_remove(path):
    if os.path.exists(path):
        run('rm', '-rf', path)

# Ensure that a given directory and all its recursive contents are owned by
# a given username/groupname.  Raises RequirePermisException
def require_recursive(root_path, username=None, groupname=None):
    # Canonicalize arguments
    root_path = os.path.abspath(root_path)
    # Call external program to do it
    try:
        run('chown', '-R', '%s:%s' % (username, groupname), root_path)
    except:
        raise RequirePermsException(root_path)

# Raises RequireUbuntuPackagesException
@print_when_used
def require_ubuntu_packages(*packages):
    if subprocess.call(['apt-get', '--yes', 'install'] + list(packages)) != 0:
        raise RequireUbuntuPackagesException(packages)

# Raises RequirePythonPackagesException
@print_when_used
def require_python_packages(*packages):
    for package in packages:
        if subprocess.call(['easy_install', package]) != 0:
            raise RequirePythonPackagesException([package])

# Failure exceptions below.

class RequireUserException(Exception):
    def __init__(self, username):
        self.username = username
    def __str__(self):
        return 'RequireUserException(username=\'%s\')' % self.username

class RequireGroupException(Exception):
    def __init__(self, groupname):
        self.groupname = groupname
    def __str__(self):
        return 'RequireGroupException(groupname=\'%s\')' % self.groupname

class RequireFileException(Exception):
    def __init__(self, file_path):
        self.file_path = file_path
    def __str__(self):
        return 'RequireFileException(file_path=\'%s\')' % self.file_path

class RequireLinkException(Exception):
    def __init__(self, link_path):
        self.link_path = link_path
    def __str__(self):
        return 'RequireLinkException(link_path=\'%s\')' % self.link_path

class RequirePermsException(Exception):
    def __init__(self, root_path):
        self.root_path = root_path
    def __str__(self):
        return 'RequirePermsException(root_path=\'%s\')' % self.root_path

class RequireUbuntuPackagesException(Exception):
    def __init__(self, packages):
        self.packages = packages
    def __str__(self):
        return 'RequireUbuntuPackagesException(packages=%s)' % str(self.packages)

class RequirePythonPackagesException(Exception):
    def __init__(self, package):
        self.package = package
    def __str__(self):
        return 'RequirePythonPackagesException(package=\'%s\')' % self.package

class UidAllocationException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return 'UidAllocationException(): could not find a free system UID'

class GidAllocationException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return 'GidAllocationException(): could not find a free system GID'
