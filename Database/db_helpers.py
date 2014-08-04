"""
Provides a easy way for accessing all needed database functions
"""

import logging
from datetime import datetime

__author__ = 'Jesse'

from Database import db_controller


class email_log(object):
    @staticmethod
    def log_email_sent(to_list):
        logging.debug(to_list)
        conn, cur = db_controller.db_access().open_connection()
        cur.execute(
            'INSERT INTO email_log (time_stamp, to_address) VALUES (%s, %s)',
            (datetime.now(), str(to_list)))
        db_controller.db_access.close_connection(conn, cur)

    @staticmethod
    def email_sent_x_minutes_ago():
        minutes_ago = 0
        #TODO Deal with empty table use case

        conn, cur = db_controller.db_access().open_connection()
        cur.execute(
            'SELECT time_stamp FROM email_log ORDER BY time_stamp DESC LIMIT 1')
        then = cur.fetchone()[0]
        db_controller.db_access.close_connection(conn, cur)
        now = datetime.now()
        diff = (now - then).seconds
        return float(diff)/60


class monitor_list(object):
    # TODO maybe move into own module?
    """ CRUD access for monitor_list table """

    @staticmethod
    def get_server_list():
        """ Gets the entire monitor_list from db """
        # FIXME write getter for server list
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_fetch = cur.fetchall()
        db_controller.db_access.close_connection(conn, cur)
        return db_fetch

    @staticmethod
    def log_service_down(server_logger_obj):
        """ Takes error and logs list to db with timestamp """

        if server_logger_obj.sl_service_type == 'tcp':  # Combine ip and port for logging
            server_logger_obj.sl_host = server_logger_obj.sl_host + ':' + str(server_logger_obj.sl_port)
        logging.warning(server_logger_obj.sl_host + ' - ' + server_logger_obj.sl_service_type + ' is DOWN')
        conn, cur = db_controller.db_access().open_connection()
        cur.execute(
            'INSERT INTO server_stats (time_stamp, ip_hostname, service_type) VALUES (%s, %s, %s)',
            (datetime.now(), server_logger_obj.sl_host, server_logger_obj.sl_service_type))
        db_controller.db_access.close_connection(conn, cur)

    @staticmethod
    def remove_server_from_monitor_list(index_to_remove):
        conn, cur = db_controller.db_access().open_connection()
        cur.execute('DELETE FROM monitor_list WHERE index =' + index_to_remove)
        db_controller.db_access.close_connection(conn, cur)

    class tcp():
        def __init__(self):
            pass

        @staticmethod
        def create_server(ip_address, port):
            conn, cur = db_controller.db_access().open_connection()
            cur.execute('INSERT INTO monitor_list (hostname, port, service_type) VALUES (%s, %s, %s)',
                        (ip_address, port, 'tcp'))
            db_controller.db_access.close_connection(conn, cur)

    class host():
        def __init__(self):
            pass

        @staticmethod
        def create_server(ip_address):
            conn, cur = db_controller.db_access().open_connection()
            cur.execute('INSERT INTO monitor_list (hostname, service_type) VALUES (%s, %s)', (ip_address, 'host'))
            db_controller.db_access.close_connection(conn, cur)

    class url():
        def __init__(self):
            pass

        @staticmethod
        def create_server(web_url):
            conn, cur = db_controller.db_access().open_connection()
            cur.execute('INSERT INTO monitor_list (hostname, service_type) VALUES (%s, %s)', (web_url, 'url'))
            db_controller.db_access.close_connection(conn, cur)
