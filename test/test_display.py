"""Test mta monitor submodule."""

from unittest import mock

import pytest

import underground
from traindisplay import display

# a list of checking scenarios with their desired answer
UPDATE_SCENARIOS = [
    # last check is recent, do not update
    (dict(last_check_ts=0, last_display_ts=1), False),
    (dict(last_check_ts=1, last_display_ts=0), True),
]


@mock.patch("underground.dateutils.current_time")
@pytest.mark.parametrize("scenario, expect", UPDATE_SCENARIOS)
def test_needs_update(mock_current_time, scenario, expect):
    """Test the update logic."""
    mock_current_time.return_value = underground.dateutils.epoch_to_datetime(100)

    # unpack unix stamps to datetimes
    last_display_ts = underground.dateutils.epoch_to_datetime(
        scenario["last_display_ts"]
    )
    last_check_dt = underground.dateutils.epoch_to_datetime(scenario["last_check_ts"])

    assert display.needs_update(last_check_dt, last_display_ts) == expect
