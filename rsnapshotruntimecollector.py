#!/usr/bin/python

"""
rsnapshot_runtime_diamond.py
A script that parses rsnapshot logs to determine runtimes between
rsnapshot execution to it's completion. 

self.publish(metric, value)
"""

import sys
import os
import argparse
import logging
import time
import socket
import pickle
from subprocess import Popen, PIPE
from datetime import datetime
import diamond.collector

class RsnapshotRuntimeCollector(diamond.collector.Collector):
    def get_default_config_help(self):
        config_help = super(RsnapshotRuntimeCollector,
                            self).get_default_config_help()
        config_help.update({
            'rsnap_log_home':
                'Path to base directory of rsnap logs'
        ' name. Defaults to "%s"' % RSNAP_LOG_HOME,
        })
        return config_help
         
    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(RsnapshotRuntimeCollector, self).get_default_config()
        config.update({
	    'rsnap_log_home': None,
        })
        return config

    def get_log_list(self, rsnap_log_home):
        """     
        Get the list of rsnapshot log from /var/log/
        """
        ls_log = "ls %s" % rsnap_log_home
        ls_log_cmd = ls_log.split()
        try:
            logs = Popen(ls_log_cmd, stdout=PIPE, stderr=PIPE)
            logs_out, logs_err = logs.communicate()
            if not logs_out and not logs_err:
                self.log.debug("list command returned Null Output or Errors.")
            elif not logs_out:
                self.log.debug("No list infromation was returned.")
            elif logs_err.rstrip():
                self.log.critical("Hostname command error "
                                "(hostname -s): <<%s>>" % logs_err)
            log_list = logs_out
            return log_list
        except Exception as e:
            self.log.critical("Caught and exception running"
                            " list command (ls rsnap_log_home)!")
            self.log.critical("%s" % e)

    def get_job_times(self, log_path):
        self.log.debug("looking at log: %s" % log_path)
        date_format = "%d/%b/%Y:%H:%M:%S"
        start_times = []
        end_times = []
        echo_count = 0
        with open(log_path) as f:
            for line in f:
                if 'echo' in line:
                    echo_count += 1
                    start_date = line.split()[0].strip("[").strip("]")
                    startd = datetime.strptime(start_date, date_format)
                    start_times.append(startd)
                elif '.pid' in line and 'rm' in line:
                    if echo_count > 1:
                        echo_pop = echo_count - 1
                        for count in range(echo_pop):
                            del start_times[-2]
                    echo_count = 0
                    end_date = line.split()[0].strip("[").strip("]")
                    endd = datetime.strptime(end_date, date_format)
                    end_times.append(endd)
        return [start_times, end_times]

    def parse_job_durations(self, log_path, start_times, end_times):
        graph_list = []
        log_name = log_path.split('/')[-1].replace(".log", "")
        if len(start_times) == (len(end_times) + 1):
            del start_times[-1]
        self.log.debug("Lenght of Rsnap start "
                     "times: %s" % (len(start_times)))
        self.log.debug("Lenght of Rsnap start "
                     "times: %s" % (len(end_times)))
        if len(start_times) == len(end_times) and \
           len(start_times) != 0 or len(end_times) != 0:
            duration = [end_i - start_i for end_i, start_i in
                        zip(end_times, start_times)]
            for end, times in zip(end_times, duration):
                end_epoch = end.strftime('%s')
                metric = self.total_secs(times)
                ## This only works in Python 2.7.x
                #metric = int(times.total_seconds())
                #graph_list = "%s %s %s\n" \
                #    % (log_name, metric, end_epoch)
                #graph_list.append(graph_list)
        return [log_name, metric]   
        if len(start_times) > (len(end_times) + 1):
            self.log.critical("Can't parse this logs properly. You may want to "
                            "clear it.: %s" % log_path)

    def total_secs(self, times):
        metric = int((times.days * 86400) + times.seconds)
        return metric

    def collect(self): 
        self.log_list = self.get_log_list(self.config['rsnap_log_home'])
        for log in self.log_list.splitlines():
            self.log_path = os.path.join(self.config['rsnap_log_home'], log) 
            start_times, end_times = self.get_job_times(self.log_path)
            #for i in range(0, len(start_times)):
            #    self.log.debug("%s: %s" % (i, start_times[i]))
            #for i in range(0, len(end_times)):
            #    self.log.debug("%s: %s" % (i, end_times[i]))
            metric_name, metric_value = self.parse_job_durations(self.log_path, start_times, end_times)
            #log.self.debug("publishing: %s %s", %(log_name, metric_value))
            if metric_value > 0:
	        self.publish(metric_name , metric_value)
