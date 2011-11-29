DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangy',
        'USER': 'djangy',
        'PASSWORD': 'password goes here',
        'HOST': '',
        'PORT': ''
    }
}

INSTALLED_APPS = (
    'management_database',
    'south'
)
