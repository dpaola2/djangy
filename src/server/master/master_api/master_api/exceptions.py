class AddApplicationException(Exception):
    """Error adding application."""
    def __init__(self, result, application_name, email, pubkey):
        self.result = result
        self.application_name = application_name
        self.email = email
        self.pubkey = pubkey
    def __str__(self):
        return 'Error adding application.  Return code: %i, application_name: "%s", email: "%s", pubkey: "%s"' % \
            (self.result, self.application_name, self.email, self.pubkey)

class RemoveApplicationException(Exception):
    """Error removing application."""
    def __init__(self, result, application_name):
        self.result = result
        self.application_name = application_name
    def __str__(self):
        return 'Error removing application.  Return code: %i, application_name: "%s".' % (self.result, self.application_name)

class UserNotFoundException(Exception):
    """ Error finding user """
    def __init__(self, email):
        self.email = email
    def __str__(self):
        return "Error finding user with email: %s." % self.email

class UpdateBillingException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class ComponentNotFoundException(Exception):
    def __init__(self, component):
        self.component = component
    def __str__(self):
        return "Error looking up component: %s" % self.component

class UpdateAllocationException(Exception):
    def __init__(self, result, application_name):
        self.result = result
        self.application_name = application_name
    def __str__(self):
        return "Error updating allocation. Return code: %i, application_name: %s" % (self.result, self.application_name)

class AddDomainException(Exception):
    def __init__(self, result, application_name, domain_name):
        self.result = result
        self.application_name = application_name
        self.domain_name = domain_name
    def __str__(self):
        return "Error adding domain '%s' to application '%s'. Return code: %i" % (self.domain_name, self.application_name, self.result)

class DeleteDomainException(Exception):
    def __init__(self, result, application_name, domain_name):
        self.result = result
        self.application_name = application_name
        self.domain_name = domain_name
    def __str__(self):
        return "Error deleting domain '%s' to application '%s'. Return code: %i" % (self.domain_name, self.application_name, self.result)
