#!/usr/bin/env python
#
# Can be used when installing/upgrading to rebuild all bundles and deploy
# their applications.  Not very fast.
#

from shared import *

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # If the user provided arguments, look up those individual
        # applications.
        applications = []
        for application_name in sys.argv[1:]:
            applications.extend(list(Application.objects.filter(deleted=None, name=application_name)))
    else:
        # No user arguments, so deploy all applications.
        applications = Application.objects.filter(deleted=None)

    for application in applications:
        # Two step deployment (in case the process table is empty)
        run_external_program(['/srv/djangy/run/master_manager/setuid/run_deploy',
            'application_name', application.name], pass_stdout=True)
        allocate_workers(application)
