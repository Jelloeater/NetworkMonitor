import getpass
import json
import logging
import os
import smtplib  # For Authentication Error
import sys
import urllib2

from Database import db_helpers
import gmail
import keyring
from keyring.errors import PasswordDeleteError


__author__ = 'Jesse'


class gmailSettings():
    """ Container class for load/save """
    USERNAME = ""
    # Password should be stored with keyring
    SEND_ALERT_TO = []  # Must be a list


class SettingsHelper(gmailSettings):
    SETTINGS_FILE_PATH = "email_settings.json"
    KEYRING_APP_ID = 'NetworkMonitor_email'

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


class send_gmail(object, SettingsHelper):
    """ Lets users send email messages """
    # TODO Maybe implement other mail providers
    def __init__(self):
        self.loadSettings()
        self.PASSWORD = keyring.get_password(self.KEYRING_APP_ID, self.USERNAME)  # Loads password from secure storage

    def test_login(self):
        """ Tests both if gmail is reachable, and if the login info is correct """
        # FIXME Come up with better way to check for gmail being up
        logging.debug('Testing login')
        http_response_code = 404
        try:
            http_response_code = urllib2.urlopen('http://www.google.com', timeout=3).code
        except urllib2.URLError:
            logging.critical('Cannot reach Gmail')

        if http_response_code == 200:
            response_flag = True
        else:
            response_flag = False

        try:
            logging.debug(str(self.USERNAME) + str(self.PASSWORD))
            gmail.GMail(username=self.USERNAME, password=self.PASSWORD)
            login_flag = True
        except smtplib.SMTPAuthenticationError:
            logging.critical('Bad gmail login info, cannot send messages, exiting')
            sys.exit(1)

        if login_flag and response_flag:
            return True
        else:
            return False

    def send(self, subject, text):
        logging.info("Sending email")
        gmail.GMail(username=self.USERNAME, password=self.PASSWORD).send(
            gmail.Message(subject=subject, to=self.convert_to_list_to_csv(), text=text))
        db_helpers.email_log.log_email_sent(self.SEND_ALERT_TO)
        logging.info("Message Sent")

    def convert_to_list_to_csv(self):
        return ",".join([str(x) for x in self.SEND_ALERT_TO])

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
    send_gmail().test_login()