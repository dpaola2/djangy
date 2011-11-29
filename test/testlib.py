"""
    Library of functions useful for writing test cases.
"""

import os, os.path, shutil, subprocess, sys, tempfile, traceback, urllib2

log_dir = os.path.join(os.getcwd(), 'test_logs')
if not os.path.isdir(log_dir):
    os.makedirs(log_dir)
test_log_file = None

def log(message):
    global test_log_file
    if test_log_file:
        test_log_file.write(message + '\n')
    else:
        print message

def testcase(func):
    """Decorator for test cases"""
    test_case_name = func.func_name
    def handle_exception(e):
        log(traceback.format_exc(e))
        print 'FAILED'
        return False
    def test_case_func(*args, **kwargs):
        global test_log_file
        try:
            test_log_file = open(os.path.join(log_dir, test_case_name + '.log'), 'w')
            print ('%s...' % test_case_name),
            sys.stdout.flush()
            log('BEGIN TEST CASE %s' % test_case_name)
            log('')
            func(*args, **kwargs)
            print 'OK'
            return True
        except Exception as e:
            return handle_exception(e)
        except KeyboardInterrupt as e:
            return handle_exception(e)
        except AssertionError as e:
            return handle_exception(e)
        finally:
            log('')
            log('END TEST CASE %s' % test_case_name)
            test_log_file.close()
    return test_case_func

def in_temp_dir(func):
    """Decorator for functions which need to run in a temporary scratch directory"""
    def in_temp_dir_func(*args, **kwargs):
        tempdir = tempfile.mkdtemp()
        #homedir = os.environ['HOME']
        olddir = os.getcwd()
        try:
            os.chdir(tempdir)
            #os.environ['HOME'] = tempdir
            #ssh_dir = os.path.join(tempdir, '.ssh')
            #os.mkdir(ssh_dir)
            #subprocess.call(['ssh-keygen', '-N', '', '-f', os.path.join(tempdir, '.ssh', 'id_rsa')])
            #subprocess.call(['cp', os.path.join(TEST_DIR, test.djangy), os.path.join(tempdir, '.djangy')])
            return func(*args, **kwargs)
        finally:
            os.chdir(olddir)
            #os.environ['HOME'] = homedir
            if os.path.dirname(tempdir) == '/tmp':
                shutil.rmtree(tempdir)
    return in_temp_dir_func

def call(*args, **kwargs):
    return call_list(list(args), **kwargs)

def call_list(args, should_fail=False, stdin_contents=None):
    log('Calling %s' % ' '.join(args))
    p = subprocess.Popen(list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    if stdin_contents:
        p.stdin.write(stdin_contents)
        p.stdin.close()
    output = p.stdout.read()
    log(output)
    if should_fail:
        assert p.wait() != 0
    else:
        assert p.wait() == 0
    return output

def test_url(url, expected_status_code=200, validation_function=None):
    try:
        response = urllib2.urlopen(url)
        if expected_status_code != 200:
            return False
        if validation_function:
            return validation_function(response.read())
        else:
            return True
    except urllib2.HTTPError as error:
        return error.code == expected_status_code

def test_urls(urls):
    for url in urls:
        print ('%s...' % url),
        if test_url(url):
            print 'OK'
        else:
            print 'FAILED'
