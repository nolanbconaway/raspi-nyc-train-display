"""Data storage utilities.

Both the MTA checker and display updater need to have some memory of the past
and implement their own decision logic.

This module should make the memory easier to manage.
"""
import datetime
import os
import typing

from sqlitedict import SqliteDict

SQLITE_PATH = os.getenv("TRAIN_DISPLAY_SQLITE_PATH", ".traindisplay.sqlite")

# the kws that are expected to be set
EXPECTED_KWS = {"last_check_dt", "last_display_dt", "stops_dt"}


def kv_store() -> SqliteDict:
    """Make a SQLite dict KV store."""
    return SqliteDict(SQLITE_PATH, autocommit=True)


def setter(_expected=True, **kw) -> None:
    """Set one or more database values, specified by kwargs.
    
    This checks that the keys are expected, unless _expected is set to False.
    """
    with kv_store() as data:
        for k, v in kw.items():
            if _expected and k not in EXPECTED_KWS:
                raise ValueError(f"Unknown database key: {k}.")
            data[k] = v


def getter(k: str, default=None, _expected=True):
    """Get a database value.
    
    This checks that the key is expected, unless _expected is set to False.
    """
    if _expected and k not in EXPECTED_KWS:
        raise ValueError(f"Unknown database key: {k}.")

    with kv_store() as data:
        return data.get(k, default)


def get_last_check() -> datetime.datetime:
    """Get the datetime of the last subway feed check.
    
    This is a wrapper around the getter function, it simply knows the key name.
    """
    return getter("last_check_dt")


def set_last_check(dt: datetime.datetime) -> datetime.datetime:
    """Set the datetime of the last subway feed check.
    
    This is a wrapper around the setter function, it simply knows the key name.
    """
    setter(last_check_dt=dt)


def get_next_stops() -> typing.Iterable[datetime.datetime]:
    """Get the datetime of the last subway feed check.
    
    This is a wrapper around the getter function, it simply knows the key name.
    """
    return getter("stops_dt", default=[])


def set_next_stops(dts: typing.Iterable[datetime.datetime]):
    """Set the datetime of the last subway feed check.
    
    This is a wrapper around the setter function, it simply knows the key name.
    """
    setter(stops_dt=dts)


def get_last_display() -> datetime.datetime:
    """Get the datetime of the last subway feed check.
    
    This is a wrapper around the getter function, it simply knows the key name.
    """
    return getter("last_display_dt")


def set_last_display(dt: datetime.datetime) -> datetime.datetime:
    """Set the datetime of the last subway feed check.
    
    This is a wrapper around the setter function, it simply knows the key name.
    """
    setter(last_display_dt=dt)
