from django.db import models
from django.db.utils import IntegrityError
from datetime import datetime

class WhiteList(models.Model):
    class Meta:
        db_table = 'whitelist'

    email = models.CharField(max_length=255) # Shouldn't this be unique=True?
    invite_code = models.CharField(max_length=255)
    referrer = models.ForeignKey('User', blank = True, default = None, null = True)

    @staticmethod
    def verify(email, invite_code):
        try:
            wl = WhiteList.objects.get(email=email)
            if wl.invite_code == invite_code:
                return True
        except:
            pass
        return False

class User(models.Model):
    class Meta:
        db_table = 'user'

    email = models.CharField(max_length=255, unique=True)
    passwd = models.CharField(max_length=255)
    admin = models.BooleanField(default=False)
    customer_id = models.CharField(max_length=255)
    referrer = models.ForeignKey('User', blank = True, default = None, null = True)
    invite_limit = models.IntegerField(default=0)
    first_name = models.CharField(max_length=255, blank = True, default = None, null = True)
    last_name = models.CharField(max_length=255, blank = True, default = None, null = True)

    @staticmethod
    def get_by_email(email):
        try:
            return User.objects.get(email=email)
        except:
            return None

    def add_ssh_public_key(self, ssh_public_key, comment):
        if not SshPublicKey.objects.filter(user=self, ssh_public_key=ssh_public_key).exists():
            SshPublicKey(user=self, ssh_public_key=ssh_public_key, comment=comment).save()

    def get_ssh_public_keys(self):
        return self.sshpublickey_set.all()

    def remove_ssh_public_key(self, key_id):
        self.sshpublickey_set.filter(id=key_id).delete()

    def get_accessible_applications(self):
        owned_applications = list(self.application_set.filter(deleted=None).all())
        collaborating_applications = filter(lambda x: x.deleted==None, \
            [x.application for x in self.collaborator_set.select_related(depth=1)])
        applications = owned_applications + collaborating_applications
        applications.sort(cmp=lambda x, y: cmp(x.name, y.name))
        return applications

    def get_subscriptions(self):
        subs = []
        apps = self.application_set.all()
        for app in apps:
            subs += list(app.subscription_set.all())
        return subs

    def get_active_subscriptions(self):
        subs = []
        apps = self.application_set.all()
        for app in apps:
            subs += list(app.subscription_set.filter(disabled=None))
        return subs

class SshPublicKey(models.Model):
    class Meta:
        db_table = 'ssh_public_key'

    user = models.ForeignKey(User)
    ssh_public_key = models.CharField(max_length=1024)
    comment = models.CharField(max_length=64)

    @staticmethod
    def get_users_by_public_key_id(id):
        # Two-step process in case two users have the same SSH public key.
        ssh_public_key = SshPublicKey.objects.get(id=id).ssh_public_key
        return [x.user for x in SshPublicKey.objects.filter(ssh_public_key=ssh_public_key)]

class ActiveApplicationName(models.Model):
    class Meta:
        db_table = 'active_application_name'

    name = models.CharField(max_length=255, unique=True)

class Application(models.Model):
    class Meta:
        db_table = 'application'

    account = models.ForeignKey(User)
    bundle_version = models.CharField(max_length=255,default='')
    name = models.CharField(max_length=255)
    db_name = models.CharField(max_length=255)
    db_username = models.CharField(max_length=255)
    db_password = models.CharField(max_length=255)
    db_host = models.CharField(max_length=255)
    db_port = models.IntegerField(default=3306)
    db_max_size_mb = models.IntegerField(default=5)
    setup_uid = models.IntegerField(default=-1)
    web_uid = models.IntegerField(default=-1)
    cron_uid = models.IntegerField(default=-1)
    app_gid = models.IntegerField(default=-1)
    num_procs = models.IntegerField(default=1)
    proc_num_threads = models.IntegerField(default=20)
    proc_mem_mb = models.IntegerField(default=64)
    proc_stack_mb = models.IntegerField(default=2)
    cache_index_size_kb = models.IntegerField(default=64)
    cache_size_kb = models.IntegerField(default=16384)
    debug = models.BooleanField(default=False)
    deleted = models.DateTimeField(null=True, blank=True)
    celery_procs = models.IntegerField(default=0)

    @staticmethod
    def get_by_name(name):
        try:
            return Application.objects.get(name=name, deleted=None)
        except:
            return None

    def mark_deleted(self):
        if not self.deleted:
            self.deleted = datetime.now()
        self.save()
        self.process_set.all().delete()
        self.virtualhost_set.all().delete()
        try:
            ActiveApplicationName.objects.get(name=self.name).delete()
        except:
            pass

    def report_allocation_change(self, chargable, quantity):
        alloc = AllocationChange(application = self, chargable = chargable, quantity = quantity)
        alloc.save()

    def has_collaborator(self, user):
        return Collaborator.objects.filter(application=self, user=user).exists()

    def accessible_by(self, user):
        return (self.deleted == None) and ((user.admin == True) or (self.account == user) or self.has_collaborator(user))

    def accessible_by_any_of(self, users):
        return any([self.accessible_by(u) for u in users])

    def add_collaborator(self, email):
        user = User.get_by_email(email)
        if not user:
            raise NoUserException(email)
        if not self.deleted and (self.account != user) \
        and not Collaborator.objects.filter(application=self, user=user).exists():
            collaborator = Collaborator(application=self, user=user)
            collaborator.save()
            return True
        else:
            return False

    def remove_collaborator(self, email):
        user = User.get_by_email(email)
        if user and not self.deleted:
            try:
                Collaborator.objects.get(application=self, user=user).delete()
            except:
                pass

    def get_collaborators(self):
        """ Returns email addresses of collaborators on this application (not including the owner). """
        return [c.user.email for c in self.collaborator_set.all()]

    def is_server_cache_enabled(self):
        return self.cache_size_kb > 0

    def enable_server_cache(self):
        self.cache_index_size_kb = 64
        self.cache_size_kb = 16384
        self.save()

    def disable_server_cache(self):
        self.cache_index_size_kb = 0
        self.cache_size_kb = 0
        self.save()

    def add_domain_name(self, domain_name):
        if domain_name not in VirtualHost.get_virtualhosts_by_application(self):
            VirtualHost(application = self, virtualhost = str(domain_name)).save()

    def delete_domain_name(self, domain_name):
        VirtualHost.objects.filter(application = self, virtualhost = str(domain_name)).delete()

class NoUserException(Exception):
    def __init__(self, email):
        self.email = email
    def __str__(self):
        return 'No user exists with email address %s' % self.email

class Collaborator(models.Model):
    class Meta:
        db_table = 'collaborator'
        unique_together = [('application', 'user')]

    application = models.ForeignKey(Application)
    user = models.ForeignKey(User)

class WorkerHost(models.Model):
    class Meta:
        db_table = 'worker_host'

    host = models.CharField(max_length=255, unique=True)
    max_procs = models.IntegerField(default=100)
    # In the future, we may want to distinguish between hosts used by paid
    # users vs. free users, and offer paid users better service while packing
    # as many free users as possible onto a host.

class Process(models.Model):
    class Meta:
        db_table = 'process'
        unique_together = [('application', 'proc_type', 'host'), ('host', 'port')]

    application = models.ForeignKey(Application)
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=20000)
    num_procs = models.IntegerField(default=1)
    proc_type = models.CharField(max_length=64, default='gunicorn')

    @staticmethod
    def get_hosts_ports_by_application(application):
        try:
            return [(process.host, process.port) for process in application.process_set.all()]
        except:
            return None

class Chargable(models.Model):
    class Meta:
        db_table = 'chargable'
    
    component = models.IntegerField(default=0)
    price = models.IntegerField(default=0)

    components = {
        'application_processes': 0,
        'background_processes':1
    }
    @staticmethod
    def get_by_component(name):
        try:
            return Chargable.objects.get(component=Chargable.components[name])
        except:
            return None

    @staticmethod
    def get_by_id(id):
        try:
            return Chargable.objects.get(component=id)
        except:
            return None

    def __str__(self):
        reverse = dict((v,k) for k, v in self.components.iteritems())
        return reverse[self.component]


class AllocationChange(models.Model):
    class Meta:
        db_table = 'allocation_change'

    application = models.ForeignKey(Application)
    chargable = models.ForeignKey(Chargable, null=True)
    quantity = models.IntegerField()
    billed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class ProxyCache(models.Model):
    class Meta:
        db_table = 'proxycache'

    application = models.ForeignKey(Application)
    host = models.CharField(max_length=255)

    @staticmethod
    def get_proxycache_hosts_by_application_name(name):
        return ProxyCache.get_proxycache_hosts_by_application(Application.get_by_name(name))

    @staticmethod
    def get_proxycache_hosts_by_application(application):
        try:
            return [proxycache.host for proxycache in application.proxycache_set.all()]
        except:
            return None

class VirtualHost(models.Model):
    class Meta:
        db_table = 'virtualhost'
        unique_together = [('application', 'virtualhost')]

    application = models.ForeignKey(Application)
    virtualhost = models.CharField(max_length=255)

    @staticmethod
    def get_virtualhosts_by_application_name(name):
        return VirtualHost.get_virtualhosts_by_application(Application.get_by_name(name))

    @staticmethod
    def get_virtualhosts_by_application(application):
        try:
            return [virtualhost.virtualhost for virtualhost in application.virtualhost_set.all()]
        except:
            return None

class BillingEvent(models.Model):
    class Meta:
        db_table = 'billingevent'

    email = models.CharField(max_length=255)
    customer_id = models.CharField(max_length=255)
    application_name = models.CharField(max_length=255)
    chargable_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    cents = models.IntegerField()
    success = models.BooleanField()
    memo = models.CharField(max_length=255, blank=True, null=True)

class SubscriptionType(models.Model):
    class Meta:
        db_table = 'subscriptiontype'

    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)

    @staticmethod
    def get_by_name(name):
        return SubscriptionType.objects.get(name=name)

class Subscription(models.Model):
    class Meta:
        db_table = 'subscription'

    application = models.ForeignKey(Application)
    subscription_type = models.ForeignKey(SubscriptionType)
    price = models.IntegerField(blank=True, null=True, default=0)
    enabled = models.DateTimeField(auto_now_add=True)
    disabled = models.DateTimeField(blank=True, null=True, default=None)

    @staticmethod
    def subscribe(application, subscription_name, price=None):
        assert not Subscription.is_subscribed(application, subscription_name)
        subscription_type = SubscriptionType.get_by_name(subscription_name)
        if price == None:
            price = subscription_type.price
        Subscription(application=application, subscription_type=subscription_type, price=price).save()

    @staticmethod
    def is_subscribed(application, subscription_name):
        subscription_type = SubscriptionType.get_by_name(subscription_name)
        return Subscription.objects.filter(application=application, subscription_type=subscription_type, disabled=None).exists()

    @staticmethod
    def unsubscribe(application, subscription_name):
        subscription_type = SubscriptionType.get_by_name(subscription_name)
        for s in Subscription.objects.filter(application=application, subscription_type=subscription_type, disabled=None):
            s.disabled = datetime.now()
            s.save()
