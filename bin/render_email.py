#!/usr/bin/env python
"""
Render a DigestEmail with a feed and print the results to files.
"""

import datetime
import feedparser
import pytz
import optparse
import random

from rssdigest import feeds, email, config
from rssdigest.batch.dailydigest import DailyDigestConfigSchema


def get_utc_days_ago(num):
    tz = pytz.timezone('UTC')
    return datetime.datetime.now(tz) - datetime.timedelta(days=num)


def get_opts():
    parser = optparse.OptionParser()
    parser.add_option('-n', '--index',  type='int', default=None)
    opts, _ = parser.parse_args()
    return opts
   

def get_feed_config(index):
    feed_configs = DailyDigestConfigSchema.feed_configs
    if index is None:
        return random.choice(feed_configs)
    return feed_configs[index]
   
def get_feed(feed_config):
    min_datetime = get_utc_days_ago(80)
    with open('./samples/%s.xml' % feed_config.list_name, 'r') as f:
        feed = feedparser.parse(f)
    return feeds.normalize(feed, feed_config, min_datetime)

def main():
    opts = get_opts()
    config.load()
    config.setup_logging()
    feed = get_feed(get_feed_config(opts.index))
    if not feeds:
        print "Oops, no recent items."
        return
    render(feed)

def render(feed):
    renderer = email.DigestEmailRenderer(feed)
    email_content = renderer.build_email()
    with open('email.html', 'w') as f:
        f.write(email_content.html.encode('utf8'))
    with open('email.txt', 'w') as f:
        f.write(email_content.text.encode('utf8'))
    print "Subject %s" % email_content.subject
     

if __name__ == "__main__":
    main()
