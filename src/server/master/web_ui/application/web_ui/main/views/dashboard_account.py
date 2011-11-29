from shared import *
import master_api
from django.core.mail import send_mail

@http_methods('GET')
@auth_required
def account(request):
    message = get_session_message(request)
    email = request.session.get('email')
    user = User.get_by_email(email)
    return render_to_response('dashboard_account.html', {
        'navbar_section':'dashboard',
        'user':user,
        'email':email,
        'sessionid': request.COOKIES['sessionid'],
        'message':message,
        'ssh_public_keys':user.get_ssh_public_keys()
    })

@http_methods('POST')
@token_required
@auth_required
def change_password(request):
    email = request.session.get('email')
    if not email:
        return HttpResponseRedirect('/login')

    user = User.get_by_email(email)
    if not user:
        return HttpResponseRedirect('/login')

    # Check that the user knew the old password
    old_password = request.POST.get('old_password')
    if user.passwd != hash_password(email, old_password):
        request.session['message'] = 'Incorrect old password.'
        return HttpResponseRedirect('/dashboard/account')

    # Confirm that the new passwords are the same and nonempty
    new_password1 = request.POST.get('new_password1')
    new_password2 = request.POST.get('new_password2')
    if (not new_password1) or (not new_password2) or (new_password1 != new_password2):
        request.session['message'] = 'New passwords do not match.'
        return HttpResponseRedirect('/dashboard/account')

    user.passwd = hash_password(email, new_password1)
    user.save()

    request.session['message'] = 'Password successfully changed.'
    return HttpResponseRedirect('/dashboard/account')

@http_methods('POST')
@token_required
@auth_required
def change_email(request):
    email = request.session.get('email')
    user = User.get_by_email(email)
    if not user:
        request.session['message'] = 'There was a problem looking up your user account.  Please contact support@djangy.com'
        return HttpResponseRedirect('/dashboard/account')

    new_email = request.POST.get('new_email')

    if not new_email:
        request.session['message'] = 'Invalid email address.'
        return HttpResponseRedirect('/dashboard/account')

    password = request.POST.get('password') or ''

    if hash_password(email, password) != user.passwd:
        request.session['message'] = 'Invalid password.'
        return HttpResponseRedirect('/dashboard/account')

    user.email = new_email
    user.passwd = hash_password(new_email, password)
    user.save()
    request.session['email'] = new_email
    request.session['message'] = 'Your email address has been updated.'
    return HttpResponseRedirect('/dashboard/account')

@http_methods('POST')
@token_required
@auth_required
def add_ssh_public_key(request):
    email = request.session.get('email')
    if not User.get_by_email(email):
        request.session['message'] = 'There was a problem looking up your user account.  Please contact support@djangy.com'
        return HttpResponseRedirect('/dashboard/account')

    ssh_public_key = request.POST.get('ssh_public_key')
    master_api.add_ssh_public_key(email, ssh_public_key)

    return HttpResponseRedirect('/dashboard/account')

@http_methods('GET')
@token_required
@auth_required
def remove_ssh_public_key(request):
    email = request.session.get('email')
    if not User.get_by_email(email):
        request.session['message'] = 'There was a problem looking up your user account.  Please contact support@djangy.com'
        return HttpResponseRedirect('/dashboard/account')

    ssh_public_key_id = int(request.GET.get('id'))
    master_api.remove_ssh_public_key(email, str(ssh_public_key_id))

    return HttpResponseRedirect('/dashboard/account')
