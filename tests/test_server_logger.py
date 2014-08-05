from unittest import TestCase
import db_helpers
import report_generator

__author__ = 'Jesse Laptop'


class TestServer_logger(TestCase):
    def test_check_server_status_report_logic(self):

        self.alert_timeout = 5
        if db_helpers.email_log.email_sent_x_minutes_ago() < self.alert_timeout:
            report_generator.reports.generate_report()
            # TODO This is the root function for all reporting