from datetime import datetime

import pytest

import config
from reminder_engine import parse_due_datetime


def test_tomorrow_time_is_future_and_timezone_aware():
    due = parse_due_datetime("tomorrow 09:15")
    assert due.tzinfo is not None
    assert due.date() > datetime.now(config.TIMEZONE).date()
    assert due.strftime("%H:%M") == "09:15"


def test_full_date_formats_are_supported():
    assert parse_due_datetime("31-12-2099 18:30").strftime("%Y-%m-%d %H:%M") == "2099-12-31 18:30"
    assert parse_due_datetime("2099-12-31 18:30").strftime("%Y-%m-%d %H:%M") == "2099-12-31 18:30"


def test_invalid_date_time_is_rejected():
    with pytest.raises(ValueError):
        parse_due_datetime("not a real time")
