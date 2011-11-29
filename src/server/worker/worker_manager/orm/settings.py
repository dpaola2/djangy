import djangy_server_shared, os.path

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(djangy_server_shared.WORKER_MANAGER_VAR_DIR, 'worker_manager.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}

INSTALLED_APPS = (
    'orm',
    'south',
)
