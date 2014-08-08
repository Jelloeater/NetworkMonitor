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

        def generate_fail_list(fail_list_in, monitor_list_in):

            fail_list_txt = []
            for i in fail_list_in:
                try:
                    # Try to parse port from hostname address
                    # (should still work even if host is removed from monitor_list)
                    host_name = str(i[2]).split(':')[0]
                    port = str(i[2]).split(':')[1]
                    fail_list_txt.append('\nHost: ' + host_name)
                    fail_list_txt.append('\nPort: ' + port)
                except IndexError:
                    host_name = str(i[2])
                    fail_list_txt.append('\nHost: ' + host_name)

                fail_list_txt.append('\nService: ' + i[3])
                fail_list_txt.append('\nTime: ' + str(i[1]))

                try:
                    # Try to find note in monitor_list
                    note_txt = str([x[4] for x in monitor_list_in if x[1] == host_name][0])
                except IndexError:
                    note_txt = ''
                fail_list_txt.append('\nNote: ' + note_txt)

                fail_list_txt.append('\n')
            return ''.join(fail_list_txt)

        # Start message creation here
        fail_list = db_helpers.server_stats.failures_in_x_minutes_ago(
            db_helpers.email_log.email_sent_x_minutes_ago())

        monitor_list = db_helpers.monitor_list.get_server_list()

        subj = "Server Status Report - # of failures: " + str(len(fail_list))
        # noinspection PyListCreation
        msg = []  # Email Message Body
        msg.append('Failure report: \n')
        msg.append('# of failures: ' + str(len(fail_list)) + '\n')
        msg.append('# of services monitored: ' + str(len(monitor_list)) + '\n')

        msg.append(generate_fail_list(fail_list, monitor_list))

        msg.append('\n\nReport Generated @ ' + str(datetime.now()))
        print(''.join(msg))
        logging.debug('BREAKPOINT')
        email_controller.send_gmail().send(subject=subj, text=''.join(msg))
        # db_helpers.email_log.log_email_sent(''.join(msg))