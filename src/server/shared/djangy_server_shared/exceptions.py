class BundleAlreadyExistsException(Exception):
    """Could not create a bundle because it already exists."""
    def __init__(self, bundle_name):
        self.bundle_name = bundle_name
    def __str__(self):
        return 'Could not create bundle "%s" because it already exists.' % self.bundle_name

class InvalidBundleException(Exception):
    """Invalid bundle."""
    def __init__(self, bundle_name):
        self.bundle_name = bundle_name
    def __str__(self):
        return 'Invalid bundle name "%s".' % self.bundle_name

class GitCloneException(Exception):
    """Error in git clone."""
    def __init__(self, application_name, temp_repo_path):
        self.application_name = application_name
        self.temp_repo_path   = temp_repo_path
    def __str__(self):
        return 'Error in git clone: application_name="%s" and temp_repo_path="%s"' % (self.application_name, self.temp_repo_path)

class CheckApplicationUidGidException(Exception):
    """Checking application uid/gid failed."""
    def __init__(self, id_type, id_value):
        self.id_type  = id_type
        self.id_value = id_value
    def __str__(self):
        return 'Checking application uid/gid failed: %i is not a valid %s.' % (self.id_value, self.id_type)

class SetUidGidFailedException(Exception):
    """Set uid/gid failed."""
    def __init__(self):
        pass
    def __str__(self):
        return self.__doc__

class InvalidApplicationNameException(Exception):
    """The requested application name does not comply with Djangy's application naming guidelines."""
    def __init__(self, application_name):
        self.application_name = application_name
    def __str__(self):
        return 'The application name "%s" does not comply with Djangy\'s application naming guidelines.' % self.application_name

class ApplicationNotInDatabaseException(Exception):
    """The requested application was not found in the management database."""
    def __init__(self, application_name):
        self.application_name = application_name
    def __str__(self):
        return 'Could not find application "%s" in management database.' % self.application_name

class ArgumentException(Exception):
    """Error parsing command-line argument list."""
    def __init__(self):
        pass
    def __str__(self):
        return self.__doc__

class RepeatedArgumentException(ArgumentException):
    """The same key was used for multiple command-line arguments."""
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return 'The key "%s" was used for multiple command-line arguments.' % self.key

class UnexpectedArgumentException(ArgumentException):
    """An unknown key was used for a command-line argument."""
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return 'Unknown key "%s" was used for a command-line argument.' % self.key

class MissingArgumentException(ArgumentException):
    """A command-line argument was missing."""
    def __init__(self):
        pass
    def __str__(self):
        return self.__doc__

class PasswordGenerationException(Exception):
    """Password generation failed."""
    def __init__(self):
        pass
    def __str__(self):
        return self.__doc__
