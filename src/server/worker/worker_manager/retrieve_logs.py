#!/usr/bin/env python

from shared import *
from mako.template import Template
from mako.lookup import TemplateLookup
import os

def main():
    try:
        check_trusted_uid(sys.argv[0])
        kwargs = check_and_return_keyword_args(sys.argv, ['application_name', 'bundle_version'])

        application_name    = kwargs['application_name']
        bundle_version      = kwargs['bundle_version']
        retrieve_logs(application_name, bundle_version)
    except:
        log_last_exception()

def retrieve_logs(application_name, bundle_version):
    bundle_name = application_name + '-' + bundle_version
    django_log_path = os.path.join(LOGS_DIR, bundle_name, "django.log")
    error_log_path = os.path.join(LOGS_DIR, bundle_name, "error.log")

    django_log = open(django_log_path).read()
    error_log = open(error_log_path).read()

    lookup = TemplateLookup(directories = [WORKER_TEMPLATE_DIR])
    template = lookup.get_template('logs.txt')
    instance = template.render(
        django_log = django_log, 
        error_log = error_log
    )
    print instance

if __name__ == '__main__':
    main()
