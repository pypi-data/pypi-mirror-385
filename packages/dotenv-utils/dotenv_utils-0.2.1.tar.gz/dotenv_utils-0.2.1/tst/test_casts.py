from datetime import date, datetime, time, timedelta
from pathlib import Path
from urllib.parse import ParseResult

import pytest

from dotenv_utils.casts import (
    str2bool,
    str2date,
    str2int,
    str2float,
    str2datetime,
    str2time,
    str2timedelta,
    str2path,
    str2url,
    str2json,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("true", True),
        ("True", True),
        ("t", True),
        ("1", True),
        ("yes", True),
        ("Y", True),
        (" false ", False),
        ("F", False),
        ("0", False),
        ("no", False),
        ("N", False),
    ],
)
def test_str2bool_valid(value, expected):
    assert str2bool(value) is expected


def test_str2bool_invalid():
    with pytest.raises(ValueError):
        str2bool("maybe")


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2024-01-31", date(2024, 1, 31)),
    ],
)
def test_str2date(value, expected):
    assert str2date(value) == expected


@pytest.mark.parametrize(
    "value, exc",
    [
        ("2024-13-01", ValueError),
        ("not-a-date", ValueError),
    ],
)
def test_str2date_errors(value, exc):
    with pytest.raises(exc):
        str2date(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("42", 42),
        ("  -7  ", -7),
    ],
)
def test_str2int(value, expected):
    assert str2int(value) == expected


@pytest.mark.parametrize("value", ["forty-two", "3.14"])  # not valid int strings
def test_str2int_errors(value):
    with pytest.raises(ValueError):
        str2int(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("3.14", 3.14),
        ("  -2.5  ", -2.5),
        ("1e3", 1000.0),
    ],
)
def test_str2float(value, expected):
    assert str2float(value) == pytest.approx(expected)


@pytest.mark.parametrize("value", ["NaNish", "one.two"])  # not valid float strings
def test_str2float_errors(value):
    with pytest.raises(ValueError):
        str2float(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2025-10-20T12:34:56", datetime(2025, 10, 20, 12, 34, 56)),
        (" 2025-10-20 12:34:56 ", datetime(2025, 10, 20, 12, 34, 56)),
    ],
)
def test_str2datetime(value, expected):
    assert str2datetime(value) == expected


@pytest.mark.parametrize("value", ["2025-13-01T00:00:00", "not-a-datetime"])  # invalid
def test_str2datetime_errors(value):
    with pytest.raises(ValueError):
        str2datetime(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("12:34:56", time(12, 34, 56)),
        (" 12:34:56 ", time(12, 34, 56)),
    ],
)
def test_str2time(value, expected):
    assert str2time(value) == expected


@pytest.mark.parametrize("value", ["25:00:00", "not-a-time"])  # invalid
def test_str2time_errors(value):
    with pytest.raises(ValueError):
        str2time(value)


@pytest.mark.parametrize(
    "value",
    [
        ".",  # current directory
        "~",  # home directory
    ],
)
def test_str2path(value):
    p = str2path(value)
    assert isinstance(p, Path)
    assert p.is_absolute()


def test_str2url():
    url = str2url("https://example.com:8443/path?q=1#frag")
    assert isinstance(url, ParseResult)
    assert url.scheme == "https"
    assert url.netloc == "example.com:8443"
    assert url.path == "/path"
    assert url.query == "q=1"
    assert url.fragment == "frag"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("{\"a\": 1}", {"a": 1}),
        ("  [1, 2, 3]  ", [1, 2, 3]),
        ("null", None),
        ("true", True),
        ("false", False),
        ("\"text\"", "text"),
    ],
)
def test_str2json_valid(value, expected):
    assert str2json(value) == expected


@pytest.mark.parametrize("value", ["{a: 1}", "[1, 2,", "not json"])
def test_str2json_invalid(value):
    with pytest.raises(ValueError):
        str2json(value)



@pytest.mark.parametrize(
    "value, expected",
    [
        ("5d", timedelta(days=5)),
        ("2h", timedelta(hours=2)),
        ("30m", timedelta(minutes=30)),
        ("45s", timedelta(seconds=45)),
        ("1d 2h 30m", timedelta(days=1, hours=2, minutes=30)),
        (" 1D  2H ", timedelta(days=1, hours=2)),  # case and whitespace insensitive
        ("0s", timedelta(seconds=0)),
    ],
)
def test_str2timedelta_valid(value, expected):
    assert str2timedelta(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "abc",
        "5",  # missing unit
        "1x",  # unknown unit
        "h1",  # wrong order within token
        "2m 1h",  # wrong order overall (should be d h m s)
        "5d xyz",  # trailing garbage should not be accepted
    ],
)
def test_str2timedelta_invalid(value):
    with pytest.raises(ValueError):
        str2timedelta(value)
