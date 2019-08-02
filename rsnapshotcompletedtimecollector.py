#!/usr/bin/python

"""
rsnapshot_runtime_diamond.py
A script that parses rsnapshot logs to determine last completion date and
time of any runs.
"""

import os
import logging
from subprocess import Popen, PIPE
from datetime import datetime
import diamond.collector


class RsnapshotCompletedTimeCollector(diamond.collector.Collector):
    def get_default_config_help(self):
        """
        Seting up help values for custom entry
        """
        config_help = super(RsnapshotCompletedTimeCollector,
                            self).get_default_config_help()
        config_help.update({
            'rsnap_log_home':
            'Path to base directory of rsnap logs'
            ' name. Defaults to "%s"' % RSNAP_LOG_HOME,
        })
        return config_help

    def collect():
        """
        Looping over all rsnap logs and publishing deltas
        """
        date_format = "%Y-%m-%dT%H:%M:%S"
        root_dir = self.config['rsnap_log_home']
        metrics = {}
        for log in sorted(os.listdir(root_dir)):
            for line in reversed(open(os.path.join(root_dir, log))
                                 .readlines()):
                if '.pid' in line and 'rm' in line:
                    end_date = line.split()[0].strip("[").strip("]")
                    endd = datetime.strptime(end_date, date_format)
            if endd:
                metric_value = endd
                metrics[os.path.splitext(log)[0]] = metric_value
        for metric_name, metric_value in metrics.iteritems():
            self.publish(metric_name, metric_value)
