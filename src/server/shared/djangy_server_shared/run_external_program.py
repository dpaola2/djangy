import os, subprocess, sys, tempfile
from json_log import *

class RunExternalProgramException(Exception):
    """Exception trying to run external program."""
    def __init__(self, args, cause_exception):
        self.args            = args
        self.cause_exception = cause_exception
    def __str__(self):
        return 'Exception %s trying to run external program %s.' % (str(self.cause_exception), str(self.args))

def external_program_encountered_error(result):
    return result['exit_code'] != 0 # or len(result['stderr_contents']) > 0

class ExternalProgram(object):
    def __init__(self, args, cwd=None, preexec_fn=None, pass_stdin=False, pass_stdout=False, pass_stderr=False, stdin_contents=None, stderr_to_stdout=False, log_stderr=False):
        self._args             = args
        self._cwd              = cwd
        self._preexec_fn       = preexec_fn
        self._pass_stdin       = pass_stdin
        self._pass_stdout      = pass_stdout
        self._pass_stderr      = pass_stderr
        self._stdin_contents   = stdin_contents
        self._stderr_to_stdout = stderr_to_stdout
        self._log_stderr       = log_stderr
        self._has_started      = False
        self._has_finished     = False
    def run(self):
        self.start()
        return self.finish()
    def start(self):
        if self._has_started:
            return
        self._has_started = True
        try:
            # Flush output if necessary
            if self._pass_stdout:
                sys.stdout.flush()
            if self._pass_stderr:
                sys.stderr.flush()
            # Create temporary files to redirect stdin/stdout/stderr
            temp_stdin       = tempfile.NamedTemporaryFile()
            self._temp_stdout = tempfile.NamedTemporaryFile()
            self._temp_stderr = tempfile.NamedTemporaryFile()
            # After fork(), we will run this to redirect stdin/stdout/stderr
            def run_process_preexec_fn():
                if not self._pass_stdin and self._stdin_contents == None:
                    os.dup2(os.open(temp_stdin.name, os.O_RDONLY), 0)
                if not self._pass_stdout:
                    os.dup2(os.open(self._temp_stdout.name, os.O_WRONLY), 1)
                if not self._pass_stderr:
                    if self._stderr_to_stdout:
                        os.dup2(1, 2)
                    else:
                        os.dup2(os.open(self._temp_stderr.name, os.O_WRONLY), 2)
                if self._preexec_fn != None:
                    self._preexec_fn()
            # Start the subprocess--calls above function.
            self._stdin_flag = None
            if self._stdin_contents != None:
                self._stdin_flag = subprocess.PIPE
            self._process = subprocess.Popen(self._args, preexec_fn=run_process_preexec_fn, \
                executable=self._args[0], close_fds=True, shell=False, cwd=self._cwd, stdin=self._stdin_flag)
            if self._stdin_contents != None:
                self._process.stdin.write(self._stdin_contents)
                self._process.stdin.close()
        except Exception as e:
            # Couldn't run external program.  Log the exception.
            log_last_exception('external_program_args', self._args)
            raise RunExternalProgramException(self._args, e)

    def finish(self):
        if self._has_finished or not self._has_started:
            return None
        self._has_finished = True
        try:
            # Run the subprocess to completion
            pid = self._process.pid
            exit_code = self._process.wait()
            # Read out stdout/stderr
            stdout_contents = self._temp_stdout.read()
            stderr_contents = self._temp_stderr.read()
            # Close stdout/stderr
            self._temp_stdout.close()
            self._temp_stderr.close()
            # Return full results
            result = { \
                'pid'            : pid, \
                'exit_code'      : exit_code, \
                'stdout_contents': stdout_contents, \
                'stderr_contents': stderr_contents \
            }
            # (but first, log any error)
            if external_program_encountered_error(result):
                if self._log_stderr:
                    log_external_program_log_stderr(self._args, result)
                else:
                    log_external_program(self._args, result)
            return result
        except Exception as e:
            # Couldn't run external program.  Log the exception.
            log_last_exception('external_program_args', self._args)
            raise RunExternalProgramException(self._args, e)

def run_external_program(*args, **kwargs):
    return ExternalProgram(*args, **kwargs).run()
