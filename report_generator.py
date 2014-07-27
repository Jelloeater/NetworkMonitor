#!/usr/bin/env python2.7
"""A python project for monitoring network resources
"""
from datetime import datetime
import getpass
import json
import smtplib
import sys
import os
import logging
import argparse
import db_controller
import keyring
from keyring.errors import PasswordDeleteError

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


class gmailSettings():
    """ Container class for load/save """
    USERNAME = ""
    # Password should be stored with keyring
    SEND_ALERT_TO = []  # Must be a list


class SettingsHelper(gmailSettings):
    SETTINGS_FILE_PATH = "email_settings.json"
    KEYRING_APP_ID = 'mineOSPlayerStats_gmail'

    @classmethod
    def loadSettings(cls):
        if os.path.isfile(cls.SETTINGS_FILE_PATH):
            try:
                with open(cls.SETTINGS_FILE_PATH) as fh:
                    gmailSettings.__dict__ = json.loads(fh.read())
            except ValueError:
                logging.error("Settings file has been corrupted, reverting to defaults")
                os.remove(cls.SETTINGS_FILE_PATH)
        logging.debug("Settings Loaded")

    @classmethod
    def saveSettings(cls):
        with open(cls.SETTINGS_FILE_PATH, "w") as fh:
            fh.write(json.dumps(gmailSettings.__dict__, sort_keys=True, indent=0))
        logging.debug("Settings Saved")


class gmail(object, SettingsHelper):
    """ Lets users send email messages """
    # TODO Maybe implement other mail providers
    def __init__(self):
        self.loadSettings()
        self.PASSWORD = keyring.get_password(self.KEYRING_APP_ID, self.USERNAME)  # Loads password from secure storage

    def test_login(self):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)  # or port 465 doesn't seem to work!
            server.ehlo()
            server.starttls()
            server.login(self.USERNAME, self.PASSWORD)
            server.close()
        except smtplib.SMTPAuthenticationError:
            print("Username password mismatch")
            sys.exit(1)

    def send(self, subject, text):
        message = "\From: {0}\nTo: {1}\nSubject: {2}\n\n{3}".format(self.USERNAME,
                                                                    ", ".join(self.SEND_ALERT_TO),
                                                                    subject,
                                                                    text)

        logging.info("Sending email")
        server = smtplib.SMTP("smtp.gmail.com", 587)  # or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(self.USERNAME, self.PASSWORD)
        server.sendmail(self.USERNAME, self.SEND_ALERT_TO, message)
        server.close()
        logging.info("Message Sent")

    def configure(self):
        print("Enter user email (user@domain.com) or press enter to skip")

        username = raw_input('({0})>'.format(self.USERNAME))

        print("Enter email password or press enter to skip")
        password = getpass.getpass(
            prompt='>')  # To stop shoulder surfing
        if username:
            gmailSettings.USERNAME = username
        if password:
            keyring.set_password(self.KEYRING_APP_ID, self.USERNAME, password)

        print("Clear alerts list? (yes/no)?")
        import distutils.util

        try:
            if distutils.util.strtobool(raw_input(">")):
                gmailSettings.SEND_ALERT_TO = []  # Clear the list
                print("Alerts list cleared")
        except ValueError:
            pass

        print("Send alerts to (press enter when done):")
        while True:
            user_input = raw_input('({0})>'.format(','.join(self.SEND_ALERT_TO)))
            if not user_input:
                break
            else:
                gmailSettings.SEND_ALERT_TO.append(user_input)
        self.saveSettings()

    def clear_password_store(self):
        try:
            keyring.delete_password(self.KEYRING_APP_ID, self.USERNAME)
            print("Password removed from Keyring")
        except PasswordDeleteError:
            logging.error("Password cannot be deleted or already has been removed")


if __name__ == "__main__":
    main()
