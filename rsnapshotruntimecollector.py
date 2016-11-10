#!/usr/bin/python

"""
rsnapshot_runtime_diamond.py
A script that parses rsnapshot logs to determine runtimes between
rsnapshot execution to it's completion.
"""

import os
import logging
from subprocess import Popen, PIPE
from datetime import datetime
import diamond.collector


class RsnapshotRuntimeCollector(diamond.collector.Collector):
    def get_default_config_help(self):
        """
        Seting up help values for custom entry
        """
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

    def collect(self):
        """
        Looping over all rsnap logs and publishing deltas
        """
        date_format = "%d/%b/%Y:%H:%M:%S"
        root_dir = self.config['rsnap_log_home']
        metrics = {}
        for log in sorted(os.listdir(root_dir)):
            for line in reversed(open(os.path.join(root_dir, log))
                                 .readlines()):
                if '.pid' in line and 'rm' in line:
                    end_date = line.split()[0].strip("[").strip("]")
                    endd = datetime.strptime(end_date, date_format)
                elif 'echo' in line and '.pid' in line:
                    start_date = line.split()[0].strip("[").strip("]")
                    startd = datetime.strptime(start_date, date_format)
                    break
            if endd and startd:
                duration = endd - startd
                metric_value = abs(int((duration.days * 86400) +
                                       duration.seconds))
                metrics[os.path.splitext(log)[0]] = metric_value
            elif startd:
                endd = datetime.datetime.now(date_format)
                duration = endd - startd
                metric_value = abs(int((duration.days * 86400) +
                                       duration.seconds))
                metrics[os.path.splitext(log)[0]] = metric_value
        for metric_name, metric_value in metrics.iteritems():
            self.publish(metric_name, metric_value)
