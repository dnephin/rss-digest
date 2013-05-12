#!/usr/bin/env python
"""
Render a DigestEmail with a feed and print the results to files.
"""

import datetime
import pytz
import optparse

from rssdigest import feeds, email, config
from rssdigest.batch.dailydigest import DailyDigestConfigSchema


def get_utc_days_ago(num):
    tz = pytz.timezone('UTC')
    return datetime.datetime.now(tz) - datetime.timedelta(days=num)


def get_opts():
    parser = optparse.OptionParser()
    parser.add_option('-n', '--index',  type='int', default=0)
    opts, _ = parser.parse_args()
    return opts
   

def main():
    opts = get_opts()
    config.load()
    feed_configs = DailyDigestConfigSchema.feed_configs
    min_datetime = get_utc_days_ago(10)
    feed = feeds.get_feed_entries(feed_configs[opts.index], min_datetime)
    renderer = email.DigestEmailRenderer(feed)
    email_content = renderer.build_email()
    with open('email.html', 'w') as f:
        f.write(email_content.html.encode('utf8'))
    with open('email.txt', 'w') as f:
        f.write(email_content.text.encode('utf8'))
    print "Subject %s" % email_content.subject
     

if __name__ == "__main__":
    main()
