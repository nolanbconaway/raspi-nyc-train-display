"""Test mta monitor submodule."""

import pytest

from traindisplay import mta

from . import epoch_to_datetime

# a list of checking scenarios with their desired answer
UPDATE_SCENARIOS = [
    # last check is recent, do not update
    (dict(now_ts=1, last_check_ts=0, stops_ts=[]), False),
    (dict(now_ts=0, last_check_ts=0, stops_ts=[]), False),
    (dict(now_ts=1, last_check_ts=0, stops_ts=[-1]), False),
    (dict(now_ts=0, last_check_ts=0, stops_ts=[-1]), False),
    (dict(now_ts=1, last_check_ts=0, stops_ts=[2]), False),
    (dict(now_ts=0, last_check_ts=0, stops_ts=[2]), False),
    # last check is not recent, so update
    (dict(now_ts=301, last_check_ts=0, stops_ts=[]), True),
    (dict(now_ts=300, last_check_ts=0, stops_ts=[]), True),
    (dict(now_ts=301, last_check_ts=0, stops_ts=[100]), True),
    (dict(now_ts=300, last_check_ts=0, stops_ts=[100]), True),
    (dict(now_ts=301, last_check_ts=0, stops_ts=[302]), True),
    (dict(now_ts=300, last_check_ts=0, stops_ts=[302]), True),
    # no stops scheduled, so must wait full 300 seconds
    (dict(now_ts=100, last_check_ts=0, stops_ts=[]), False),
    # most recent stop has elapsed, so check
    (dict(now_ts=100, last_check_ts=0, stops_ts=[99]), True),
    (dict(now_ts=100, last_check_ts=0, stops_ts=[100]), True),
    (dict(now_ts=100, last_check_ts=0, stops_ts=[-1]), True),
    # most recent stop in future, so wait
    (dict(now_ts=100, last_check_ts=0, stops_ts=[101]), False),
]


@pytest.mark.parametrize("scenario, expect", UPDATE_SCENARIOS)
def test_needs_update(monkeypatch, scenario, expect):
    """Test the update logic."""
    # unpack unix stamps to datetimes

    now_dt = epoch_to_datetime(scenario["now_ts"])
    stops_dt = [epoch_to_datetime(i) for i in scenario["stops_ts"]]
    last_check_dt = epoch_to_datetime(scenario["last_check_ts"])

    monkeypatch.setattr("traindisplay.mta.current_time", lambda: now_dt)

    assert mta.needs_update(last_check_dt, stops_dt) == expect
