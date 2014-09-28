'''
Created Apr 3, 2013
@author: linhnv1
'''
import threading
import time
import datetime
import os
import signal
import subprocess


class TimeoutThread(threading.Thread):
    """Timeout thread class"""
    def __init__(self, pid, timeout=60):
        threading.Thread.__init__(self)
        self.timeout = timeout
        self.pid = pid
        self.is_stop = False
        self.start_time = None
        self.is_timed_out = False

    def run(self):
        """run thread"""
        self.start_time = datetime.datetime.now()
        while(True):
            time.sleep(0.5)
            n = datetime.datetime.now()
            if( n <= self.start_time):
                continue
            delta = n - self.start_time
            if(delta.seconds >= self.timeout):
                self.is_timed_out = True
                try:
                    os.kill(self.pid, signal.SIGTERM)
                except Exception as ex:
                    pass
                break
            if(self.is_stop):
                break


class ProcessUtil(object):
    """Subprocess utility class"""
    @staticmethod
    def run_job(cmd, timeout=60, is_shell=False):
        """Run command cmd, if duration larger than 60 secs, kill it"""
        # Print cmd:
        # print "***************CMD*************"
        # for s in cmd:
        #     print "\t" + s
        # print "*******************************"
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, shell=is_shell)
            th = TimeoutThread(p.pid, timeout)
            th.start()
            (out_str, err_str) = p.communicate()
            if(not th.is_timed_out):
                th.is_stop = True
            th.join(10)
            return (p.returncode, th.is_timed_out, out_str, err_str)
        except:
            return (-10)

    @staticmethod
    def run_job_gccarm(cmd, timeout = 60, is_shell=False):
        """Run command cmd, if duration larger than 60 secs, kill it"""
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, shell=False)
            th = TimeoutThread(p.pid, timeout)
            th.start()
            ProcessUtil.current_prs = p
            if(not th.is_timed_out):
                th.is_stop = True
            th.join(10)
            return (p.returncode, th.is_timed_out)
        except:
            return (-10)

    @staticmethod
    def kill_job(is_shell=False):
        if (ProcessUtil.current_prs is not None):
            try:
                ProcessUtil.current_prs.terminate()
                ProcessUtil.current_prs = None
                return True
            except:
                return False
        return False
