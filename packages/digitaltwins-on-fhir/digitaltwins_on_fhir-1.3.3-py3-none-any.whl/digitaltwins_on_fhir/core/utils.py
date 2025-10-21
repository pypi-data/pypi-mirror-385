import datetime
import pytz
from datetime import timezone

FHIR_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
FHIR_DATE_FORMAT = "%Y-%m-%d"


def _format_date_time(date: datetime.datetime):
    return pytz.utc.normalize(date).strftime(FHIR_DATE_TIME_FORMAT)


def _format_date(date: datetime.date):
    return date.strftime(FHIR_DATE_FORMAT)


def transform_value(value):
    """
    >>> transform_value(datetime.datetime(2019, 1, 1, tzinfo=pytz.utc))
    '2019-01-01T00:00:00Z'

    >>> transform_value(datetime.date(2019, 1, 1))
    '2019-01-01'

    >>> transform_value(True)
    'true'
    """
    if isinstance(value, datetime.datetime):
        return _format_date_time(value)
    if isinstance(value, datetime.date):
        return _format_date(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return value

