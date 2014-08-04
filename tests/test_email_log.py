import logging
from unittest import TestCase

__author__ = 'Jesse Laptop'

from db_helpers import email_log


class TestEmail_log(TestCase):
    def test_email_sent_x_minutes_ago(self):
        x = email_log.email_sent_x_minutes_ago()
        logging.debug(x)
        self.assertGreater(x, -1)