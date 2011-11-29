from shared import *
import admin

@http_methods('GET', 'POST')
@auth_required
def invite(request):
    if request.method == 'POST':
        admin.invite(request)

    message = get_session_message(request)
    email = request.session.get('email')
    user = User.get_by_email(email)

    num_invited = User.objects.filter(referrer=user).count() + WhiteList.objects.filter(referrer=user).count()
    num_remaining_invitations = user.invite_limit - num_invited

    return render_to_response('dashboard_invite.html', {
        'navbar_section': 'dashboard',
        'user': user,
        'email': email,
        'sessionid': request.COOKIES['sessionid'],
        'message': message,
        'num_remaining_invitations': num_remaining_invitations
    })
