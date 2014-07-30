#!/usr/bin/env python2.7
"""A python project for monitoring network resources
"""
from datetime import datetime
import sys
import logging
import argparse

from Alerters.email import gmail
from Database import db_controller


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
    report_group = parser.add_argument_group('Actions')
    report_group.add_argument("-g",
                              "--generate_report",
                              help="Generate Weekly Report",
                              action="store_true")

    email_group = parser.add_argument_group('E-mail Config')
    email_group.add_argument("-e",
                             "--configure_email_settings",
                             help="Configure email alerts",
                             action="store_true")
    email_group.add_argument("-r",
                             "--remove_email_password_store",
                             help="Removes password stored in system keyring",
                             action="store_true")

    db_group = parser.add_argument_group('Database Config')
    db_group.add_argument("-b",
                          "--configure_db_settings",
                          help="Configure database settings",
                          action="store_true")
    db_group.add_argument("-p",
                          "--remove_db_password_store",
                          help="Removes password stored in system keyring",
                          action="store_true")

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
    # Create new mode object for flow, I'll buy that :)

    if len(sys.argv) == 1:  # Displays help and lists servers (to help first time users)
        parser.print_help()
        sys.exit(1)

    if args.remove_db_password_store:
        db_controller.db_helper().clear_password_store()

    if args.configure_db_settings:
        db_controller.db_helper().configure()

    if args.remove_email_password_store:
        gmail().clear_password_store()

    if args.configure_email_settings:
        gmail().configure()

    # Magic starts here
    if args.generate_report:
        db_controller.db_helper().test_db_setup()
        gmail().test_login()
        action.generate_report()


class action:
    @staticmethod
    def generate_report(number_of_days=7):
        conn, cur = db_controller.db_access().open_connection()
        # TODO Rewrite table query
        # query = '''SELECT * FROM player_activity WHERE "Time_Stamp" >= (now() - '{0} day'::INTERVAL);'''
        # cur.execute(query.format(number_of_days))
        data = cur.fetchall()
        db_controller.db_access.close_connection(conn, cur)
        logging.debug('DB dump')
        logging.debug(data)


        # noinspection PyListCreation
        msg = ['The First Line: \n\n']  # Email Message Body

        msg.append('\nA message')

        msg.append('\n\nReport Generated @ ' + str(datetime.now()))
        subj = "Server Status Report"
        gmail().send(subject=subj, text=''.join(msg))
        # Create gmail obj


if __name__ == "__main__":
    main()
