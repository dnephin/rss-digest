"""
Send emails to all subscribers for each feed with new items.
"""

import datetime
import itertools

from rssdigest import feeds, email


class DailyDigestConfigSchema(object):
    
    feed_configs = []


def get_min_datetime():
    # TODO: read from config
   return datetime.datetime.now() - datetime.timedelta(days=1)


def get_feeds_with_new_entries(feed_configs, min_datetime):
    return itertools.ifilter(None, 
        (feeds.get_feed_entries(feed_config, min_datetime)
        for feed_config in feed_configs))


def run():
    min_datetime = get_min_datetime()
    feed_configs = DailyDigestConfigSchema.feed_configs
    for feed in get_feeds_with_new_entries(feed_configs, min_datetime):
        email.send_digest(feed)
