import re, traceback
from shared import *
import management_database
from management_database import *

def _check_application_access(func):
    """ Decorator for checking that the user has access to the selected application.  Use after auth_required. """
    def check_application_access(request, application_name):
        email = request.session.get('email')
        user = User.get_by_email(email)
        application = Application.get_by_name(application_name)
        if application and application.accessible_by(user):
            return func(request, application_name)
        else:
            return HttpResponseForbidden('Access denied for user "%s" to application "%s".' % (email, application_name))
    return check_application_access

# GET /dashboard/application/<application_name>
@http_methods('GET')
@auth_required
@_check_application_access
def application(request, application_name):
    email = request.session.get('email')
    user = User.get_by_email(email)
    application = Application.get_by_name(application_name)

    message = get_session_message(request)
    gunicorn_processes = Process.objects.filter(application__name=application_name, proc_type='gunicorn').aggregate(Sum('num_procs'))['num_procs__sum']
    celery_processes   = Process.objects.filter(application__name=application_name, proc_type='celery'  ).aggregate(Sum('num_procs'))['num_procs__sum']
    custom_domains = VirtualHost.get_virtualhosts_by_application_name(application_name)
    custom_domains.remove('%s.djangy.com' % application.name)
    return render_to_response('dashboard_application.html', {
        'navbar_section':'dashboard',
        'user': user,
        'application_name': application.name,
        'sessionid': request.COOKIES['sessionid'],
        'application_instances': gunicorn_processes,
        'application_instances_range': range(1, 10+1),
        'background_workers': celery_processes,
        'background_workers_range': range(0, 5+1),
        'message': message,
        'custom_domains': custom_domains,
        'enable_debug': application.debug,
        'enable_server_cache': application.is_server_cache_enabled(),
        'owner_email': application.account.email,
        'collaborator_emails': application.get_collaborators()
    })

# POST /dashboard/application/<application_name>/delete?really_delete=yes
@http_methods('POST')
@token_required
@auth_required
@_check_application_access
def delete_application(request, application_name):
    if not request.POST.get('really_delete'):
        return HttpResponseRedirect('/dashboard/application/%s' % application_name)

    try:
        remove_application(application_name)
    except Exception, e:
        return HttpResponseServerError('Error deleting application.')

    request.session['message'] = 'Application %s was deleted.' % application_name
    return HttpResponseRedirect('/dashboard')

# POST /dashboard/application/<application_name>/add_collaborator?email=<email>
@http_methods('POST')
@token_required
@auth_required
@_check_application_access
def add_collaborator(request, application_name):
    email = request.POST.get('email')
    if email != None:
        try:
            application = management_database.Application.get_by_name(application_name)
            if application.add_collaborator(email):
                request.session['message'] = 'Collaborator %s added to %s' % (email, application_name)
            else:
                request.session['message'] = 'Collaborator %s already has access to %s' % (email, application_name)
        except NoUserException as e:
            request.session['message'] = 'Error: %s does not have a Djangy account' % email
        except Exception as e:
            request.session['message'] = 'Error adding collaborator %s <br/><pre>%s</pre>' % (email, traceback.format_exc())

    return HttpResponseRedirect('/dashboard/application/%s' % application_name)

# GET /dashboard/application/<application_name>/remove_collaborator?email=<email>
@http_methods('GET')
@token_required
@auth_required
@_check_application_access
def remove_collaborator(request, application_name):
    email = request.GET.get('email')
    if email != None:
        try:
            application = Application.get_by_name(application_name)
            application.remove_collaborator(email)
            request.session['message'] = 'Collaborator %s removed from %s' % (email, application_name)
        except Exception:
            request.session['message'] = 'Error removing collaborator %s' % email

    return HttpResponseRedirect('/dashboard/application/%s' % application_name)

# GET /dashboard/application/<application_name>/logs
@http_methods('GET')
@auth_required
@_check_application_access
def logs(request, application_name):
    return HttpResponse(retrieve_logs(application_name), content_type='text/plain')

# POST /dashboard/application/<application_name>/debug?enable_debug=yes
@http_methods('POST')
@token_required
@auth_required
@_check_application_access
def debug_redirect(request, application_name):
    _application_debug(request, application_name)
    return HttpResponseRedirect('/dashboard/application/%s' % application_name)

# Called by application_debug_redirect()
#@http_methods('GET', 'POST')
#@token_required
#@auth_required
#@_check_application_access
def _application_debug(request, application_name):
    if request.method == 'POST':
        enable_debug = not not request.POST.get('enable_debug')
        toggle_debug(application_name, enable_debug)

    elif request.method == 'GET':
        enable_debug = Application.get_by_name(application_name).debug
        return HttpResponse(enable_debug)

# POST /dashboard/application/<application_name>/server_cache?enable_server_cache=yes
@http_methods('POST')
@token_required
@auth_required
@_check_application_access
def server_cache_redirect(request, application_name):
    server_cache = not not request.POST.get('enable_server_cache')
    if server_cache:
        enable_server_cache(application_name)
    else:
        disable_server_cache(application_name)
    return HttpResponseRedirect('/dashboard/application/%s' % application_name)

# POST /dashboard/application/<application_name>/allocation
@http_methods('POST')
@token_required
@auth_required
@_check_application_access
def application_allocation_redirect(request, application_name):
    if _has_billing_info(application_name):
        _application_allocation(request, application_name)
        return HttpResponseRedirect('/dashboard/application/%s' % application_name)
    else:
        request.session['message'] = "We need your billing info first!"
        return HttpResponseRedirect('/dashboard/billing')

def _require_int(str_int):
    try:
        return int(str_int)
    except:
        return None

# Called by application_allocation_redirect()
#@http_methods('POST')
#@token_required
#@auth_required
#@_check_application_access
def _application_allocation(request, application_name):
    application_processes = _require_int(request.POST.get('application_instances'))
    if application_processes == None:
        return HttpResponseBadRequest('Missing argument: application_instances')
    background_processes = _require_int(request.POST.get('background_workers'))
    if background_processes == None:
        return HttpResponseBadRequest('Missing argument: background_workers')
    result = update_application_allocation(application_name, {'application_processes':application_processes, 'background_processes':background_processes})
    if not result:
        return HttpResponseServerError('There was a problem saving changes.  Djangy staff has been notified.')

# called by application_allocation_redirect
def _has_billing_info(application_name):
    app = Application.get_by_name(application_name)
    if not app:
        return False
    cust_id = app.account.customer_id
    if cust_id == '-1' or cust_id == '' or cust_id is None:
        return False
    return True

_domain_name_regex = re.compile('^[A-Za-z0-9-][A-Za-z0-9-\.]*[A-Za-z0-9-]$')

def _valid_custom_domain(domain):
    return domain \
    and _domain_name_regex.match(domain) != None \
    and not domain.endswith('.djangy.com') \
    and domain != 'djangy.com'

# POST /dashboard/application/<application_name>/add_domain
@http_methods('POST')
@token_required
@auth_required
@_check_application_access
def add_domain_redirect(request, application_name):
    domain = request.REQUEST.get('domain')
    if _valid_custom_domain(domain):
        add_domain_name(application_name, domain)
    return HttpResponseRedirect('/dashboard/application/%s' % application_name)

# GET /dashboard/application/<application_name>/remove_domain?sessionid=...
@http_methods('GET')
@token_required
@auth_required
@_check_application_access
def remove_domain_redirect(request, application_name):
    domain = request.REQUEST.get('domain')
    if _valid_custom_domain(domain):
        delete_domain_name(application_name, domain)
    return HttpResponseRedirect('/dashboard/application/%s' % application_name)

