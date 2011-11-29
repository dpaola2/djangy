from shared import *

@http_methods('GET', 'POST')
@auth_required
@admin_required
def admin(request):
    message = get_session_message(request)

    user = User.get_by_email(request.session.get('email'))
    emails = Email.objects.all()
    user_count = User.objects.all().count()
    app_count = Application.objects.filter(deleted=None).all().count()
    emails_applications = [(u.email, u.application_set.filter(deleted=None)) for u in User.objects.all()]
    return render_to_response('admin.html', {
        'navbar_section':'admin',
        'emails_applications':emails_applications,
        'user':user,
        'message':message,
        'emails':emails,
        'user_count':user_count,
        'app_count':app_count
    })

# XXX - CSRF
@http_methods('GET', 'POST')
@auth_required
def invite(request):
    email = request.REQUEST.get('email')

    # ensure there are invitations left
    inviter = User.get_by_email(request.session.get('email', None))
    invitees = User.objects.filter(referrer=inviter).count() + WhiteList.objects.filter(referrer=inviter).count()
    if invitees > inviter.invite_limit and (not inviter.admin):
        request.session['message'] = 'You have no invitations left.'
        return HttpResponseRedirect('/dashboard/account')

    # Prevent duplicate invitations
    if User.get_by_email(email) != None:
        request.session['message'] = 'User already exists, email not sent to %s.' % email
        return HttpResponseRedirect('/dashboard/account')

    invite_code = gen_invite_code()

    wl = WhiteList.objects.all().filter(email=email)
    for obj in wl:
        WhiteList.delete(obj)
    wl = WhiteList(email=email)
    wl.invite_code = invite_code
    try:
        wl.referrer = User.get_by_email(request.session.get('email', None))
    except:
        logging.debug("tried to set whitelist referrer to: %s" % request.session.get("email", None))
    wl.save()
    referrer = 'the Djangy admin'
    if wl.referrer:
        referrer = wl.referrer.email
    # mark the user as invited
    try:
        email_object = Email.objects.filter(email=email).all()
        for em in email_object:
            em.invited = True
            em.save()
    except Exception, e:
        logging.debug(e)

    # email the user
    send_mail(
        'Your Djangy.com Private Beta Invitation',
        """
Congratulations, %s has invited you to join the private beta of Djangy.com,
the hosting service that lets you deploy your Django applications instantly!

Your invite code is: %s

Click the following link to sign up:
https://www.djangy.com/join?%s

For more information, check out our documentation:
http://www.djangy.com/docs

Please email support@djangy.com with any feedback you may have.

Love,
Djangy.com""" % (referrer, invite_code, urlencode({'email':email, 'invite_code':invite_code})),
        'support@djangy.com',
        [email, 'support@djangy.com'], fail_silently=False
    )

    request.session['message'] = 'Invitation sent to %s' % email
    return HttpResponseRedirect('/admin')

@auth_required
@admin_required
def get_emails(request):
    emails = [user.email for user in User.objects.all()]
    return render_to_response("emails.txt", {'emails':emails}, mimetype="text/plain")
