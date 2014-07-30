#!/usr/bin/env python2.7
"""A python project for monitoring network resources
"""
import json
import sys
import logging
import argparse
from time import sleep

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

    if args.remove_password_store:
        db_controller.db_helper().clear_password_store()

    if args.configure_db_settings:
        db_controller.db_helper().configure()

    db_controller.db_helper().test_db_setup()

    # Magic starts here
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
            self.sleep()


class server_logger():
    """ self.variable same as monitor_list columns"""
    def __init__(self, monitor_row):
        self.host = monitor_row[1]
        self.port = monitor_row[2]
        self.url = monitor_row[3]
        self.service_type = monitor_row[4]

    def check_server_status(self):
        # TODO Pick either TCP, Ping host, or check web, depending on args
        if self.service_type == 'url':
            logging.debug("Checking URL: " + str(self.url))
            # TODO HTTP URL Check

        if self.service_type == 'host':
            logging.debug("Checking host: " + str(self.host))
            print(network.MonitorHost(self.host).run_test())
            # TODO Host Check

        if self.service_type == 'tcp':
            logging.debug("Checking TCP Service: " + str(self.host) + ' port: ' + str(self.port))
            # TODO TCP Check

    def log_errors_to_db(self):
        """ Takes error and logs list to db with timestamp """

        players_list = json.dumps([])
        # players_list = json.dumps(self.get_player_list())

        # conn, cur = database.db_access().open_connection()
        # cur.execute(
        #     'INSERT INTO player_activity ("Time_Stamp","Player_Count","Player_Names","Server_Name") VALUES (%s, %s, %s,%s)',
        #     (datetime.now(), self.ping[3], players_list, self.server_name))
        # database.db_access.close_connection(conn, cur)

if __name__ == "__main__":
    main()

