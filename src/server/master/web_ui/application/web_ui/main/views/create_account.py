from shared import *

@http_methods('POST')
def signup(request):
    email = request.POST.get('email')
    if not email:
        return HttpResponseRedirect('/')

    try:
        validate_email(email)
    except Exception, e:
        request.session['message'] = 'Please enter a valid email address, or email support@djangy.com for help.'
        return HttpResponseRedirect('/')
        #return render_to_response('index.html', {'message':'Please enter a valid email address, or email support@djangy.com for help.'})

    email_obj = Email(email = email)
    email_obj.save()

    request.session['message'] = "Thanks!  We'll send you an invitation soon."
    return HttpResponseRedirect('/')
    #return render_to_response('index.html', {'message':"Thanks!  We'll send you an invitation soon.", 'index':True})

# XXX
@http_methods('GET', 'POST')
def join(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        invite_code = request.POST.get('invite_code')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if (not email) or (not password1) or (not password2):
            return HttpResponseRedirect('/')

        if (password1 != password2):
            return render_to_response('join.html', {'message':'Whoops, looks like your passwords didn\'t match.  Please try again.', 'email':email, 'invite_code':invite_code})
        try:
            validate_email(email)
        except:
            return HttpResponseRedirect('/')

        user = User()
        user.email = email
        user.passwd = hash_password(email, password1)

        wl = WhiteList.objects.get(email = email)
        user.referrer = wl.referrer
        user.save()
        wl.delete()
        user.save()

        request.session['email'] = email
        logging.info('%s joined successfully.' % email)
        return HttpResponseRedirect('/dashboard')

    elif request.method == 'GET':
        email = request.GET.get('email')
        invite_code = request.GET.get('invite_code')
        if (email is None) or (invite_code is None):
            request.session['message'] = 'Email or invite code not found.'
            return HttpResponseRedirect('/')

        if WhiteList.verify(email, invite_code):
            return render_to_response('join.html', { 'email':email, 'invite_code':invite_code})
        else:
            request.session['message'] = 'Invalid invite code.'
        return HttpResponseRedirect('/')

# XXX
@http_methods('GET', 'POST')
def hackerdojo(request):
    if request.method == 'GET':
        return render_to_response('hackerdojo.html')

    elif request.method == 'POST':
        email = request.POST.get('email')
        invite_code = request.POST.get('invite_code')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if (not email) or (not password1) or (not password2):
            return render_to_response('hackerdojo.html', {'message':'Please enter a valid email address.', 'invite_code':invite_code})

        if (password1 != password2):
            return render_to_response('hackerdojo.html', {'message':'Whoops, looks like your passwords didn\'t match.  Please try again.', 'email':email, 'invite_code':invite_code})
        try:
            validate_email(email)
        except:
            return render_to_response('hackerdojo.html', {'message':'Please enter a valid email address.', 'invite_code':invite_code})
        if not invite_code:
            return render_to_response('hackerdojo.html', {'message':'It looks like you forgot to enter an invite code.  Try again.', 'email':email})

	try:
            wl = WhiteList.objects.get(invite_code = invite_code)
	    if wl.email:
                return render_to_response('hackerdojo.html', {'message':'That invite code has already been used.  Please try again.', 'email':email})
            wl.email = email
            wl.save()
	except:
            return render_to_response('hackerdojo.html', {'message':'That invite code is invalid.  Please try again.', 'email':email})

        user = User()
        user.email = email
        user.passwd = hash_password(email, password1)
        user.save()


        request.session['email'] = email
	request.session['message'] = 'Thanks for signing up!'
        logging.info('%s joined successfully.' % email)
        return HttpResponseRedirect('/dashboard')
