#!/usr/bin/env python

import heroku
import logging
import optparse
import staticconf

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
    config.setup_logging()
    load_config(opts)
    dailydigest.run()
