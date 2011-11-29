import os.path
from core import *

@print_when_used
def require_apache():
    run_ignore_failure('/etc/init.d/apache2', 'stop')
    run('a2enmod', 'ssl')
    require_file('/etc/apache2/ports.conf', 'root', 'root', 0644, contents=read_file('conf/apache/ports.conf'), overwrite=True)
    for (site, apache_conf) in [('000-defaults',   '/srv/djangy/install/conf/apache/000-defaults/config/apache.conf'), \
                                ('api.djangy.com', '/srv/djangy/src/server/master/web_api/config/apache.conf'       ), \
                                ('djangy.com',     '/srv/djangy/src/server/master/web_ui/config/apache.conf'        )]:
        assert os.path.exists(apache_conf)
        require_link(os.path.join('/etc/apache2/sites-available', site), apache_conf)
        require_link(os.path.join('/etc/apache2/sites-enabled', site), os.path.join('/etc/apache2/sites-available', site))
    run_ignore_failure('/etc/init.d/apache2', 'start')

@print_when_used
def require_no_apache():
    if os.path.isfile('/etc/init.d/apache2'):
        run_ignore_failure('/etc/init.d/apache2', 'stop')
