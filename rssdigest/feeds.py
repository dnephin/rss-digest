"""
Read rss/atom feeds.
"""

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


def parse_date(feed_config, date_string):
    naive_dt = datetime.datetime.strptime(date_string, feed_config.date_format)
    return naive_dt.replace(tzinfo=pytz.timezone(feed_config.time_zone))


def get_recent_items(feed_config, feed, min_datetime):
    def date_filter(feed_item):
        return parse_date(feed_config, feed_item['updated']) > min_datetime
    return filter(date_filter, feed.entries)


def normalize(feed, feed_config, min_datetime):
    class_name = feed_config.normalize_class
    if class_name not in globals():
        raise ValueError("Unknown normalizer: %s" % class_name)
    return globals()[class_name](feed, feed_config, min_datetime)


def get_feed_entries(feed_config, min_datetime):
    feed = feedparser.parse(feed_config.url)
    feed = normalize(feed, feed_config, min_datetime)
    if not feed.items():
        log.warn("No entries for %s", feed_config.name)
        return
    return feed


def normalize_items(normalizer):
    return [normalizer.normalize_item(item) for item in get_recent_items(
                    normalizer.config, 
                    normalizer.feed,
                    normalizer.min_datetime)]
   

class PrismFeedNormalizer(object):

    def __init__(self, feed, config, min_datetime):
        self.feed = feed
        self.config = config
        self.min_datetime = min_datetime

    @property
    def issue(self):
        cover_date = self.feed['channel'].get('prism_coverdisplaydate')
        if not cover_date:
            return None
        date = datetime.datetime.strptime(cover_date, '%b %d %Y %I:%M:%S:000%p')
        return date.strftime("%B %d, %Y")

    def items(self):
        return normalize_items(self)

    def normalize_item(self, item):
        item = dict(item)
        item.update({
            'date':         item['prism_publicationdate'],
            'publication':  self.item_publication(item),
            'keywords':     self.item_keywords(item),
        })
        return item

    def item_keywords(self, item):
        return None if not item.get('tags') else item['tags'][0]['term']
 
    def item_publication(self, item):
        return 'Vol. %s No. %s %s-%s' % (
            item['prism_volume'],
            item['prism_number'],
            item['prism_startingpage'],
            item['prism_endingpage'])
       

class LancetFeedNormalizer(object):

    def __init__(self, feed, config, min_datetime):
        self.feed = feed
        self.config = config
        self.min_datetime = min_datetime

    @property
    def issue(self):
        return None

    def items(self):
        return normalize_items(self)

    def normalize_item(self, item):
        item = dict(item)
        item['summary'] = clean_trailing_brs(item['summary'])
        return item


def clean_trailing_brs(source):
    while source.endswith('<br />'):
        source = source[:-6]
    return source
