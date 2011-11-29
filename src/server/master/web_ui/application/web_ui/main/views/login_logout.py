from shared import *

@http_methods('GET', 'POST')
def login(request):
    if request.session.get('email'):
        return HttpResponseRedirect('/dashboard')

    if request.method == 'GET':
        return render_to_response('login.html', {'navbar_section':'login'})

    email = request.POST.get('email')
    password = request.POST.get('password')

    # Check the login email address and hashed password
    try:
        validate_email(email)
        user = User.get_by_email(email)
        assert check_password(email, password, user.passwd)
    except:
        return render_to_response('login.html', {'navbar_section':'login', 'message':'Incorrect email address or password.  Please try again.'})

    # set session data
    request.session['email'] = email

    # redirect to the dashboard

    return HttpResponseRedirect('/dashboard')

# XXX - CSRF?
@http_methods('GET', 'POST')
def logout(request):
    try:
        del request.session['email']
    except KeyError:
        pass
    request.session['message'] = 'You have been logged out.'
    return HttpResponseRedirect('/login')

@http_methods('GET', 'POST')
def reset_password(request):
    reset_hash = request.GET.get('reset', None)
    if not reset_hash:
        request.session['message'] = 'No reset code supplied.'
        return HttpResponseRedirect('/')

    email = request.GET.get('email', None)
    if not email:
        request.session['message'] = 'No email code supplied.'
        return HttpResponseRedirect('/')

    user = User.get_by_email(email)
    if not user:
        request.session['message'] = 'Invalid user.'
        return HttpResponseRedirect('/')

    if check_password(email, user.passwd, reset_hash):
        # legit request, go ahead and process
        return render_to_response('reset_password_form.html', {'email': email})
    request.session['message'] = 'Invalid reset hash.'
    return HttpResponseRedirect('/')

@http_methods('POST')
def set_password(request):
    email = request.POST.get("email", None)
    if not email:
        return HttpResponseRedirect('/')
    password1 = request.POST.get('password1', None)
    password2 = request.POST.get('password2', None)
    if not password1 or not password2 or password1 != password2:
        request.session['message'] = 'Your passwords did not match.'
        return render_to_response('reset_password_form.html', {'email':email})
    user = User.get_by_email(email)
    if not user:
        return HttpResponseRedirect('/')
    user.passwd = hash_password(email, password1)
    user.save()
    request.session['message'] = 'Your password has been reset.'
    request.session['email'] = email
    return HttpResponseRedirect('/dashboard')

@http_methods('POST', 'GET')
def request_reset_password(request):
    if request.method.lower() == 'post':
        # send the email
        email = request.POST.get('email', None)
        if not email:
            return HttpResponseRedirect('/')
        user = User.get_by_email(email)
        if not user:
            return HttpResponseRedirect('/')
        reset_hash = hash_password(email, user.passwd)
        message_body = """

A password reset request has been requested for the Djangy account owned by this email address.  If this is correct, please click on the following link:

https://www.djangy.com/reset_password?email=%s&reset=%s

If not, please simply disregard this message or contact support@djangy.com.

-Djangy
        """ % (email, reset_hash)
        result = send_mail('Password Reset request', message_body, 'support@djangy.com', [email], fail_silently=False)
        request.session['message'] = 'Please check your email for a link to reset your password.'
        return HttpResponseRedirect('/')
    else: # GET request
        return render_to_response('request_reset_password.html')
