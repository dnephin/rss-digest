import datetime
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
        self.renderer = mock.create_autospec(email.DigestEmailRenderer)
        self.email = email.DigestEmail(self.feed, self.renderer)
        with mock.patch('rssdigest.email.send_email') as self.mock_send_email:
            yield

    def test_send(self):
        autospec_method(self.email.handle_response)
        self.email.send()
        self.mock_send_email.assert_called_with(
            self.email.mail_config,
            self.feed.config.list_name,
            self.email.renderer.build_email.return_value)
        self.email.handle_response.assert_called_with(
            self.mock_send_email.return_value)


class DigestEmailRendererTestCase(TestCase):

    @setup
    def setup_renderer(self):
        self.feed = mock.Mock()
        self.renderer = email.DigestEmailRenderer(self.feed)

    @mock.patch('rssdigest.email.pynliner', autospec=True)
    def test_build_email(self, mock_pynliner):
        autospec_method(self.renderer.render_template)
        autospec_method(self.renderer.build_context)
        email_content = self.renderer.build_email()
        expected = email.EmailContent(
            self.renderer.build_context.return_value.title,
            mock_pynliner.Pynliner.return_value.from_string.return_value.run.return_value,
            self.renderer.render_template.return_value)
        assert_equal(email_content, expected)
        self.renderer.build_context.assert_called_with()
        assert_equal(self.renderer.render_template.mock_calls,
            [mock.call(self.renderer.config.html_template,
                       self.renderer.build_context.return_value),
            mock.call(self.renderer.config.text_template,
                      self.renderer.build_context.return_value)])

    def test_render_template(self):
        context = {
            'title': 'the title',
            'items': [mock.Mock(), mock.Mock()]
        }
        rendered = self.renderer.render_template(
            self.renderer.config.html_template, context)
        assert rendered.startswith('<html>')


class TextHelpersTestCase(TestCase):

    def test_slugify(self):
        expected = 'the-slug'
        assert_equal(email.slugify('ThE  !.-\n\t slug'), expected)

    def test_truncate(self):
        expected = 'starting with...'
        text = 'starting with a long string is a good idea.'
        assert_equal(email.truncate(text, 13), expected)


class DigestEmailContextTestCase(TestCase):

    @setup
    def setup_context(self):
        self.feed = mock.Mock()
        self.date = datetime.date(2013, 4, 4)
        self.context = email.DigestEmailContext(self.feed, self.date)

    def test_title(self):
        expected ='%s digest for April 04, 2013' % self.feed.config.name
        assert_equal(self.context.title, expected)


class HandleResponseTestCase(TestCase):

    @setup_teardown
    def patch_logger(self):
        self.feed = mock.Mock(recent_items=[])
        self.response = mock.Mock()
        self.renderer = mock.create_autospec(email.DigestEmailRenderer)
        self.email = email.DigestEmail(self.feed, self.renderer)
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
       
