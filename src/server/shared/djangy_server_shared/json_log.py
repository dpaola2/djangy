import json, os, socket, sys, time, traceback
import logging
#from sentry.client.base import SentryClient

__log_file_path__ = None
__log_file__ = None

class LogFileAlreadyOpenException(Exception):
    """Tried to open a different log file when the log file was already open."""
    def __init__(self, old_log_file, new_log_file):
        self.old_log_file = old_log_file
        self.new_log_file = new_log_file
    def __str__(self):
        return 'Tried to open new log file "%s" when old log file "%s%" was already open.' % (self.new_log_file, self.old_log_file)

def open_log_file(log_file_path, mode):
    global __log_file_path__
    global __log_file__
    if __log_file__ != None:
        if __log_file_path__ != log_file_path:
            raise LogFileAlreadyOpenException(__log_file_path__, log_file_path)
    else:
        __log_file_path__ = log_file_path
        __log_file__ = open(log_file_path, 'a')
        os.chmod(log_file_path, mode)

def __format_time_utc__(time_struct):
    return "%04i-%02i-%02i %02i:%02i:%02i.%03i UTC" % \
        (time_struct['tm_year'], time_struct['tm_mon'], time_struct['tm_mday'], \
         time_struct['tm_hour'], time_struct['tm_min'], time_struct['tm_sec'], time_struct['tm_msec'])

def __current_time_utc__():
    time_struct = time.gmtime()
    tm_msec = int(time.time() * 1000) % 1000
    time_dict = { \
        'tm_year': time_struct.tm_year, \
        'tm_mon' : time_struct.tm_mon, \
        'tm_mday': time_struct.tm_mday, \
        'tm_hour': time_struct.tm_hour, \
        'tm_min' : time_struct.tm_min, \
        'tm_sec' : time_struct.tm_sec, \
        'tm_msec': tm_msec \
    }
    return __format_time_utc__(time_dict)

def __format_list_as_struct__(list):
    out = '{'
    if len(list) % 2 == 1:
        list = list[:-1]
    for i in range(0, len(list), 2):
        if i > 0:
            out = out + ', '
        out = out + json.dumps(list[i]) + ':' + json.dumps(list[i+1])
    out = out + '}'
    return out

def __make_log_entry__(*args):
    ip = socket.gethostbyname(socket.gethostname())
    return __format_list_as_struct__(['date_time_utc', __current_time_utc__(), 'epoch_time', time.time(), \
        'host_ip', ip, 'program', sys.argv[0], 'pid', os.getpid(), 'uid', os.getuid(), 'gid', os.getgid()] \
        + list(args))

def log(*args):
    log_file = __log_file__
    if log_file == None:
        log_file = sys.stderr
    log_entry = __make_log_entry__(*args)
    log_file.write(log_entry + '\n')
    log_file.flush()

def print_or_log_usage(usage):
    if os.isatty(1):
        print usage
    else:
        log('type', 'USAGE_ERROR', 'usage', usage)

def log_info_message(message, *args):
    #SentryClient().create_from_text(message, level = logging.INFO)
    log('type', 'INFO_MESSAGE', 'message', message, *args)

def log_error_message(message, *args):
    #SentryClient().create_from_text(message, level = logging.ERROR)
    log('type', 'ERROR_MESSAGE', 'message', message, *args)

def log_warning_message(message, *args):
    #SentryClient().create_from_text(message, level = logging.WARN)
    log('type', 'WARNING_MESSAGE', 'message', message, *args)

def log_external_program(external_program_args, result, *args):
    #SentryClient().create_from_text("EXTERNAL PROGRAM ERROR: %s" % external_program_args, level = logging.ERROR)
    log('type', 'EXTERNAL_PROGRAM_ERROR', 'external_program_args', external_program_args, \
        'external_program_pid', result['pid'], 'exit_code', result['exit_code'], \
        'stdout', result['stdout_contents'], 'stderr', result['stderr_contents'], *args)

def log_external_program_log_stderr(external_program_args, result, *args):
    log('type', 'BEGIN_EXTERNAL_PROGRAM_LOG', 'external_program_args', external_program_args, \
        'external_program_pid', result['pid'], 'exit_code', result['exit_code'], \
        'stdout', result['stdout_contents'], 'stderr_follows_in_log', True, *args)
    for message in result['stderr_contents'].split('\n'):
        log(message)
    log('type', 'END_EXTERNAL_PROGRAM_LOG', 'external_program_pid', result['pid'])

def __log_exception__(exception, *args):
    log('type', 'EXCEPTION', 'class', exception.__class__.__name__, 'message', str(exception), *args)

def log_last_exception(*args):
    #SentryClient().create_from_exception()
    (_, exception, _) = sys.exc_info()
    __log_exception__(exception, 'traceback', traceback.format_exc(), *args)
