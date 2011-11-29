from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseRedirect, HttpResponseServerError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.db.models import Sum
from web_ui.main.utils import check_password, hash_password
from web_ui.main.models import *
from web_ui.main.invite_code import gen_invite_code
from management_database import *
from master_api import *
import os, logging
from urllib import urlencode
from datetime import datetime

#
# Decorators that abstract out common checks for views.
#

# Decorator for views that require users to be logged in.
def auth_required(func):
    """ Decorator for views that require users to be logged in. """
    def _auth_required(request, *args, **kwargs):
        if not request.session.get('email'):
            return HttpResponseRedirect('/login')
        return func(request, *args, **kwargs)
    return _auth_required

# Decorator for views that perform an action and hence must be protected against CSRF.
def token_required(func):
    """ Decorator for views that perform an action and hence must be protected against CSRF. """
    def _token_required(request, *args, **kwargs):
        posted_session_id = request.REQUEST.get('sessionid')
        if posted_session_id != request.COOKIES['sessionid']:
            return HttpResponseForbidden('Invalid session information.')
        return func(request, *args, **kwargs)
    return _token_required

# Decorator for views only accessible to admin users.
def admin_required(func):
    """ Decorator for views only accessible to admin users. """
    def _admin_required(request, *args, **kwargs):
        user = User.get_by_email(request.session.get('email'))

        if not user.admin:
            return HttpResponseRedirect('/dashboard')
        return func(request, *args, **kwargs)
    return _admin_required

# Decorator for views that only accept certain HTTP request methods (e.g., GET, POST).
def http_methods(*methods):
    """ Decorator for views that only accept certain HTTP request methods (e.g., GET, POST). """
    def http_methods_decorator(func):
        def _http_methods(request, *args, **kwargs):
            if not request.method in methods:
                return HttpResponseNotAllowed(methods)
            else:
                return func(request, *args, **kwargs)
        return _http_methods
    return http_methods_decorator

#
# Helper functions
#

def get_session_message(request):
    """ Remove and return the message stored in the session.  This is a poor
        design which can mess up if the user runs two concurrent requests in
        the same session (race condition). """
    message = request.session.get('message')
    try:
        del request.session['message']
    except:
        pass
    return message

# Return True or False the status of whether or not the current session is an admin
def is_admin(request):
    email = request.session.get("email", None)
    if not email:
        return False
    user = User.get_by_email(email)
    if not user:
        return False
    return user.admin
 
def get_user(request):
    email = request.session.get("email", None)
    if not email:
        return False
    return User.get_by_email(email)

def cc_years():
    current_year = datetime.now().year
    return range(current_year, current_year + 12)

def cc_months():
    months = []
    for month in range(1, 13):
        if len(str(month)) == 1:
            numeric = '0' + str(month)
        else:
            numeric = str(month)
        months.append(numeric)
    return months
