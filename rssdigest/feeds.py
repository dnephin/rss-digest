"""
Read rss/atom feeds.
"""

from collections import namedtuple
import datetime
import feedparser
import logging
import pytz


log = logging.getLogger(__name__)

# TODO:make staticconf.Schema accept a path argument
class FeedConfig(object):

    def __init__(self, config_dict):
        self.config = config_dict

    def __getattr__(self, name):
        return self.config[name]


Feed = namedtuple('Feed', 'feed config recent_items')


def parse_date(feed_config, date_string):
    lstrip, rstrip = feed_config.date_strip
    date_string = date_string[lstrip:][:-rstrip]
    naive_dt = datetime.datetime.strptime(date_string, feed_config.date_format)
    return naive_dt.replace(tzinfo=pytz.timezone(feed_config.time_zone))


def get_recent_items(feed_config, feed, min_datetime):
    def date_filter(feed_item):
        feed_item['date'] = parse_date(feed_config, feed_item['updated'])
        return feed_item['date'] > min_datetime
    return filter(date_filter, feed.entries)


def get_feed_entries(feed_config, min_datetime):
    feed = feedparser.parse(feed_config.url)
    recent_items = get_recent_items(feed_config, feed, min_datetime)
    if not recent_items:
        log.warn("No entries for %s", feed_config.name)
        return

    return Feed(feed, feed_config, recent_items)


