"""Test package."""


def epoch_to_datetime(epoch):
    """Convert epoch time into a datetime in NYC timezone."""
    import datetime
    import pytz

    return (
        pytz.timezone("UTC")
        .localize(datetime.datetime.utcfromtimestamp(epoch))
        .astimezone(pytz.timezone("US/Eastern"))
    )
