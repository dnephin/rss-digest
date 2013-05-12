#!/usr/bin/env python

import heroku
import logging
import optparse
import staticconf
import sys

from rssdigest import config
from rssdigest.batch import dailydigest


log = logging.getLogger(__name__)


def parse_opts():
    parser = optparse.OptionParser()
    parser.add_option('-c', '--email-config', default='config/email.yaml')
    parser.add_option('--rssdigest-config', default=config.path)
    parser.add_option('-a', '--api_key')
    parser.add_option('-o', '--override', action='append', default=[])
    opts, args = parser.parse_args()
    return opts


def setup_logging(verbose=True):
    fmt = "%(asctime)s %(levelname)7s  %(name)s  %(message)s"
    level = logging.INFO if verbose else logging.WARN
    logging.basicConfig(stream=sys.stdout, level=level, format=fmt)


def get_app(api_key):
    cloud = heroku.from_key(api_key)
    return cloud.apps['rss-digest']


def load_config(opts):
    app = get_app(opts.api_key)
    staticconf.DictConfiguration(app.config.data, namespace='app_config')
    staticconf.YamlConfiguration(opts.email_config)
    config.load(opts.rssdigest_config)
    staticconf.ListConfiguration(opts.override)
    

if __name__ == "__main__":
    opts = parse_opts()
    setup_logging()
    load_config(opts)
    dailydigest.run()
