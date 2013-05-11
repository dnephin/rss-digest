from testify import TestCase, setup, setup_teardown, assert_equal
import mock

from rssdigest import emailer


class SendEmailTestCase(TestCase):

    @setup_teardown
    def patch_requests(self):
        patcher = mock.patch('rssdigest.email.requests')
        with patcher as self.mock_requests:
            yield

    def test_send_email(self):
        pass

