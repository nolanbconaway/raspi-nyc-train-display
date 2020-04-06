"""Test mta monitor submodule."""

import pytest

from traindisplay import display

from . import epoch_to_datetime

# a list of checking scenarios with their desired answer
UPDATE_SCENARIOS = [
    # last check is recent, do not update
    (dict(last_check_ts=0, last_display_ts=1), False),
    (dict(last_check_ts=1, last_display_ts=0), True),
]


@pytest.mark.parametrize("scenario, expect", UPDATE_SCENARIOS)
def test_needs_update(monkeypatch, scenario, expect):
    """Test the update logic."""
    monkeypatch.setattr(
        "traindisplay.display.current_time", lambda: epoch_to_datetime(100)
    )

    # unpack unix stamps to datetimes
    last_display_ts = epoch_to_datetime(scenario["last_display_ts"])
    last_check_dt = epoch_to_datetime(scenario["last_check_ts"])

    assert display.needs_update(last_check_dt, last_display_ts) == expect
