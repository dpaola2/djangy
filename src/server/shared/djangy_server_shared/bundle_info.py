from ConfigParser import RawConfigParser

def write_params(file_path, section_name, **params):
    config = RawConfigParser()
    config.add_section(section_name)
    for (k, v) in params.items():
        config.set(section_name, k, str(v))
    f = open(file_path, 'w')
    config.write(f)
    f.close()

class BundleInfo(object):
    def __init__(self, django_project_path, django_admin_media_path, \
        admin_media_prefix, admin_email, setup_uid, web_uid, cron_uid, \
        app_gid, user_settings_module_name, db_host, db_port, db_name, \
        db_username, db_password):

        self.django_project_path       = django_project_path
        self.django_admin_media_path   = django_admin_media_path
        self.admin_media_prefix        = admin_media_prefix
        self.admin_email               = admin_email
        self.setup_uid                 = setup_uid
        self.web_uid                   = web_uid
        self.cron_uid                  = cron_uid
        self.app_gid                   = app_gid
        self.user_settings_module_name = user_settings_module_name
        self.db_host                   = db_host
        self.db_port                   = db_port
        self.db_name                   = db_name
        self.db_username               = db_username
        self.db_password               = db_password

    def save_to_file(self, file_path):
        write_params(file_path, 'bundle_info', \
            django_project_path       = self.django_project_path, \
            django_admin_media_path   = self.django_admin_media_path, \
            admin_media_prefix        = self.admin_media_prefix, \
            admin_email               = self.admin_email, \
            setup_uid                 = self.setup_uid, \
            web_uid                   = self.web_uid, \
            cron_uid                  = self.cron_uid, \
            app_gid                   = self.app_gid, \
            user_settings_module_name = self.user_settings_module_name, \
            db_host                   = self.db_host, \
            db_port                   = self.db_port, \
            db_name                   = self.db_name, \
            db_username               = self.db_username, \
            db_password               = self.db_password)

    @staticmethod
    def load_from_file(file_path):
        parser = RawConfigParser()
        parser.read(file_path)
        return BundleInfo( \
            django_project_path       = parser.get('bundle_info', 'django_project_path'), \
            django_admin_media_path   = parser.get('bundle_info', 'django_admin_media_path'), \
            admin_media_prefix        = parser.get('bundle_info', 'admin_media_prefix'), \
            admin_email               = parser.get('bundle_info', 'admin_email'), \
            setup_uid                 = int(parser.get('bundle_info', 'setup_uid')), \
            web_uid                   = int(parser.get('bundle_info', 'web_uid')), \
            cron_uid                  = int(parser.get('bundle_info', 'cron_uid')), \
            app_gid                   = int(parser.get('bundle_info', 'app_gid')), \
            user_settings_module_name = parser.get('bundle_info', 'user_settings_module_name'), \
            db_host                   = parser.get('bundle_info', 'db_host'), \
            db_port                   = int(parser.get('bundle_info', 'db_port')), \
            db_name                   = parser.get('bundle_info', 'db_name'), \
            db_username               = parser.get('bundle_info', 'db_username'), \
            db_password               = parser.get('bundle_info', 'db_password'))
