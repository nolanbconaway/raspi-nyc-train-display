"""Interact with the MTA API via underground."""
import datetime
import os
import typing

import underground

from .. import current_time


def next_train_times(
    route_id: str, stop_id: str, api_key: str = None
) -> typing.List[datetime.datetime]:
    """Return a list of datetimes corresponding to the next trains at a stop.
    
    Parameters
    ----------
    route_id : str
        Route ID.
    stop_id : str
        Stop ID, per stops.txt.
        
    Returns
    -------
    list[datetime.datetime]
        A sorted list of the planned stop times.

    """
    feed = underground.SubwayFeed.get(route_id, api_key=api_key)
    return sorted(feed.extract_stop_dict().get(route_id, {}).get(stop_id, list()))


def needs_update(last_check_dt: datetime.datetime, stops_dt: datetime.datetime) -> bool:
    """Implement logic to determine if current data are out of date.
    
    Reads from env variables for:
    - TRAIN_DISPLAY_MAX_WAIT
    - TRAIN_DISPLAY_MIN_WAIT
    - TRAIN_DISPLAY_PEAK_HOURS

    """
    # check if last check is not known
    if last_check_dt is None:
        return True

    now_dt = current_time()

    if last_check_dt > now_dt:
        raise ValueError("Last check is in the future. Something is wrong.")

    # check every TRAIN_DISPLAY_MAX_WAIT regardless of train content.
    if (now_dt - last_check_dt).total_seconds() >= int(
        os.getenv("TRAIN_DISPLAY_MAX_WAIT", "300")
    ):
        return True

    # check at most once a TRAIN_DISPLAY_MIN_WAIT.
    if (now_dt - last_check_dt).total_seconds() < int(
        os.getenv("TRAIN_DISPLAY_MIN_WAIT", "60")
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
