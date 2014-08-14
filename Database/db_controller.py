import logging
import os
import sys
import json
import getpass

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
    DATABASE = 'network_monitor'


class SettingsHelper(db_settings):
    SETTINGS_FILE_PATH = "database_settings.json"
    KEYRING_APP_ID = 'NetworkMonitor_db'

    @classmethod
    def loadSettings(cls):
        if os.path.isfile(cls.SETTINGS_FILE_PATH):
            try:
                with open(cls.SETTINGS_FILE_PATH) as fh:
                    db_settings.__dict__ = json.loads(fh.read())
            except ValueError:
                logging.error("Settings file has been corrupted, reverting to defaults")
                os.remove(cls.SETTINGS_FILE_PATH)
                # logging.debug("Settings Loaded")

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
        """ Returns connection, cursor"""
        connection = pg8000.DBAPI.connect(
            user=self.USERNAME,
            password=self.PASSWORD,
            host=self.DB_HOST,
            port=self.PORT,
            database=self.DATABASE)
        cursor = connection.cursor()
        # logging.debug('Opened DB Connection')
        return connection, cursor

    @staticmethod
    def close_connection(connection, cursor):
        """ Takes connection, cursor """
        try:
            cursor.close()
        except pg8000.errors.ProgrammingError:
            connection.rollback()
            logging.warning('Rollback')
        else:
            connection.commit()
            # logging.debug('Closed DB Connection')


class db_helper(db_access):
    """ Lets users send email messages """
    # db = postgresql.open(user = 'usename', database = 'datname', port = 5432)
    # http://python.projects.pgfoundry.org/docs/1.1/

    def __init__(self):
        super(db_helper, self).__init__()

    def __create_database(self):
        """ Creates the database using template1 """
        try:
            try:
                logging.info("Check if Database Exists")
                connection = pg8000.DBAPI.connect(
                    user=self.USERNAME, password=self.PASSWORD, host=self.DB_HOST, database='template1')  # Default DB
                cursor = connection.cursor()
                connection.autocommit = True
                cursor.execute('''CREATE DATABASE network_monitor''')
                connection.close()
                logging.info('Created Database: ' + self.DATABASE)
            except errors.ProgrammingError:
                logging.warn('Database (' + self.DATABASE + ') Already Exists')
        except pg8000.errors.InterfaceError:
            logging.error("DB Connection Interface Error")
            print('Please check the user settings')

    def __create_tables(self):
        """ Creates all the necessary tables for the program to function """

        # Generates server_stats table
        logging.warning('Creating (' + 'server_stats' + ') table')
        DDL_Query = '''
        CREATE TABLE server_stats (
        "index" SERIAL NOT NULL,
        "time_stamp" TIMESTAMP(0) NOT NULL,
        "ip_hostname" TEXT NOT NULL,
        "service_type" TEXT NOT NULL,
        CONSTRAINT "server_stats_pkey"
        PRIMARY KEY ("index"))'''
        conn, cur = self.open_connection()
        try:
            cur.execute(DDL_Query)
        except pg8000.errors.ProgrammingError:
            logging.warn('server_stats already exists')
        db_access.close_connection(conn, cur)

        # Generates email_log table
        logging.warning('Creating (' + 'email_log' + ') table')
        DDL_Query = '''
        CREATE TABLE email_log (
        "index" SERIAL NOT NULL,
        "time_stamp" TIMESTAMP(0) NOT NULL,
        "to_address" TEXT NOT NULL,
        CONSTRAINT "email_log_pkey"
        PRIMARY KEY ("index"))'''
        conn, cur = self.open_connection()
        try:
            cur.execute(DDL_Query)
        except pg8000.errors.ProgrammingError:
            logging.warn('email_log already exists')
        db_access.close_connection(conn, cur)

        # Generates valid_types table for foreign key constraints
        logging.warning('Creating (' + 'valid_types' + ') table')
        DDL_Query = '''
        CREATE TABLE valid_types (
        "type" TEXT,
        CONSTRAINT "valid_types_pkey"
        PRIMARY KEY ("type"))'''
        # Checks to make sure the type in valid on INSERT

        conn, cur = self.open_connection()
        try:
            cur.execute(DDL_Query)
        except pg8000.errors.ProgrammingError:
            logging.warn('monitor_list already exists')
        db_access.close_connection(conn, cur)

        # Adds valid types for foreign key validity checking in monitor_list
        logging.warning('Adding ' + 'valid_types' + ' to table')
        DDL_Query = '''INSERT INTO "valid_types" VALUES ('host'),('tcp'),('url');'''
        conn, cur = self.open_connection()
        try:
            cur.execute(DDL_Query)
        except pg8000.errors.ProgrammingError:
            logging.warn('types already inserted')
        db_access.close_connection(conn, cur)

        # Generates monitor_list table
        logging.warning('Creating (' + 'monitor_list' + ') table')
        DDL_Query = '''
        CREATE TABLE monitor_list (
        "index" SERIAL NOT NULL,
        "hostname" TEXT,
        "port" INTEGER ,
        "service_type" TEXT NOT NULL,
        "note" TEXT,
        CONSTRAINT "monitor_list_pkey"
        PRIMARY KEY ("index"))'''
        # Checks to make sure the type in valid on INSERT
        conn, cur = self.open_connection()
        try:
            cur.execute(DDL_Query)
        except pg8000.errors.ProgrammingError:
            logging.warn('monitor_list already exists')
        db_access.close_connection(conn, cur)

        # Alters server_stats by adding foreign key constraint from valid_types table
        logging.warning('Enforcing foreign key on (' + 'server_stats' + ') table')
        DDL_Query = '''ALTER TABLE "server_stats" ADD FOREIGN KEY ("service_type")
                       REFERENCES "valid_types" ("type") ON DELETE NO ACTION ON UPDATE NO ACTION;'''
        conn, cur = self.open_connection()
        try:
            cur.execute(DDL_Query)
        except pg8000.errors.ProgrammingError:
            logging.warn('server_stats already has foreign key')
        db_access.close_connection(conn, cur)

        # Alters monitor_list by adding foreign key constraint from valid_types table
        logging.warning('Enforcing foreign key on (' + 'monitor_list' + ') table')
        DDL_Query = '''ALTER TABLE "monitor_list" ADD FOREIGN KEY ("service_type")
        REFERENCES "valid_types" ("type") ON DELETE NO ACTION ON UPDATE NO ACTION;'''
        conn, cur = self.open_connection()
        try:
            cur.execute(DDL_Query)
        except pg8000.errors.ProgrammingError:
            logging.warn('monitor_list already has foreign key')
        db_access.close_connection(conn, cur)

        # TODO Execute on first run

    def test_db_setup(self):
        """ Gets run on startup """
        logging.debug('Testing DB Setup')
        logging.debug(db_settings.__dict__)
        logging.debug('DB Password= ' +
                      keyring.get_password(SettingsHelper.KEYRING_APP_ID, db_settings.USERNAME))
        try:
            logging.info('Testing Database Connection')
            conn, cur = self.open_connection()
            try:
                cur.execute('SELECT * FROM server_stats')
                db_access.close_connection(conn, cur)
                logging.info('Connection Successful')
            except pg8000.errors.ProgrammingError:
                logging.error('Cannot find player_activity table')
                self.__create_tables()
        except pg8000.errors.ProgrammingError:
            logging.error('Cannot find '+self.DATABASE+' database')
            self.__create_database()
            self.__create_tables()
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



