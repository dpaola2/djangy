from shared import *

@http_methods('GET')
@auth_required
def applicationlist(request):
    message = get_session_message(request)
    email = request.session.get('email')

    user = User.get_by_email(email)
    applications = user.get_accessible_applications()
    return render_to_response('dashboard_applicationlist.html', {
        'navbar_section':'dashboard',
        'applications':applications,
        'user':user,
        'email':email,
        'message': message
    })
