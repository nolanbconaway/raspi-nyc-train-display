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


def kv_store() -> SqliteDict:
    """Make a SQLite dict KV store."""
    return SqliteDict(SQLITE_PATH, autocommit=True)


def setter(**kw) -> None:
    """Set one or more database values, specified by kwargs."""
    with kv_store() as data:
        for k, v in kw.items():
            data[k] = v


def getter(k: str, default=None):
    """Get a database value, return the default if the key is not in the database."""
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
    return setter(last_check_dt=dt)


def get_next_stops() -> typing.Iterable[datetime.datetime]:
    """Get the datetime of the last subway feed check.
    
    This is a wrapper around the getter function, it simply knows the key name.
    """
    return getter("stops_dt", default=[])


def set_next_stops(dts: typing.Iterable[datetime.datetime]):
    """Set the datetime of the last subway feed check.
    
    This is a wrapper around the setter function, it simply knows the key name.
    """
    return setter(stops_dt=dts)


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


def wipe() -> None:
    """Delete all data in the dict."""
    with kv_store() as data:
        for key in list(data.keys()):
            del data[key]
