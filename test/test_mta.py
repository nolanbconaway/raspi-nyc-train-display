"""Test mta monitor submodule."""

import os
from unittest import mock

import pytest

import underground
from traindisplay import mta

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


@pytest.fixture()
def fake_json_file():
    """Set up and tear down the fake json file.
    
    It needs to exist only in order to pass 
    """
    fake_file_path = os.path.join(".train_display_test.json")
    with open(fake_file_path, "w"):
        pass

    yield fake_file_path

    if os.path.exists(fake_file_path):
        os.remove(fake_file_path)


@mock.patch("json.load")
@mock.patch("underground.dateutils.current_time")
@pytest.mark.parametrize("scenario, expect", UPDATE_SCENARIOS)
def test_needs_update(
    mock_current_time, mock_json_load, scenario, expect, fake_json_file
):
    """Test the update logic."""
    mock_current_time.return_value = underground.dateutils.epoch_to_datetime(
        scenario["now_ts"]
    )
    mock_json_load.return_value = scenario

    assert mta.needs_update(fake_json_file) == expect
