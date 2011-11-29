class Router(object):
    """ Router to tell the application when to use the management_database and when to use the 'default' database.
    see http://docs.djangoproject.com/en/1.2/topics/db/multi-db/
    """

    def check_for_md(self, model, **hints):
        if model._meta.app_label == 'management_database':
            return 'management_database'
        return None

    db_for_read = check_for_md
    db_for_write = check_for_md

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label == obj1._meta.app_label):
            return True
        return False

    def allow_syncdb(self, db, model):
        """ Keep the management database from being synchronized here."""
        if model._meta.app_label == 'management_database':
            return False
        return None
