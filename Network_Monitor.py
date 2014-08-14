#!/usr/bin/env python2.7
"""A python project for monitoring network resources
"""
import sys
import os

sys.path.append(os.getcwd() + '/keyring')  # Strange path issue, only appears when run from local console, not IDE
sys.path.append(os.getcwd() + '/pg8000-master')
sys.path.append(os.getcwd() + '/python-nmap-0.1.4')
sys.path.append(os.getcwd() + '/gmail-0.5')

import logging
import argparse
from time import sleep
from Database import db_controller
from Database import db_helpers
from Monitors import network
from Database import db_monitor_list

from Alerters import email_controller
from Alerters import email_alerts


__author__ = "Jesse S"
__license__ = "GNU GPL v2.0"
__version__ = "1.5"
__email__ = "jelloeater@gmail.com"

LOG_FILENAME = "NetworkMonitor.log"


def main():
    """ Take arguments and direct program """
    parser = argparse.ArgumentParser(description="A Network Stats Database Report Generator"
                                                 " (http://github.com/Jelloeater/NetworkMonitor)",
                                     version=__version__,
                                     epilog="Please specify action")

    multi_server_group = parser.add_argument_group('Multi Server Mode')
    multi_server_group.add_argument("-m",
                                    "--monitor",
                                    help="Multi server watch mode",
                                    action="store_true")

    report_group = parser.add_argument_group('Actions')
    report_group.add_argument("-g",
                              "--generate_report_flag",
                              help="Generate Weekly Report",
                              action="store_true")

    email_group = parser.add_argument_group('E-mail Config')
    email_group.add_argument("-config_email",
                             help="Configure email alerts",
                             action="store_true")
    email_group.add_argument("-rm_email_pass_store",
                             help="Removes password stored in system keyring",
                             action="store_true")

    db_group = parser.add_argument_group('Database Settings')
    db_group.add_argument("-config_db",
                          help="Configure database settings",
                          action="store_true")
    db_group.add_argument("-rm_db_pass_store",
                          help="Removes password stored in system keyring",
                          action="store_true")

    monitor_list_group = parser.add_argument_group('Monitor List')
    monitor_list_group.add_argument("-config_monitors",
                                    help="Configure servers to monitor",
                                    action="store_true")
    monitor_list_group.add_argument("-list",
                                    help="List servers to monitor",
                                    action="store_true")

    parser.add_argument("-d",
                        "--delay",
                        action="store",
                        type=int,
                        default=60,
                        help="Wait x second between checks (60)")

    parser.add_argument("-a",
                        "--alert_timeout",
                        action="store",
                        type=int,
                        default=15,
                        help="Wait x minutes between alerts (15)")

    parser.add_argument("-t",
                        "--host_timeout",
                        action="store",
                        type=int,
                        default=10,
                        help="Wait x seconds for failure (10)")

    parser.add_argument("--debug",
                        action="store_true",
                        help="Debug Mode Logging")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                            level=logging.DEBUG)
        logging.debug(sys.path)
        logging.debug(args)
        logging.debug('Debug Mode Enabled')
    else:
        logging.basicConfig(filename=LOG_FILENAME,
                            format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                            level=logging.WARNING)

    mode = modes(sleep_delay=args.delay, alert_timeout=args.alert_timeout, host_timeout=args.host_timeout)
    # Create new mode object for flow, I'll buy that :)

    if len(sys.argv) == 1:  # Displays help and lists servers (to help first time users)
        parser.print_help()
        sys.exit(1)

    # Arg Logic here
    if args.list:
        db_monitor_list.get_print_server_list()

    if args.config_monitors:
        db_monitor_list.config_monitor_list()

    if args.config_db:
        db_controller.db_helper().configure()

    if args.rm_db_pass_store:
        db_controller.db_helper().clear_password_store()

    if args.config_email:
        email_controller.send_gmail().configure()

    if args.rm_email_pass_store:
        email_controller.send_gmail().clear_password_store()

    # Magic starts here
    if args.generate_report_flag:
        db_controller.db_helper().test_db_setup()
        email_controller.send_gmail().test_login()
        email_alerts.email_actions.generate_report()
        print('*NOTE: If report is empty, that just means nothing has failed since we sent an email, '
              'run -m to "fix" it*')

    if args.monitor:
        db_controller.db_helper().test_db_setup()
        email_controller.send_gmail().test_login()
        mode.multi_server()


class modes(object):  # Uses new style classes
    def __init__(self, sleep_delay, alert_timeout, host_timeout):
        self.sleep_delay = sleep_delay
        self.alert_timeout = alert_timeout
        self.host_timeout = host_timeout
        self.server_list = []


    def sleep(self):
        try:
            sleep(self.sleep_delay)
        except KeyboardInterrupt:
            print("Bye Bye.")
            sys.exit(0)

    def multi_server(self):
        print("Multi Server mode")
        print("Press Ctrl-C to quit")

        while True:
            self.server_list = db_helpers.monitor_list.get_server_list()
            # Gets server list on each refresh, in-case of updates
            logging.debug(self.server_list)
            # Send each row of monitor_list to logic gate
            for i in self.server_list:
                server_logger(i, sleep_delay=self.sleep_delay, alert_timeout=self.alert_timeout,
                              host_timeout=self.host_timeout).check_server_status()

            last_email = db_helpers.email_log.email_sent_x_minutes_ago()
            last_fail = db_helpers.monitor_list.get_time_from_last_failure()
            logging.debug(
                'Last e-mail sent: ' + str(last_email) + 'Timeout: ' + str(self.alert_timeout) +
                'Last Failure: ' + str(last_fail))

            if db_helpers.email_log.email_sent_x_minutes_ago() > self.alert_timeout \
                    > db_helpers.monitor_list.get_time_from_last_failure():
                # Are we spamming alerts?
                # Check if any servers have gone down in the the last X minutes
                # If any have gone down, send report
                if email_controller.send_gmail().test_login():
                    logging.info('SENDING REPORT')
                    email_alerts.email_actions.generate_report()
            else:
                logging.info('E-mail timeout still cooling off')

            self.sleep()


class server_logger(modes):
    """ self.variable same as monitor_list columns"""

    def __init__(self, monitor_row, sleep_delay, alert_timeout, host_timeout):
        super(server_logger, self).__init__(sleep_delay, alert_timeout, host_timeout)
        self.sl_host = monitor_row[1]
        self.sl_port = monitor_row[2]
        self.sl_service_type = monitor_row[3]
        self.sl_note = monitor_row[4]

    def check_server_status(self):
        """ Picks either TCP, Ping host, or check web, depending on args """

        up_down_flag = False

        if self.sl_service_type == 'url':
            logging.debug("Checking URL: " + str(self.sl_host))
            up_down_flag = network.MonitorHTTP(url=self.sl_host, timeout=self.host_timeout).run_test()

        if self.sl_service_type == 'host':
            logging.debug("Checking host: " + str(self.sl_host))
            up_down_flag = network.MonitorHost(host=self.sl_host, timeout=self.host_timeout).run_test()

        if self.sl_service_type == 'tcp':
            logging.debug("Checking TCP Service: " + str(self.sl_host) + ' port: ' + str(self.sl_port))
            up_down_flag = network.MonitorTCP(host=self.sl_host, port=str(self.sl_port),
                                              timeout=self.host_timeout).run_test()

        if up_down_flag is False:
            self.server_down_actions()
        else:
            logging.info(self.sl_host + ' -  ' + str(self.sl_port) + ' is UP')

    def server_down_actions(self):
        """ Core logic for driving program """
        db_helpers.monitor_list.log_service_down(self)
        # TODO FEATURE: Add special alert for critical systems (need to add column to monitor_list)


if __name__ == "__main__":
    main()

