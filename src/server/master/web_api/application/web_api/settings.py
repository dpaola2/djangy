# Django settings for web_api project.
import djangy_server_shared, os.path

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Bob Jones', 'bob@jones.mil')
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE':'mysql',
        'NAME':'web_api',
        'USER':'web_api',
        'PASSWORD':'password goes here',
        'HOST':'',
        'PORT':'',
    },
    'management_database': {
        'ENGINE': 'mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'djangy',                      # Or path to database file if using sqlite3.
        'USER': 'djangy',                      # Not used with sqlite3.
        'PASSWORD': 'password goes here',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

DATABASE_ROUTERS = ['api.Router']
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
#SECRET_KEY = <password goes here>

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'web_api.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    #'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'management_database',
    'web_api.api',
    'sentry.client',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
)
SENTRY_KEY = 'password goes here'
SENTRY_REMOTE_URL = 'django logsentry remote URL goes here'

import logging

LOG_FILENAME = os.path.join(djangy_server_shared.LOGS_DIR, 'api.djangy.com/django.log')
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
from sentry.client.handlers import SentryHandler

logging.getLogger().addHandler(SentryHandler())

# Add StreamHandler to sentry's default so you can catch missed exceptions
logging.getLogger('sentry').addHandler(logging.StreamHandler())

