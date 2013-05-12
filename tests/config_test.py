
import datetime
from testify import TestCase, assert_equal
import pytz

from rssdigest import config


class ValidateUTCDatetimeTestCase(TestCase):

    def test_validate_utc_datetime(self):
        date = '2010-01-01 01:01:01'
        expected = datetime.datetime(2010, 1, 1, 1, 1, 1,
            tzinfo=pytz.timezone('UTC'))
        assert_equal(config.validate_utc_datetime(date), expected)
