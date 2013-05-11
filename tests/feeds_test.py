import contextlib
import datetime
import pytz
import mock
from testify import TestCase, assert_equal, setup, setup_teardown

from rssdigest import feeds

class ParseDateTestCase(TestCase):

    @setup
    def setup_config(self):
        self.config = mock.Mock(
            date_format="%Y-%m-%dT%H:%M:%S",
            time_zone='MST',
            date_strip=(0, 6))

    def test_parse_date(self):
        date_string = u'2013-05-07T15:00:43-07:00'
        expected = datetime.datetime(2013, 5, 7, 15, 0, 43,
            tzinfo=pytz.timezone('MST'))
        assert_equal(feeds.parse_date(self.config, date_string), expected)
      
    def test_recent_items(self):
        base_date = datetime.datetime(2013, 4, 12, tzinfo=pytz.timezone('EST'))
        def build_date_string(i):
            dt = base_date + datetime.timedelta(days=i)
            return dt.strftime(self.config.date_format) + "a" * 6
        entries = [dict(updated=build_date_string(i)) for i in range(-3, 3)]
        feed = mock.MagicMock(entries=entries)
        recent = feeds.get_recent_items(self.config, feed, base_date)
        assert_equal(recent, entries[3:])
        assert recent[0]['date'] 


class GetFeedEntriesTestCase(TestCase):

    @setup_teardown
    def patch_deps(self):
        self.config = mock.Mock(url='url', name='name')
        self.min_datetime = mock.Mock()
        with contextlib.nested(
            mock.patch('rssdigest.feeds.feedparser'),
            mock.patch('rssdigest.feeds.get_recent_items')
        ) as (self.mock_parser, self.mock_get_recent):
            yield

    def test_get_feed_entries_none(self):
        self.mock_get_recent.return_value = []
        feed = feeds.get_feed_entries(self.config, self.min_datetime)
        assert not feed
        self.mock_parser.parse.assert_called_with(self.config.url)
        self.mock_get_recent.assert_called_with(self.config, 
            self.mock_parser.parse.return_value, self.min_datetime)

    def test_get_feed_entires_some(self):
        self.mock_get_recent.return_value = [mock.Mock()]
        feed = feeds.get_feed_entries(self.config, self.min_datetime)
        assert_equal(feed.feed, self.mock_parser.parse.return_value)
        assert_equal(feed.recent_items, self.mock_get_recent.return_value)

