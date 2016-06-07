import time
import os
import datetime
import logging

LOG_PATH = 'c:\\UCX\\ApplicationLogs'
#LOG_PATH = '/tmp/ucxlog'

def getCurrentTimeStamp():
    micro_seconds = ".3f"
    return time.strftime("%Y-%m-%d %H:%M:%S.", time.localtime()) + \
           str(datetime.datetime.now().microsecond / 1000).zfill(3)


def getCurrentTime():
    return time.strftime("%Y-%m-%d%H%M%S", time.localtime())


class Logger(object):
    def __init__(self, appName=None, logFile=None):
        self.log_file = logFile

    def log_header(self, line):
        with open(self.log_file, 'a') as f:
            f.write(line + '\n')
            f.flush()

    def log(self, line):
        with open(self.log_file, 'a') as f:
            f.write(getCurrentTimeStamp() + ', ' + line + '\n')
            f.flush()
