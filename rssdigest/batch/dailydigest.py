"""
Send emails to all subscribers for each feed with new items.
"""

import datetime
import itertools
import logging
import pytz
import staticconf

from rssdigest import feeds, email, config


log = logging.getLogger(__name__)


def get_default_min_entry_date():
    tz = pytz.timezone('UTC')
    return datetime.datetime.now(tz) - datetime.timedelta(days=1)


class DailyDigestConfigSchema(object):

    is_production = staticconf.get_bool('is_production')
    feed_configs = config.get_feed_config('feeds')
    min_entry_date = config.get_utc_datetime(
        'min_entry_date', default=get_default_min_entry_date())


def get_feeds_with_new_entries(feed_configs, min_datetime):
    return itertools.ifilter(None, 
        (feeds.get_feed_entries(feed_config, min_datetime)
        for feed_config in feed_configs))


def update_for_environment(feed):
    if DailyDigestConfigSchema.is_production:
        return
    feed.config.config['list_name'] = 'dev-test'


def run():
    min_datetime = DailyDigestConfigSchema.min_entry_date
    log.info("Starting daily digest for %s", min_datetime)

    feed_configs = DailyDigestConfigSchema.feed_configs
    for feed in get_feeds_with_new_entries(feed_configs, min_datetime):
        update_for_environment(feed)
        email.send_digest(feed)
