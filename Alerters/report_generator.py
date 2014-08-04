from datetime import datetime
import logging

from Alerters import email
from Database import db_controller
from Database import db_helpers


__author__ = "Jesse S"
__license__ = "GNU GPL v2.0"
__version__ = "1.2"
__email__ = "jelloeater@gmail.com"


class reports:
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

        email.send_gmail().send(subject=subj, text=''.join(msg))
        db_helpers.email_log.log_email_sent(''.join(msg))


