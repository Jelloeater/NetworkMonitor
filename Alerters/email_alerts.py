from datetime import datetime
import logging

from Database import db_helpers
from Alerters import email_controller


__author__ = 'Jesse Laptop'


class email_actions():
    def __init__(self):
        pass

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
    def parse_url_info(url_in):
        try:
            host_name = str(url_in).split(':')[1].strip('/')  # http://|www.x.com|:|8080|
            port = str(url_in).split(':')[2]
        except IndexError:
            host_name = str(url_in)  # http://www.google.com
            port = ''
        return host_name, port

    @staticmethod
    def generate_fail_table(fail_list_in, monitor_list_in):
        w_ts = 25
        w_hn = 50
        w_p = 8
        w_sr = 10
        w_no = 25
        width = (w_ts + w_hn + w_p + w_sr + w_no + 16)

        fail_list_txt = ["Servers:",
                         '\n' + '-' * width + '\n',
                         "| {0} | {1} | {2} | {3} | {4} |".format("Time Stamp".ljust(w_ts), "Hostname".ljust(w_hn),
                                                                  "Port".ljust(w_p),
                                                                  "Service".ljust(w_sr), "Note".ljust(w_no)),
                         '\n' + '-' * width + '\n']

        #
        # Beginning of item in list
        for fail_event in fail_list_in:
            host_name_fail_event = ''
            port = ''

            try:
                # Try to parse port from hostname address
                # (should still work even if host is removed from monitor_list)
                if fail_event[3] != 'url':
                    host_name_fail_event = str(fail_event[2]).split(':')[0]  # 127.0.0.1:80
                    port = str(fail_event[2]).split(':')[1]
                if fail_event[3] == 'url':
                    host_name_fail_event, port = email_actions.parse_url_info(fail_event[2])
            except IndexError:
                host_name_fail_event = str(fail_event[2])  # 127.0.0.1
                port = ''

            service = fail_event[3]
            time_stamp = str(fail_event[1])

            # Try to find note in
            note_txt = ''
            for monitor_item in monitor_list_in:
                monitor_item_host = monitor_item[1]
                monitor_item_type = monitor_item[3]

                # TODO Need to pare out host_name if url
                # monitor_item[4] = 'url'  # TYPE CHECK
                if monitor_item_type != 'url':
                    if monitor_item_host == host_name_fail_event:
                        note_txt = monitor_item[4]
                        break
                if monitor_item_type == 'url':
                    host_name_parse = email_actions.parse_url_info(monitor_item_host)
                    if host_name_parse == host_name_fail_event:
                        note_txt = monitor_item[4]
                        break

            if note_txt is None:
                note_txt = ''

            fail_list_txt.append(
                "| {0} | {1} | {2} | {3} | {4} |".format(time_stamp.ljust(w_ts), host_name_fail_event.ljust(w_hn),
                                                         port.ljust(w_p), service.ljust(w_sr),
                                                         note_txt.ljust(w_no)))
            fail_list_txt.append('\n')
            # End of item in list

        # End of list
        fail_list_txt.append('-' * width + '\n', )
        logging.debug('BREAKPOINT')
        return ''.join(fail_list_txt)

    @staticmethod
    def generate_report():
        """ Created report of all fails since last email was sent """

        # Start message creation here
        fail_list = db_helpers.server_stats.failures_in_x_minutes_ago(
            db_helpers.email_log.email_sent_x_minutes_ago())

        monitor_list = db_helpers.monitor_list.get_server_list()

        unique_failed_monitors = list(set([x[2] for x in fail_list]))

        subj = "Server Status Report - # of failures: " + str(len(unique_failed_monitors))
        # noinspection PyListCreation
        msg = []  # Email Message Body
        msg.append('Failure report- \n')
        msg.append('# of failures: ' + str(len(fail_list)) + '\n')
        msg.append('# of services monitored: ' + str(len(monitor_list)) + '\n')
        msg.append('# of services failed: ' + str(len(unique_failed_monitors)) + '\n\n')

        msg.append('-' * 70 + '\n')
        msg.append('| Failed Servers / Services: \n')
        for i in unique_failed_monitors:
            msg.append('| ' + str(i) + '\n')
        msg.append('-' * 70 + '\n\n')

        # Calls the fail table generator above
        msg.append(email_actions.generate_fail_table(fail_list, monitor_list))

        msg.append("\nMonitored Servers / Services:" +
                   '\n' + '-' * 98 + '\n' + "| {0} | {1} | {2} | {3} |".format("Hostname".ljust(35), "Port".ljust(10),
                                                                               "Service".ljust(15),
                                                                               "Note".ljust(17 + 8)) +
                   '\n' + '-' * 98 + '\n')
        for i in monitor_list:
            msg.append("| {0} | {1} | {2} | {3} |".format(str(i[1]).ljust(35), str(i[2]).ljust(10),
                                                          str(i[3]).ljust(15), str(i[4]).ljust(17 + 8)), )
            msg.append('\n')
        msg.append('-' * 98)
        # FIXME Create nice looking table

        msg.append('\n\nReport Generated @ ' + str(datetime.now()))
        logging.debug('\n' + ''.join(msg))
        logging.debug('BREAKPOINT')
        # email_controller.send_gmail().send(subject=subj, text=''.join(msg))