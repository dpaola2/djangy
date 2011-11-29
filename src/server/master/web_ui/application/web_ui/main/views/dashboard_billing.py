from shared import *
from master_api import update_billing_info as do_update_billing_info

# XXX - CSRF
@http_methods('GET', 'POST')
@auth_required
def update_billing_info(request):
    email = request.session.get('email')
    user = User.get_by_email(email)
    REQUIRED_KEYS = [
        'first_name',
        'last_name',
        'cc_number',
        'cvv',
        'expiration_month',
        'expiration_year'
    ]
    if request.method == 'GET':
        info = retrieve_billing_info(user)
        # if the values are in the session, restore them and remove from session
        for key in REQUIRED_KEYS:
            try:
                value = request.session.get(key, None)
                if value:
                    info[key] = value
                del request.session[key]
            except:
                pass
        message = get_session_message(request)
        amount = None
        usage = None
        try:
            amount = int(info['usage'])
            dollars = (amount / 100)
            cents = (amount % 100)
            usage = "$%s.%02d" % (dollars, cents)
        except:
            pass
        return render_to_response('dashboard_billing.html', {
            'navbar_section':'dashboard', 
            'user':user, 
            'info':info, 
            'message':message,
            'months':cc_months(),
            'years':cc_years(),
            'usage':usage,
        })
    elif request.method == 'POST':
        email = request.session.get('email')
        if not email:
            return HttpResponseRedirect('/dashboard')

        msg_mapper = {
            'cc_number':'Card number',
            'exp_month':'Expiration month',
            'exp_year':'Expiration year',
            'cvv':'CVV',
            'first_name':'First name',
            'last_name':'Last name'
        }
        info = dict()
        for k in REQUIRED_KEYS:
            value = request.POST.get(k, None)
            info[k] = value
            if k != 'cc_number':
                request.session[k] = value
        for k in REQUIRED_KEYS:
            if info[k] is None or info[k] == '':
                    request.session['message'] = 'Missing: %s' % msg_mapper.get(k, k)
                    return HttpResponseRedirect('/dashboard/billing')

        message = do_update_billing_info(email, info)
        if True == message:
            for k in REQUIRED_KEYS:
                try:
                    del request.session[k]
                except:
                    pass
            request.session['message'] = 'Your billing settings have been saved.  Thanks!'
        else:
            request.session['message'] = message
            return HttpResponseRedirect('/dashboard/billing')
        return HttpResponseRedirect('/dashboard')
