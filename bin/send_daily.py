#!/usr/bin/env python

import optparse
import staticconf

from rssdigest import config
from rssdigest.batch import dailydigest


def parse_opts():
    parser = optparse.OptionParser()
    parser.add_option('-c', '--email-config', default='config/email.yaml')
    parser.add_option('--rssdigest-config', default=config.path)
    parser.add_option('-o', '--override', action='append', default=[])
    parser.add_option('--api-key')
    opts, args = parser.parse_args()
    return opts


def load_config(opts):
    config.load_app_config(opts.api_key)
    staticconf.YamlConfiguration(opts.email_config)
    config.load(opts.rssdigest_config)
    staticconf.ListConfiguration(opts.override)
    

if __name__ == "__main__":
    opts = parse_opts()
    config.setup_logging()
    load_config(opts)
    dailydigest.run()
