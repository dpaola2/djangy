import os.path

__DJANGO_PROJECT_DIR_FILES__ = set(['__init__.py', 'manage.py', 'settings.py', 'urls.py'])

def find_django_project(repo_path):
    """Finds a django project within the given repository.  If the
    repository contains more than one django project, an arbitrary one will
    be chosen.  Raises a NoDjangoProjectFoundException if the repository
    does not contain any django projects."""

    # Traverse a git repository, but don't follow symbolic links because we
    # don't know where they might point.
    for (dir_path, sub_dir_names, file_names) in os.walk(repo_path, topdown=True, followlinks=False):
        # Don't bother stepping into the .git directory
        if '.git' in sub_dir_names:
            sub_dir_names.remove('.git')
        # Check if we've found a django project
        if '__init__.py' in file_names and \
        dir_contains_module(dir_path, 'manage') and \
        dir_contains_module(dir_path, 'settings') and \
        dir_contains_module(dir_path, 'urls'):
            return dir_path

    # If we got here, we did an exhaustive search of the repository and
    # couldn't find a django project.
    raise DjangoProjectNotFoundException(repo_path)

def dir_contains_module(dir_path, module_name):
    return os.path.isfile(os.path.join(dir_path, module_name + '.py')) or \
        os.path.isdir(os.path.join(dir_path, module_name)) and \
        os.path.isfile(os.path.join(dir_path, module_name, '__init__.py'))

class DjangoProjectNotFoundException(Exception):
    """No django project found in the specified repository."""
    def __init__(self, repo_path):
        self.repo_path = repo_path
    def __str__(self):
        return 'No django project found in the repository "%s".' % self.repo_path
