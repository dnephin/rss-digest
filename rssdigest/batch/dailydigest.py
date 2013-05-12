"""
Send emails to all subscribers for each feed with new items.
"""

import datetime
import itertools
import logging
import pytz
import staticconf
from staticconf import getters, validation

from rssdigest import feeds, email


log = logging.getLogger(__name__)


def get_default_min_entry_date():
    tz = pytz.timezone('UTC')
    return datetime.datetime.now(tz) - datetime.timedelta(days=1)


def validate_utc_datetime(value):
     tz = pytz.timezone('UTC')
     return validation.validate_datetime(value).replace(tzinfo=tz)

get_utc_datetime = getters.build_getter(validate_utc_datetime)


class DailyDigestConfigSchema(object):

    feed_configs = [
        feeds.FeedConfig,
    ]
    min_entry_date = get_utc_datetime(
        'min_entry_date', default=get_default_min_entry_date())


def get_feeds_with_new_entries(feed_configs, min_datetime):
    return itertools.ifilter(None, 
        (feeds.get_feed_entries(feed_config, min_datetime)
        for feed_config in feed_configs))


def run():
    min_datetime = DailyDigestConfigSchema.min_entry_date
    log.info("Starting daily digest for %s", min_datetime)

    feed_configs = DailyDigestConfigSchema.feed_configs
    for feed in get_feeds_with_new_entries(feed_configs, min_datetime):
        email.send_digest(feed)
