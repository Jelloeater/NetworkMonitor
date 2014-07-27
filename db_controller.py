import logging
import os
import sys
import json
import getpass

sys.path.append(os.getcwd() + '/keyring')  # Strange path issue, only appears when run from local console, not IDE
sys.path.append(os.getcwd() + '/pg8000-master')
import pg8000
from pg8000 import errors
import keyring
from keyring.errors import PasswordDeleteError

__author__ = 'Jesse'


class db_settings():
    """ Container class for load/save """
    USERNAME = 'postgres'
    # Password should be stored with keyring
    DB_HOST = '127.0.0.1'
    PORT = 5432
    DATABASE = 'player_stats'


class SettingsHelper(db_settings):
    SETTINGS_FILE_PATH = "database_settings.json"
    KEYRING_APP_ID = 'mineOSPlayerStats'

    @classmethod
    def loadSettings(cls):
        if os.path.isfile(cls.SETTINGS_FILE_PATH):
            try:
                with open(cls.SETTINGS_FILE_PATH) as fh:
                    db_settings.__dict__ = json.loads(fh.read())
            except ValueError:
                logging.error("Settings file has been corrupted, reverting to defaults")
                os.remove(cls.SETTINGS_FILE_PATH)
        logging.debug("Settings Loaded")

    @classmethod
    def saveSettings(cls):
        with open(cls.SETTINGS_FILE_PATH, "w") as fh:
            fh.write(json.dumps(db_settings.__dict__, sort_keys=True, indent=0))
        logging.debug("Settings Saved")


class db_access(SettingsHelper, object):
    def __init__(self):
        self.loadSettings()
        self.PASSWORD = keyring.get_password(self.KEYRING_APP_ID, self.USERNAME)  # Loads password from secure storage

    def open_connection(self):
        """ Returns connection & cursor"""
        connection = pg8000.DBAPI.connect(
            user=self.USERNAME,
            password=self.PASSWORD,
            host=self.DB_HOST,
            port=self.PORT,
            database=self.DATABASE)
        cursor = connection.cursor()
        logging.debug('Opened DB Connection')
        return connection, cursor

    @staticmethod
    def close_connection(connection, cursor):
        try:
            cursor.close()
        except pg8000.errors.ProgrammingError:
            connection.rollback()
            logging.warning('Rollback')
        else:
            connection.commit()
        logging.debug('Closed DB Connection')


class db_helper(db_access):
    """ Lets users send email messages """
    # db = postgresql.open(user = 'usename', database = 'datname', port = 5432)
    # http://python.projects.pgfoundry.org/docs/1.1/

    # TODO Maybe implement other mail providers
    def __init__(self):
        super(db_helper, self).__init__()

    def __create_database(self):
        """ Creates the database using template1 """
        try:
            try:
                logging.info("Check if Database Exists")
                connection = pg8000.DBAPI.connect(
                    user=self.USERNAME, password=self.PASSWORD, host=self.DB_HOST, database='template1')
                cursor = connection.cursor()
                connection.autocommit = True
                cursor.execute('''CREATE DATABASE player_stats''')
                connection.close()
                logging.info('Created Database')
            except errors.ProgrammingError:
                logging.warn('Database (Player_Stats) Already Exists')
        except pg8000.errors.InterfaceError:
            logging.error("DB Connection Interface Error")
            print('Please check the user settings')


    def __create_table(self):
        logging.warning('Creating player_activity table')
        DDL_Query = '''
        CREATE TABLE player_activity (
        "Index" SERIAL NOT NULL,
        "Time_Stamp" TIMESTAMP(0) NOT NULL,
        "Player_Count" INT4 NOT NULL,
        "Player_Names" TEXT NOT NULL,
        "Server_Name" TEXT NOT NULL,
        CONSTRAINT "player_activity_pkey"
        PRIMARY KEY ("Index"))'''
        conn, cur = self.open_connection()
        try:
            cur.execute(DDL_Query)
        except pg8000.errors.ProgrammingError:
            logging.warn('player_activity already exists')
        db_access.close_connection(conn, cur)

        # TODO Execute on first run

    def test_db_setup(self):
        """ Gets run on startup """
        logging.debug(db_settings.__dict__)
        logging.debug('DB Password= ' +
                      keyring.get_password(SettingsHelper.KEYRING_APP_ID, db_settings.USERNAME))
        try:
            logging.info('Testing Database Connection')
            conn, cur = self.open_connection()
            try:
                cur.execute('SELECT * FROM player_activity')
                db_access.close_connection(conn, cur)
                logging.info('Connection Successful')
            except pg8000.errors.ProgrammingError:
                logging.error('Cannot find player_activity table')
                self.__create_table()
        except pg8000.errors.ProgrammingError:
            logging.error('Cannot find player_stats database')
            self.__create_database()
            self.__create_table()
            try:
                self.test_db_setup()  # Retry test_db_setup
            except pg8000.errors.ProgrammingError:
                logging.critical('Cannot recover from missing table & database')
                logging.critical('Maybe try creating the database and table in Webmin, and running again?')
                logging.critical('Sorry :( "I wasnt even supposed to be here today" -Dante')
                sys.exit(1)


    def configure(self):
        print("Enter database username (postgres) or press enter to skip")
        username = raw_input('({0})>'.format(self.USERNAME))
        if username:
            db_settings.USERNAME = username

        print("Enter database password or press enter to skip")
        password = getpass.getpass(
            prompt='>')  # To stop shoulder surfing
        if password:
            keyring.set_password(self.KEYRING_APP_ID, self.USERNAME, password)

        print("Enter database server HOST Address to edit (127.0.0.1) or press enter to skip")
        DB_HOST = raw_input('({0})>'.format(self.DB_HOST))
        if DB_HOST:
            db_settings.DB_HOST = DB_HOST

        print("Enter database server port to edit (playerStats) or press enter to skip")
        port = raw_input('({0})>'.format(str(self.PORT)))
        if port:
            db_settings.PORT = int(port)
        self.saveSettings()

        print("Settings Updated")
        sys.exit(0)

    def clear_password_store(self):
        try:
            keyring.delete_password(self.KEYRING_APP_ID, self.USERNAME)
            print("Password removed from Keyring")
        except PasswordDeleteError:
            logging.error("Password cannot be deleted or already has been removed")

        sys.exit(0)



