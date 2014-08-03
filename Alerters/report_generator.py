#!/usr/bin/env python2.7
"""A python project for monitoring network resources
"""
from datetime import datetime
import logging

from Alerters.email import gmail
from Database import db_controller


__author__ = "Jesse S"
__license__ = "GNU GPL v2.0"
__version__ = "1.2"
__email__ = "jelloeater@gmail.com"


class action():
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

    @staticmethod
    def last_report_generated_minute_count():
        pass

    @staticmethod
    def report_generation_check():
        pass

