import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'orm.settings'
from orm.models import *

def lock_application(func):
    def lock_and_call(application_name, *args, **kwargs):
        lock = LocalApplicationLocks.lock(application_name)
        try:
            func(application_name, *args, **kwargs)
        finally:
            LocalApplicationLocks.unlock(lock)
    return lock_and_call
