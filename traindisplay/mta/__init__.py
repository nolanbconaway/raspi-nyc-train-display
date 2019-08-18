"""Interact with the MTA API via underground."""
import datetime
import json
import os
import typing

import underground


def next_train_times(
    route_id: str, stop_id: str, **kw
) -> typing.List[datetime.datetime]:
    """Return a tuple of datetimes corresponding to the next trasins at a stop.
    
    Parameters
    ----------
    route_id : str
        Route ID.
    stop_id : str
        Stop ID, per stops.txt.
    **kw
        Passed to underground.SubwayFeed.get
        
    Returns
    -------
    list[datetime.datetime]
        A sorted list of the planned stop times.

    """
    feed_id = underground.metadata.ROUTE_FEED_MAP[route_id]
    feed = underground.SubwayFeed.get(feed_id, **kw)
    return sorted(feed.extract_stop_dict().get(route_id, {}).get(stop_id, list()))


def needs_update(json_file_path: str) -> bool:
    """Implement logic to determine if current data are out of date.
    
    Reads from env variables for:
    - TRAIN_DISPLAY_MAX_WAIT
    - TRAIN_DISPLAY_MIN_WAIT
    - TRAIN_DISPLAY_PEAK_HOURS

    """
    # need to check if data do not exist
    if not os.path.exists(json_file_path):
        return True

    # read json
    with open(json_file_path, "r") as file:
        data = json.load(file)

    # need to check if data are empty or expected fields are not there
    if not data or "last_check_ts" not in data or "stops_ts" not in data:
        return True

    # get datetimes
    now_dt = underground.dateutils.current_time()
    last_check_dt = underground.dateutils.epoch_to_datetime(data["last_check_ts"])
    stops_dt = sorted(
        [underground.dateutils.epoch_to_datetime(i) for i in data["stops_ts"]]
    )

    if last_check_dt > now_dt:
        raise ValueError("Last check is in the future. Something is wrong.")

    # check every TRAIN_DISPLAY_MAX_WAIT regardless of train content.
    if (now_dt - last_check_dt).total_seconds() >= int(
        os.getenv("TRAIN_DISPLAY_MAX_WAIT", 300)
    ):
        return True

    # check at most once a TRAIN_DISPLAY_MIN_WAIT.
    if (now_dt - last_check_dt).total_seconds() < int(
        os.getenv("TRAIN_DISPLAY_MIN_WAIT", 60)
    ):
        return False

    # Do not check if there are no trains scheduled. We should wait the 5 minutes in
    # this case rather than checking constantly.
    if not stops_dt:
        return False

    # update if latest stop has passed
    if stops_dt[0] <= now_dt:
        return True

    # At this point the following are true:
    #  - The data exist and have the expected fields.
    #  - It is between min and max wait seconds since the last update.
    #  - There are stops scheduled and the next one is in the future.
    #
    # Check for peak hours, do not update if not set.
    peak_hours = os.getenv("TRAIN_DISPLAY_PEAK_HOURS", None)
    if peak_hours is None:
        return False

    # update if we are in a peak hour
    if now_dt.hour in [int(i) for i in peak_hours.split(",")]:
        return True

    # otherwise do not update
    return False


def update_json_file(route_id: str, stop_id: str, json_file_path: str, **kw):
    """Update the JSON data with stop times for a route/stop."""
    # get stops and current ts
    now_ts = underground.dateutils.current_time(epoch=True)
    stops_ts = sorted(
        [
            underground.dateutils.datetime_to_epoch(i)
            for i in next_train_times(route_id, stop_id, **kw)
        ]
    )

    data = dict(last_check_ts=now_ts, stops_ts=stops_ts)

    with open(json_file_path, "w") as file:
        json.dump(data, file, indent=2)

    return data
