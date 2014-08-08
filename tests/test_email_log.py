from unittest import TestCase

__author__ = 'Jesse Laptop'

from db_helpers import email_log

import logging

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG)


class TestEmail_log(TestCase):
    def test_email_sent_x_minutes_ago(self):
        """ Makes sure the time sent is a proper positive float """
        x = email_log.email_sent_x_minutes_ago()
        logging.debug(x)
        self.assertGreater(x, 0)