from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
urlpatterns = patterns('',
    (r'^$', 'web_ui.main.views.index.index'),
    (r'^pricing$',                  'web_ui.main.views.index.pricing'),
    # Log in/log out/request password reset
    (r'^login$',                  'web_ui.main.views.login_logout.login'),
    (r'^logout$',                 'web_ui.main.views.login_logout.logout'),
    (r'^request_reset_password$', 'web_ui.main.views.login_logout.request_reset_password'),
    (r'^reset_password$', 'web_ui.main.views.login_logout.reset_password'),
    (r'^set_password$', 'web_ui.main.views.login_logout.set_password'),
    # Request account/create account using invite code
    (r'^signup$',     'web_ui.main.views.create_account.signup'),
    (r'^join$',       'web_ui.main.views.create_account.join'),
    (r'^hackerdojo$', 'web_ui.main.views.create_account.hackerdojo'),
    # Administrative dashboard
    (r'^admin$',        'web_ui.main.views.admin.admin'),
    (r'^admin/invite$', 'web_ui.main.views.admin.invite'),
    (r'^admin/get_emails$', 'web_ui.main.views.admin.get_emails'),
    # User dashboard
    (r'^dashboard$',                                                             'web_ui.main.views.dashboard_applicationlist.applicationlist'),
    (r'^dashboard/account$',                                                     'web_ui.main.views.dashboard_account.account'),
    (r'^dashboard/account/change_password$',                                     'web_ui.main.views.dashboard_account.change_password'),
    (r'^dashboard/account/change_email$',                                        'web_ui.main.views.dashboard_account.change_email'),
    (r'^dashboard/account/add_ssh_public_key$',                                  'web_ui.main.views.dashboard_account.add_ssh_public_key'),
    (r'^dashboard/account/remove_ssh_public_key$',                               'web_ui.main.views.dashboard_account.remove_ssh_public_key'),
    (r'^dashboard/invite$',                                                      'web_ui.main.views.dashboard_invite.invite'),
    (r'^dashboard/application/(?P<application_name>[^/]*)$',                     'web_ui.main.views.dashboard_application.application'),
    (r'^dashboard/application/(?P<application_name>[^/]*)/allocation$',          'web_ui.main.views.dashboard_application.application_allocation_redirect'),
    (r'^dashboard/application/(?P<application_name>[^/]*)/add_domain$',          'web_ui.main.views.dashboard_application.add_domain_redirect'),
    (r'^dashboard/application/(?P<application_name>[^/]*)/remove_domain$',       'web_ui.main.views.dashboard_application.remove_domain_redirect'),
    (r'^dashboard/application/(?P<application_name>[^/]*)/debug$',               'web_ui.main.views.dashboard_application.debug_redirect'),
    (r'^dashboard/application/(?P<application_name>[^/]*)/server_cache$',        'web_ui.main.views.dashboard_application.server_cache_redirect'),
    (r'^dashboard/application/(?P<application_name>[^/]*)/logs$',                'web_ui.main.views.dashboard_application.logs'),
    (r'^dashboard/application/(?P<application_name>[^/]*)/add_collaborator$',    'web_ui.main.views.dashboard_application.add_collaborator'),
    (r'^dashboard/application/(?P<application_name>[^/]*)/remove_collaborator$', 'web_ui.main.views.dashboard_application.remove_collaborator'),
    (r'^dashboard/application/(?P<application_name>[^/]*)/delete$',              'web_ui.main.views.dashboard_application.delete_application'),
    (r'^dashboard/billing$',                                                     'web_ui.main.views.dashboard_billing.update_billing_info'),
    # Documentation
    (r'^docs/', include('docs.urls')),
    # Static content -- note, we should run web_ui as a djangy application since we're using static.serve
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'static'}),
)
