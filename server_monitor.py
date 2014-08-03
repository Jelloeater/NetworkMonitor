#!/usr/bin/env python2.7
"""A python project for monitoring network resources
"""
import sys
import logging
import argparse
from time import sleep

# from Alerters import email

from Alerters import report_generator
from Database import db_controller
from Database import db_helpers
from Monitors import network


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
    server_group = parser.add_argument_group('Single Server Mode')
    server_group.add_argument("-s",
                              "--single",
                              action="store",
                              help="Single server watch mode")
    interactive_group = parser.add_argument_group('Interactive Mode')
    interactive_group.add_argument("-i",
                                   "--interactive",
                                   help="Interactive menu mode",
                                   action="store_true")
    multi_server_group = parser.add_argument_group('Multi Server Mode')
    multi_server_group.add_argument("-m",
                                    "--monitor",
                                    help="Multi server watch mode",
                                    action="store_true")
    multi_server_group.add_argument("-e",
                                    "--editServerList",
                                    help="Edit the server watch list",
                                    action="store_true")

    db_group = parser.add_argument_group('Database Settings')
    db_group.add_argument("-c",
                          "--configure_db_settings",
                          help="Configure database settings",
                          action="store_true")
    db_group.add_argument("-r",
                          "--remove_password_store",
                          help="Removes password stored in system keyring",
                          action="store_true")

    report_group = parser.add_argument_group('Actions')
    report_group.add_argument("-g",
                              "--generate_report",
                              help="Generate Weekly Report",
                              action="store_true")

    email_group = parser.add_argument_group('E-mail Config')
    email_group.add_argument("--configure_email_settings",
                             help="Configure email alerts",
                             action="store_true")

    email_group.add_argument("--remove_email_password_store",
                             help="Removes password stored in system keyring",
                             action="store_true")

    parser.add_argument("-d",
                        "--delay",
                        action="store",
                        type=int,
                        default=60,
                        help="Wait x second between checks (ex. 60)")
    parser.add_argument("-l",
                        "--list",
                        action="store_true",
                        help="List MineOS Servers")
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

    if args.list:
        mode.list_servers()

    # if args.remove_email_password_store:
    # email.gmail().clear_password_store()
    #
    # if args.configure_email_settings:
    #     email.gmail().configure()
    #
    # # Magic starts here
    # if args.generate_report:
    #     db_controller.db_helper().test_db_setup()
    #     email.gmail().test_login()
    #     report_generator.action.generate_report()

    if args.remove_password_store:
        db_controller.db_helper().clear_password_store()

    if args.configure_db_settings:
        db_controller.db_helper().configure()

    db_controller.db_helper().test_db_setup()

    # Magic starts here
    if args.monitor:
        mode.multi_server()


class modes(object, report_generator):  # Uses new style classes
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

    def list_servers(self):
        print("Servers:")
        self.server_list = db_helpers.monitor_list.get_server_list()
        for i in self.server_list:
            print(i)

    def multi_server(self):
        print("Multi Server mode")
        print("Press Ctrl-C to quit")

        while True:
            self.server_list = db_helpers.monitor_list.get_server_list()  # Gets server list on each refresh, in-case of updates
            logging.debug(self.server_list)
            for i in self.server_list:
                server_logger(i).check_server_status()  # Send each row of monitor_list to logic gate

            report_generator.action.report_generation_check()
            self.sleep()


class server_logger(db_helpers, modes):
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
            up_down_flag = network.MonitorTCP(host=self.sl_host, port=str(self.sl_port) + ',').run_test()

        if up_down_flag is False:
            db_helpers.monitor_list.log_service_down(self)
        else:
            logging.debug(self.sl_host + ' is UP')


if __name__ == "__main__":
    main()

