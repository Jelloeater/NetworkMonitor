from datetime import datetime
import logging
# import db_helpers
# import email_controller

__author__ = 'Jesse Laptop'


class email_actions():
    @staticmethod
    def send_alert(server_info_object):

        logging.debug(server_info_object)
        # TODO handle multiple server log types (tcp,url,host)
        var = server_info_object.sl_host
        var = server_info_object.sl_port
        var = server_info_object.sl_service_type

        subj = "Server Status Report"
        # noinspection PyListCreation
        msg = []  # Email Message Body
        msg.append('The First Line: \n\n')
        msg.append('\nA message')

        msg.append('\n\nReport Generated @ ' + str(datetime.now()))

        logging.debug('Subject:' + subj)
        logging.debug(''.join(msg))
        # email_controller.send_gmail().send(subject=subj, text=''.join(msg))
        # db_helpers.email_log.log_email_sent(''.join(msg))