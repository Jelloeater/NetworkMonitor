#!/usr/bin/env python2.7
"""A python project for monitoring network resources
"""
import sys
import os

sys.path.append(os.getcwd() + '/keyring')  # Strange path issue, only appears when run from local console, not IDE
sys.path.append(os.getcwd() + '/pg8000-master')
sys.path.append(os.getcwd() + '/python-nmap-0.1.4')
sys.path.append(os.getcwd() + '/gmail-0.5')

import json
import logging
import argparse
from time import sleep
from Database import db_controller
from Database import db_helpers
from Monitors import network
from Database import monitor_list_config

# from Alerters import report_generator
from Alerters import email


__author__ = "Jesse S"
__license__ = "GNU GPL v2.0"
__version__ = "1.2"
__email__ = "jelloeater@gmail.com"

LOG_FILENAME = "serverMonitor.log"


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
    multi_server_group.add_argument("-e",
                                    "--editServerList",
                                    help="Edit the server watch list",
                                    action="store_true")

    report_group = parser.add_argument_group('Actions')
    report_group.add_argument("-g",
                              "--generate_report",
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
                        help="Wait x second between checks (ex. 60)")
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

    mode = modes(sleep_delay=args.delay)
    # Create new mode object for flow, I'll buy that :)

    if len(sys.argv) == 1:  # Displays help and lists servers (to help first time users)
        parser.print_help()
        sys.exit(1)

    # Arg Logic here
    if args.list:
        monitor_list_config.list_servers()

    if args.config_monitors:
        monitor_list_config.main()

    if args.config_db:
        db_controller.db_helper().configure()

    if args.rm_db_pass_store:
        db_controller.db_helper().clear_password_store()

    if args.config_email:
        email.send_gmail().configure()

    if args.rm_email_pass_store:
        email.send_gmail().clear_password_store()

    # Magic starts here
    if args.generate_report:
        db_controller.db_helper().test_db_setup()
        logging.debug('Testing login')
        email.send_gmail().test_login()
        # report_generator.reports.generate_report()  #TODO Re-add report generator

    if args.monitor:
        mode.multi_server()


class modes(object):  # Uses new style classes
    def __init__(self, sleep_delay):
        self.sleep_delay = sleep_delay
        self.server_list = []

        # TODO Load server List from JSON

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
            self.server_list = db_helpers.monitor_list.get_server_list()  # Gets server list on each refresh, in-case of updates
            logging.debug(self.server_list)
            for i in self.server_list:
                server_logger(i).check_server_status()  # Send each row of monitor_list to logic gate
            self.sleep()


class server_logger():
    """ self.variable same as monitor_list columns"""

    def __init__(self, monitor_row):
        self.sl_host = monitor_row[1]
        self.sl_port = monitor_row[2]
        self.sl_service_type = monitor_row[3]

    def check_server_status(self):
        """ Picks either TCP, Ping host, or check web, depending on args """

        up_down_flag = False

        if self.sl_service_type == 'url':
            logging.debug("Checking URL: " + str(self.sl_host))
            up_down_flag = network.MonitorHTTP(self.sl_host).run_test()

        if self.sl_service_type == 'host':
            logging.debug("Checking host: " + str(self.sl_host))
            up_down_flag = network.MonitorHost(self.sl_host).run_test()

        if self.sl_service_type == 'tcp':
            logging.debug("Checking TCP Service: " + str(self.sl_host) + ' port: ' + str(self.sl_port))
            up_down_flag = network.MonitorTCP(host=self.sl_host, port=str(self.sl_port)).run_test()

        if up_down_flag is False:
            db_helpers.monitor_list.log_service_down(self)
        else:
            logging.info(self.sl_host + ' is UP')


    def log_errors_to_db(self):
        """ Takes error and logs list to db with timestamp """

        players_list = json.dumps([])
        # players_list = json.dumps(self.get_player_list())

        # conn, cur = database.db_access().open_connection()
        # cur.execute(
        # 'INSERT INTO player_activity ("Time_Stamp","Player_Count","Player_Names","Server_Name") VALUES (%s, %s, %s,%s)',
        # (datetime.now(), self.ping[3], players_list, self.server_name))
        # database.db_access.close_connection(conn, cur)


if __name__ == "__main__":
    main()

