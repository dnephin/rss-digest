
import heroku
import logging
import os
import pytz
import staticconf
from staticconf import getters, validation
import sys

from rssdigest import feeds


path = 'config/rssdigest.yaml'
app_name = 'rss-digest'


def load(path=path):
    staticconf.YamlConfiguration(path)


def validate_utc_datetime(value):
     tz = pytz.timezone('UTC')
     return validation.validate_datetime(value).replace(tzinfo=tz)

get_utc_datetime = getters.build_getter(validate_utc_datetime)


def validate_feed_config(value):
    return feeds.FeedConfig(value)

get_feed_config = getters.build_getter(
    validation.build_list_type_validator(validate_feed_config))


def setup_logging(verbose=True):
    fmt = "%(asctime)s %(levelname)7s  %(name)s  %(message)s"
    level = logging.INFO if verbose else logging.WARN
    logging.basicConfig(stream=sys.stdout, level=level, format=fmt)


def get_app(api_key):
    cloud = heroku.from_key(api_key)
    return cloud.apps[app_name]


def load_app_config(api_key=None):
    app = get_app(api_key or os.environ.get('HEROKU_API_KEY'))
    staticconf.DictConfiguration(app.config.data, namespace='app_config')
