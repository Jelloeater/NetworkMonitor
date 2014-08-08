from datetime import datetime
import logging

from Database import db_helpers
from Alerters import email_controller


__author__ = 'Jesse Laptop'


class email_actions():
    @staticmethod
    def send_alert(server_info_object):

        logging.debug(server_info_object)

        subj = server_info_object.sl_service_type + " @ " + server_info_object.sl_host + ' is DOWN'
        # noinspection PyListCreation
        msg = []  # Email Message Body
        msg.append('Report: ')

        msg.append('\nHost: ' + server_info_object.sl_host)
        msg.append('\nPort: ' + str(server_info_object.sl_port))
        msg.append('\nService: ' + server_info_object.sl_service_type)
        msg.append('\nNote: ' + str(server_info_object.sl_note))

        msg.append('\n\nReport Generated @ ' + str(datetime.now()))

        logging.debug('Subject:' + subj)
        logging.debug(''.join(msg))
        email_controller.send_gmail().send(subject=subj, text=''.join(msg))
        db_helpers.email_log.log_email_sent(''.join(msg))


    @staticmethod
    def generate_report(number_of_days=7):
        conn, cur = db_controller.db_access().open_connection()
        # FIXME Rewrite table query
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

        email_controller.send_gmail().send(subject=subj, text=''.join(msg))
        db_helpers.email_log.log_email_sent(''.join(msg))