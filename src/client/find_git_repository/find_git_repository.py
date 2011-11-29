import os.path

__DOT_GIT_FILES__            = ['config', 'description', 'HEAD']
__DOT_GIT_SUBDIRECTORIES__   = ['hooks', 'info', 'objects', 'refs']

def find_git_repository(cwd):
    """Finds the nearest enclosing git repository.  Raises a
    GitRepositoryNotFoundException if there is none."""

    # Normalize the path
    dir_path = os.path.abspath(cwd)
    # Start with this directory, and iterate up a level until we find a git
    # repository root directory.
    while dir_path != '/':
        if is_git_repository_root(dir_path):
            return dir_path
        else:
            dir_path = os.path.dirname(dir_path)

    # Check one more time just in case / is a git repository
    if is_git_repository_root(dir_path):
        return dir_path
    else:
        raise GitRepositoryNotFoundException(cwd)

def is_git_repository_root(dir_path):
    """Is dir_path the root directory of a git repository?"""

    # Is there a .git subdirectory?  And is it well-formed?
    git_dir = os.path.join(dir_path, '.git')
    if os.path.isdir(git_dir) \
    and is_git_dir(git_dir):
        return True

    # Is this directory itself a bare git repository with no working copy
    # checkout directory?
    return os.path.basename(dir_path).endswith('.git') \
        and os.path.basename(dir_path) != '.git' \
        and is_git_dir(dir_path)

def is_git_dir(dir_path):
    """Is dir_path a reasonably well-formed .git directory?"""

    # Files that must exist in a .git directory
    for git_file in __DOT_GIT_FILES__:
        if not os.path.isfile(os.path.join(dir_path, git_file)):
            return False

    # Subdirectories that must exist in a .git directory
    for git_subdir in __DOT_GIT_SUBDIRECTORIES__:
        if not os.path.isdir(os.path.join(dir_path, git_subdir)):
            return False
    return True

class GitRepositoryNotFoundException(Exception):
    """No git repository root found in any parent of specified directory."""
    def __init__(self, path):
        self.path = path
    def __str__(self):
        return 'No git repository root found in any parent of directory "%s".' % self.path
