from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^add_foo$', 'testapp.main.views.add_foo'),
    (r'^count_rows$', 'testapp.main.views.count_rows'),
    (r'^$', 'testapp.main.views.index'),
    # Example:
    # (r'^testapp/', include('testapp.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
