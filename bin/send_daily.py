#!/usr/bin/env python

import heroku
import logging
import optparse

from rssdigest.batch import dailydigest

log = logging.getLogger(__name__)


def parse_opts(self):
    parser = optparser.OptionParser()
    parser.add_option('-c', '--config')
    parser.add_option('-a', '--api_key')
    opts, args = parser.parse_args()
    return opts


def get_app(api_key):
    cloud = heroku.from_key(api_key)
    return cloud.apps['rss-digest']


if __name__ == "__main__":
    opts = parse_opts()
    app = get_app(opts.api_key)
    # TODO: put config into staticconf
    daily_digest.run()
