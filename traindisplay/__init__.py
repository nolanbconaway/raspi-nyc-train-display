"""Package for displaying upcoming trains."""


def current_time():
    """Get the current datetime in the NYC timezone."""
    import pytz
    import datetime

    return datetime.datetime.now(pytz.timezone("UTC")).astimezone(
        pytz.timezone("US/Eastern")
    )
