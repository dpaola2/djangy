from shared import *

@http_methods('GET')
def index(request):
    message = get_session_message(request)
    email = request.session.get('email')
    if email:
        user = User.get_by_email(email)
    else:
        user = None
    return render_to_response('index.html', {'navbar_section':'home', 'message':message, 'user':user, 'index':True})

@http_methods('GET')
def pricing(request):
    message = get_session_message(request)
    email = request.session.get('email')
    if email:
        user = User.get_by_email(email)
    else:
        user = None
    return render_to_response('pricing.html', {'navbar_section':'pricing', 'message':message, 'user':user, 'index':False})
