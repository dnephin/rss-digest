#!/usr/bin/env python
"""
 Scale dynos
"""

import heroku
import logging
import optparse
import os

from rssdigest import config

log = logging.getLogger(__name__)

def parse_opts():
    parser = optparse.OptionParser()
    parser.add_option('-t', '--type', default='web')
    parser.add_option('--app-name', default=config.app_name)
    parser.add_option('-n', '--num-dynos', type='int', default=0)
    opts, _ = parser.parse_args()

    if opts.num_dynos not in (0, 1):
        parser.error("Can not scale to %s" % opts.num_dynos)

    return opts


def scale(app, dyno_type, quantity):
    resp = app._h._http_resource(
        method='POST',
        resource=('apps', app.name, 'ps', 'scale'),
        data={'type': dyno_type, 'qty': quantity})
    if resp.status_code != 200:
        log.warn("Failed to scale: %s, %s", resp.status_code, resp.content)
        return
    log.warn("Scaled %s to %s", dyno_type, resp.content)


def main(dyno_type, quantity):
    cloud   = heroku.from_key(os.environ.get('HEROKU_API_KEY'))
    app     = cloud.apps[config.app_name]
    scale(app, dyno_type, quantity)


if __name__ == "__main__":
    opts = parse_opts()
    config.setup_logging()
    main(opts.type, opts.num_dynos)
