import os
from django.db import models

class LocalApplication(models.Model):

    class Meta:
        db_table = 'local_application'

    application_name = models.CharField(max_length=255, unique=True)
    bundle_version   = models.CharField(max_length=255, null=True)
    is_stopped       = models.BooleanField(default=False)
    num_procs        = models.IntegerField()
    proc_num_threads = models.IntegerField()
    proc_mem_mb      = models.IntegerField()
    proc_stack_mb    = models.IntegerField()
    celery_procs     = models.IntegerField()

class LocalApplicationLocks(models.Model):

    class Meta:
        db_table = 'local_application_locks'

    application = models.ForeignKey(LocalApplication, unique=True)
    # Diagnostic information about the lock in case it is not properly
    # unlocked and we need to track down the problem.
    pid         = models.IntegerField()
    time        = models.DateField(auto_now_add=True)

    @staticmethod
    def lock(application_name):
        """Locks an application.  Throws an exception if it is already locked."""
        try:
            application = LocalApplication.objects.get(application_name=application_name)
            lock        = LocalApplicationLocks(application=application, pid=os.getpid())
            lock.save()
            return lock
        except Exception as e:
            raise LockFailedException(application_name)

    @staticmethod
    def unlock(lock):
        """Unlocks an application.  The argument must be the return value of 
           a previous call to lock() which has not already been unlocked."""
        try:
            if lock != None:
                lock.delete()
        except Exception as e:
            raise UnlockFailedException(lock.application.application_name)

class LockFailedException(Exception):
    """Could not lock the application."""
    def __init__(self, application_name):
        self.application_name = application_name
    def __str__(self):
        return 'Could not lock the application "%s".' % self.application_name

class UnlockFailedException(Exception):
    """Could not unlock the application."""
    def __init__(self, application_name):
        self.application_name = application_name
    def __str__(self):
        return 'Could not unlock the application "%s".' % self.application_name
