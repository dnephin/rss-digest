from testify import TestCase, setup, setup_teardown, assert_equal
import mock

from rssdigest import email


def autospec_method(method, *args, **kwargs):
    """create an autospec for an instance method."""
    mocked_method = mock.create_autospec(method, *args, **kwargs)
    setattr(method.im_self, method.__name__, mocked_method)


class SendEmailTestCase(TestCase):

    @setup_teardown
    def patch_requests(self):
        self.config = mock.Mock()
        self.list_name = 'list_name'
        self.email_content = mock.Mock()
        patcher = mock.patch('rssdigest.email.requests')
        with patcher as self.mock_requests:
            yield

    def test_send_email(self):
        resp = email.send_email(self.config, self.list_name, self.email_content)
        assert_equal(resp, self.mock_requests.post.return_value)


class DigestEmailTestCase(TestCase):

    @setup_teardown
    def setup_email(self):
        self.feed = mock.Mock()
        self.email = email.DigestEmail(self.feed)
        with mock.patch('rssdigest.email.send_email') as self.mock_send_email:
            yield

    def test_send(self):
        autospec_method(self.email.handle_response)
        autospec_method(self.email.build_email)
        self.email.send()
        self.mock_send_email.assert_called_with(
            self.email.config,
            self.feed.config.list_name,
            self.email.build_email.return_value)
        self.email.handle_response.assert_called_with(
            self.mock_send_email.return_value)


class HandleResponseTestCase(TestCase):

    @setup_teardown
    def patch_logger(self):
        self.feed = mock.Mock(recent_items=[])
        self.response = mock.Mock()
        self.email = email.DigestEmail(self.feed)
        with mock.patch('rssdigest.email.log') as self.mock_log:
            yield

    def test_handle_response_success(self):
        self.response.status_code = 200
        self.email.handle_response(self.response) 
        assert_equal(self.mock_log.info.call_count, 1)

    def test_handle_response_error(self):
        self.response.status_code = 400
        self.email.handle_response(self.response)
        assert_equal(self.mock_log.warn.call_count, 1)
       
