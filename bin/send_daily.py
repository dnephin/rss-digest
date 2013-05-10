#!/usr/bin/env python

import logging
import optparse

from rssdigest.batch import dailydigest

log = logging.getLogger(__name__)


def parse_opts(self):
    parser = optparser.OptionParser()
    parser.add_option('-c', '--config')
    opts, args = parser.parse_args()
    return opts


if __name__ == "__main__":
    opts = parse_opts()
    daily_digest.run()
