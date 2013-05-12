
import datetime
from testify import TestCase, setup, setup_teardown, assert_equal
import mock
import pytz

from rssdigest.batch import dailydigest


class ValidateUTCDatetimeTestCase(TestCase):

    def test_validate_utc_datetime(self):
        date = '2010-01-01 01:01:01'
        expected = datetime.datetime(2010, 1, 1, 1, 1, 1,
            tzinfo=pytz.timezone('UTC'))
        assert_equal(dailydigest.validate_utc_datetime(date), expected)
