#!/usr/bin/env python2.7
"""A python project for monitoring network resources
"""
from datetime import datetime
import json
import sys
import os
import logging
import argparse
from time import sleep
import subprocess
import db_controller


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
                                    "--multi",
                                    help="Multi server watch mode",
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
    parser.add_argument('-b',
                        dest='base_directory',
                        default='/var/games/minecraft',
                        help='Change MineOS Server Base Location (ex. /var/games/minecraft)')
    parser.add_argument('-o',
                        dest='owner',
                        default='mc',
                        help='Sets the owner of the Minecraft servers (ex mc)')
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

    mode = modes(base_directory=args.base_directory, owner=args.owner, sleep_delay=args.delay)
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
    if args.multi:
        mode.multi_server()


class modes(object):  # Uses new style classes
    def __init__(self, base_directory, owner, sleep_delay):
        self.base_directory = base_directory
        self.sleep_delay = sleep_delay
        self.owner = owner  # We NEED to specify owner or we get a error in the webGUI during start/stop from there
        logging.debug("Modes obj created" + str(self.base_directory) + '  ' + str(self.owner))

    def sleep(self):
        try:
            sleep(self.sleep_delay)
        except KeyboardInterrupt:
            print("Bye Bye.")
            sys.exit(0)

    def list_servers(self):
        pass
        #TODO Return list of servers


    def multi_server(self):
        print("Multi Server mode")
        print("Press Ctrl-C to quit")

        while True:
            server_list = mc.list_servers(self.base_directory)
            logging.debug(server_list)

            for i in server_list:
                server_logger(server_name=i, owner=self.owner, base_directory=self.base_directory).check_server_status()
            self.sleep()


class server_logger(mc):
    def check_server_status(self):
        logging.info("Checking server {0}".format(self.server_name))
        if self.up and int(self.ping[3]) > 0:  # Server is up and has players
            self.log_active_players_to_db()

    def log_active_players_to_db(self):
        """ Takes active players and logs list to db with timestamp """
        logging.debug('# of players: ' + str(self.ping[3]))  # number of players
        logging.debug('PID: ' + str(self.screen_pid))

        players_list = json.dumps([])
        # players_list = json.dumps(self.get_player_list())

        conn, cur = db_controller.db_access().open_connection()
        cur.execute(
            'INSERT INTO player_activity ("Time_Stamp","Player_Count","Player_Names","Server_Name") VALUES (%s, %s, %s,%s)',
            (datetime.now(), self.ping[3], players_list, self.server_name))
        db_controller.db_access.close_connection(conn, cur)

    def get_player_list(self):
        players_list = []

        logging.debug(os.getcwd())
        # FIXME Command not working, but attaching to screen
        # See http://www.cyberciti.biz/faq/python-run-external-command-and-get-output/
        cmd = 'screen -d -m -r ' + str(self.screen_pid) + ' "/list"'  # Breaks screen on exit, stuck in loop
        # cmd = 'ls'
        logging.debug(subprocess.check_output(cmd))
        cmd_exit = 'screen detach'

        subprocess.check_output(cmd_exit)

        # os.system(cmd)
        # process = subprocess.Popen(cmd)
        # (output, err) = process.communicate()
        # logging.debug('Output: ' + str(output))
        # logging.debug('Err: ' + str(err))
        # status_code = process.wait()
        # logging.debug('Status Code: ' + str(status_code))
        # process.wait(5)

        return players_list


if __name__ == "__main__":
    main()

