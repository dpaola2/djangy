#! /usr/bin/env python

"""
    Djangy system correctness test cases.

    When you run this file, additional output will go to log files in the
    test_logs directory.
"""

import os, os.path, random, shutil, sys, time
#from fabric.api import *
import fetch_url, urls
from testlib import *
from time import sleep

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DJANGY_SRC_DIR = os.path.dirname(TEST_DIR)
os.environ['PATH'] = os.environ['PATH'] + ':' + os.path.join(DJANGY_SRC_DIR, 'src/client')

def random_application_name():
    return 'testapp' + str(random.randrange(10000000, 99999999))

@in_temp_dir
def test_cases():
    create_djangy_client_virtualenv()
    test_urls(urls.urls)
    assert test_create() # If test_create() fails, don't run the other test cases
    test_recreate()
    assert test_update()
    test_cache()
    test_logs()
    test_syncdb()
    test_migrate()

def create_djangy_client_virtualenv():
    cwd = os.getcwd()
    call('virtualenv', 'python-virtual')
    os.environ['PATH'] = '%s:/usr/bin:/bin' % os.path.join(cwd, "python-virtual", "bin")
    os.chdir(os.path.join(DJANGY_SRC_DIR, 'src', 'client'))
    call('make')
    os.chdir(cwd)

@testcase
def test_create():
    global application_name, repository_path
    # Make a new application
    log('[%s]' % time.ctime())
    (application_name, repository_path) = make_application('testapp')
    # Copy in code (as a subdirectory -- also need to test as direct contents)
    log('[%s]' % time.ctime())
    shutil.copytree(os.path.join(TEST_DIR, 'data', 'testapp-v1'), os.path.join(repository_path, 'testapp'))
    # Add code and djangy.config to git repository
    log('[%s]' % time.ctime())
    commit_code('initial version')
    # Push application to djangy
    log('[%s]' % time.ctime())
    push_code()
    # Check the website.
    log('[%s]' % time.ctime())
    check_website(application_name, 'testapp.main')
    log('[%s]' % time.ctime())
    return True

@testcase
def test_recreate():
    # Try to make the application a second time (should fail)
    call('djangy', 'create', should_fail=True)

@testcase
def test_update():
    global application_name, repository_path
    # Update code, move it to root level
    #shutil.rmtree(os.path.join(repository_path, 'testapp'))
    #shutil.copytree(, )
    call_list(['git', 'mv'] + listdir_path('testapp') + ['.'])
    call('/bin/bash', '-c', 'cp -r %s/* %s' % (os.path.join(TEST_DIR, 'data', 'testapp-v2'), repository_path))
    commit_code('updated version')
    # Push application to djangy
    push_code()
    # Check the website.
    check_website(application_name, 'testapp.main second edition')
    return True

@testcase
def test_cache():
    global application_name, repository_path
    # Check the website.
    log('Checking static web data is cached...')
    url = 'http://%s.djangy.com/site_media/index.html' % application_name
    log('url: %s' % url)
    headers1 = fetch_url.fetch_url_headers('api.djangy.com', url)
    log('headers1: %s' % str(headers1))
    time.sleep(2)
    headers2 = fetch_url.fetch_url_headers('api.djangy.com', url)
    log('headers2: %s' % str(headers2))
    assert headers1['Cache-Control'] == 'max-stale=600'
    assert headers1['Date']          != headers2['Date']
    assert headers1['Last-Modified'] == headers2['Last-Modified']
    assert headers1['Expires']       == headers2['Expires']

@testcase
def test_logs():
    # Check logs
    logs = call('djangy', 'logs')
    logs.index('DJANGY LOG')

@testcase
def test_syncdb():
    # Check syncdb
    call('/bin/bash', '-c', 'cp -r %s/* %s' % (os.path.join(TEST_DIR, 'data', 'testapp-v3'), repository_path))
    commit_code('test syncdb')
    # Push application to djangy
    push_code()
    # run syncdb
    output = call('djangy', 'manage.py', 'syncdb', stdin_contents="no")
    # Check the website.
    check_website(application_name, 'bar', resource="add_foo")
    return (application_name, repository_path)

@testcase
def test_migrate():
    # Check migrate
    (application_name, repository_path) = make_application('testapp')
    # Copy in code (as a subdirectory -- also need to test as direct contents)
    shutil.copytree(os.path.join(TEST_DIR, 'data', 'testapp-v4'), os.path.join(repository_path, 'testapp'))
    # Add code and djangy.config to git repository
    commit_code('initial version')
    # Push application to djangy
    push_code()
    # run syncdb
    output = call('djangy', 'manage.py', 'syncdb', stdin_contents="no")
    # run migrate
    output = call('djangy', 'manage.py', 'migrate')
    # Check the website.
    check_website(application_name, 'bar', resource="add_foo")
    return (application_name, repository_path)

def make_application(rootdir):
    # Choose an application name
    application_name = random_application_name()
    repository_path = os.path.join(os.getcwd(), application_name)
    os.mkdir(repository_path)
    os.chdir(repository_path)
    # Create a git repository
    call('git', 'init')
    # Create a djangy.config file
    create_file('djangy.config', '[application]\napplication_name=%s\nrootdir=%s\n' % (application_name, rootdir))
    commit_code('djangy.config')
    # Create a djangy application
    call('djangy', 'create')
    return (application_name, repository_path)

def create_file(file_path, file_contents):
    file = open(file_path, 'w')
    file.write(file_contents)
    file.close()

def commit_code(commit_message):
    call('git', 'add', '.')
    call('git', 'commit', '-m', commit_message)

def push_code():
    # Push application to djangy
    call('git', 'push', 'djangy', 'master')
    sleep(1)

def check_website(application_name, expected_output, resource=""):
    log('Checking website output...',)
    url = "http://%s.djangy.com/%s" % (application_name, resource)
    log("Using URL: %s" % url)
    result = fetch_url.fetch_url_body('api.djangy.com', url)
    log("Expected output: %s" % expected_output)
    log("Actual Output: %s" % result)
    assert result == expected_output
    log('Website output matched.')

def listdir_path(dir_path):
    return map(lambda x: os.path.join(dir_path, x), os.listdir(dir_path))

if __name__ == '__main__':
    try:
        test_cases()
    except KeyboardInterrupt:
        pass
