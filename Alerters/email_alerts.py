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
    def generate_report():
        """ Created report of all fails since last email was sent """
        fail_list = db_helpers.server_stats.failures_in_x_minutes_ago(db_helpers.email_log.email_sent_x_minutes_ago())
        server_list = db_helpers.monitor_list.get_server_list()

        fail_list_txt = []

        for i in fail_list:
            host_name = None
            try:
                host_name = str(i[2]).split(':')[0]
                port = str(i[2]).split(':')[1]
                fail_list_txt.append('\nHost: ' + host_name)
                fail_list_txt.append('\nPort: ' + port)
            except IndexError:
                # For Hosts with no port
                host_name = str(i[2])
                fail_list_txt.append('\nHost: ' + host_name)

            fail_list_txt.append('\nService: ' + i[3])
            fail_list_txt.append('\nTime: ' + str(i[1]))

            # Look up note if present
            try:
                note_txt = str([x[4] for x in server_list if x[1] == host_name][0])
            except IndexError:
                note_txt = ''

            fail_list_txt.append('\nNote: ' + note_txt)
            fail_list_txt.append('\n')

        logging.debug('BREAKPOINT')

        # noinspection PyListCreation
        msg = ['The First Line: \n\n']  # Email Message Body

        msg.append('\nA message')

        msg.append('\n\nReport Generated @ ' + str(datetime.now()))
        subj = "Server Status Report"

        email_controller.send_gmail().send(subject=subj, text=''.join(msg))
        db_helpers.email_log.log_email_sent(''.join(msg))