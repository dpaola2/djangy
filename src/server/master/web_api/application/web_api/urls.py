from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'web_api.api.views.index'),
    (r'^create$', 'web_api.api.views.create'),
    (r'^delete$', 'web_api.api.views.delete'),
    (r'^logs$', 'web_api.api.views.logs'),
    (r'^syncdb$', 'web_api.api.views.syncdb'),
    (r'^migrate$', 'web_api.api.views.migrate'),
    (r'^createsuperuser$', 'web_api.api.views.createsuperuser'),
)
