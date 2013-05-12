#!/usr/bin/env python
"""
Render a DigestEmail with a feed and print the results to files.
"""

import datetime
import pytz

from rssdigest import feeds, email, config
from rssdigest.batch.dailydigest import DailyDigestConfigSchema


def get_utc_days_ago(num):
    tz = pytz.timezone('UTC')
    return datetime.datetime.now(tz) - datetime.timedelta(days=num)


def main():
    config.load()
    feed_configs = DailyDigestConfigSchema.feed_configs
    min_datetime = get_utc_days_ago(10)
    feed = feeds.get_feed_entries(feed_configs[0], min_datetime)
    renderer = email.DigestEmailRenderer(feed)
    email_content = renderer.build_email()
    with open('email.html', 'w') as f:
        f.write(email_content.html)
    with open('email.txt', 'w') as f:
        f.write(email_content.text)
    print "Subject %s" % email_content.subject
     

if __name__ == "__main__":
    main()
