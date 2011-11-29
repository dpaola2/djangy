all: run/python-virtual run/python-virtual/bin/post_receive.py run/python-virtual/bin/git_serve.py run/python-virtual/bin/shell_serve.py setuid

run/python-virtual: src/server/master/management_database/management_database/* src/server/master/master_api/master_api/* src/server/shared/djangy_server_shared/*
	virtualenv run/python-virtual
	bash -c 'source run/python-virtual/bin/activate; easy_install Django==1.2.1 Mako==0.3.4 South==0.7.2 django-sentry==1.0.9'
	bash -c 'source run/python-virtual/bin/activate; easy_install src/server/master/management_database src/server/master/master_api src/server/shared'

run/python-virtual/bin/post_receive.py: run/python-virtual src/server/master/master_manager/post_receive.py
	cp src/server/master/master_manager/post_receive.py run/python-virtual/bin/post_receive.py
	chmod +x run/python-virtual/bin/post_receive.py

run/python-virtual/bin/git_serve.py: run/python-virtual src/server/master/master_manager/git_serve.py
	cp src/server/master/master_manager/git_serve.py run/python-virtual/bin/git_serve.py
	chmod +x run/python-virtual/bin/git_serve.py

run/python-virtual/bin/shell_serve.py: run/python-virtual src/server/master/master_manager/shell_serve.py
	cp src/server/master/master_manager/shell_serve.py run/python-virtual/bin/shell_serve.py
	chmod +x run/python-virtual/bin/shell_serve.py

setuid: run/master_manager/setuid run/proxycache_manager/setuid run/worker_manager/setuid

run/master_manager/setuid: src/server/master/master_manager/setuid/*
	rm -rf run/master_manager
	mkdir -p run/master_manager/setuid
	cd src/server/master/master_manager/setuid; make clean; make
	cp -a src/server/master/master_manager/setuid/run_* run/master_manager/setuid
	rm run/master_manager/setuid/*.c

run/proxycache_manager/setuid: src/server/proxycache/proxycache_manager/setuid/*
	rm -rf run/proxycache_manager
	mkdir -p run/proxycache_manager/setuid
	cd src/server/proxycache/proxycache_manager/setuid; make clean; make
	cp -a src/server/proxycache/proxycache_manager/setuid/run_* run/proxycache_manager/setuid
	rm run/proxycache_manager/setuid/*.c

run/worker_manager/setuid: src/server/worker/worker_manager/setuid/*
	rm -rf run/worker_manager
	mkdir -p run/worker_manager/setuid
	cd src/server/worker/worker_manager/setuid; make clean; make
	cp -a src/server/worker/worker_manager/setuid/run_* run/worker_manager/setuid
	rm run/worker_manager/setuid/*.c

clean:
	rm -rf run
	rm -rf src/server/master/management_database/temp src/server/master/management_database/build src/server/master/management_database/management_database.egg-info
	rm -rf src/server/master/master_api/temp src/server/master/master_api/build src/server/master/master_api/master_api.egg-info
	rm -rf src/server/shared/temp src/server/shared/build src/server/shared/djangy_server_shared.egg-info
	-find * -name '*.pyc' | xargs rm
	-find * -name '*~' | xargs rm
