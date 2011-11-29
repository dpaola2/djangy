import site
site.addsitedir("/srv/djangy/run/python-virtual/lib/python2.6/site-packages")

import os, sys

sys.path.append('/srv/djangy/src/server/master/web_api/application/web_api')
sys.path.append('/srv/djangy/src/server/master/web_api/application')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
