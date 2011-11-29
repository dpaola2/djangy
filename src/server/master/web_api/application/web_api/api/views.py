from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseServerError
from master_api import name_available, add_application, remove_application, retrieve_logs, command
from management_database import *
import logging, json

def _presence_of(arg, msg):
    """ Decorator that returns the specified message if the specified POST variable isn't present."""
    def presence(func):
        def verify(*args, **kwargs):
            if not args[0].POST.get(arg, None):
                return HttpResponseBadRequest(msg)
            return func(*args, **kwargs)
        return verify
    return presence

def _auth_required(func):
    """ Decorator for API function calls that ensures the presence of email, hashed_password, pubkey, and application_name. """
    def auth(*args, **kwargs):
        if args[0].method.lower() != 'post':
            return HttpResponseNotAllowed(['POST'])

        email = args[0].POST.get('email', None)
        if email is None:
            return HttpResponseBadRequest('No email provided.')

        hashed_password = args[0].POST.get('hashed_password', None)
        if hashed_password is None:
            return HttpResponseBadRequest('No password provided.')

        user = User.get_by_email(email)
        if user is None:
            return HttpResponseForbidden('Please create an account on Djangy.com first.')

        if user.passwd != hashed_password:
            return HttpResponseForbidden('Invalid password.')

        return func(*args, **kwargs)
    return auth

def _check_application_access(func):
    """ Decorator for checking that the user has access to the selected application.  Use after _auth_required. """
    def check_application_access(request):
        email = request.REQUEST.get('email')
        application_name = request.REQUEST.get('application_name')
        user = User.get_by_email(email)
        application = Application.get_by_name(application_name)
        if application and application.accessible_by(user):
            return func(request, email, application_name)
        else:
            return HttpResponseBadRequest('Access denied for user "%s" to application "%s".' % (email, application_name))
    return check_application_access

@_auth_required
def index(request):
    return HttpResponse('')

@_presence_of('pubkey', 'No public key provided.')
@_presence_of('application_name', 'No application name provided.')
@_auth_required
def create(request):
    """ create command, called from the djangy command line client."""
    email = request.POST.get('email')
    application_name = request.POST.get('application_name')

    # check for that application name
    if not name_available(application_name):
        return HttpResponseBadRequest('Error: an application named "%s" already exists.' % application_name)

    # create the application
    try:
        pubkey = request.POST.get('pubkey')
        add_application(application_name, email, pubkey)
    except Exception, e:
        return HttpResponseServerError('Exception while adding application: %s' % e)

    logging.info('Application created: %s.' % application_name)

    return HttpResponse('Application created.')

@_presence_of('application_name', 'No application name provided.')
@_auth_required
@_check_application_access
def delete(request, email, application_name):
    """ Remove a project. Called from the djangy.py command line client. """
    status = remove_application(application_name)
    if not status:
        return HttpResponseServerError('Error: %s.' % status)

    return HttpResponse('Your application, %s, has been deleted.' % application_name)

@_presence_of('application_name', 'No application name provided.')
@_auth_required
@_check_application_access
def logs(request, email, application_name):
    """ Return the last 100 lines of the django.log file for this application."""
    try:
        return HttpResponse(retrieve_logs(application_name))
    except Exception, e:
        return HttpResponseServerError('Error: %s.' % e)

@_presence_of('application_name', 'No application name provided.')
@_auth_required
@_check_application_access
def syncdb(request, email, application_name):
    """ Run the syncdb command. """
    try:
        return HttpResponse(command(application_name, 'syncdb', '--noinput'))
    except Exception, e:
        return HttpResponseServerError('Error: %s.' % e)

@_presence_of('application_name', 'No application name provided.')
@_auth_required
@_check_application_access
def migrate(request, email, application_name):
    """ Run the migrate command. """
    raw_args = request.POST.get('args', '')
    logging.info('[MIGRATE] got args: %s' % raw_args)
    try:
        args = json.loads(raw_args)
    except:
        args = []
    try:
        return HttpResponse(command(application_name, 'migrate', *args))
    except Exception, e:
        return HttpResponseServerError('Error: %s.' % e)

@_presence_of('application_name', 'No application name provided.')
@_auth_required
@_check_application_access
def createsuperuser(request, email, application_name):
    """ Run the createsuperuser command. """
    try:
        return HttpResponse(command(application_name, 'createsuperuser'))
    except Exception, e:
        return HttpResponseServerError('Error: %s.' % e)
