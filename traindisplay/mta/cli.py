"""CLI handler for the MTA subway monitor.

``main`` provides a tool which infinitely loops, updating a JSON file when new checks
are needed.
"""

import time

import click

import underground
from traindisplay import db, mta


@click.command()
@click.option(
    "-r",
    "--route",
    "route_id",
    envvar="TRAIN_DISPLAY_ROUTE_ID",
    required=True,
    type=click.Choice(underground.metadata.VALID_ROUTES),
    help="Route ID to find stops for. Can be read from $TRAIN_DISPLAY_ROUTE_ID.",
)
@click.option(
    "-s",
    "--stop",
    "stop_id",
    envvar="TRAIN_DISPLAY_STOP_ID",
    required=True,
    type=str,
    help="Stop ID (from stops.txt) to target. Can be read from $TRAIN_DISPLAY_STOP_ID.",
)
@click.option(
    "-e",
    "--echo",
    "echo",
    is_flag=True,
    help="Option to print out the updates to the console.",
)
def main(route_id, stop_id, echo):
    """Run the main CLI Program."""
    try:
        while True:

            # wait a second if updates are not needed
            if not mta.needs_update(db.get_last_check(), db.get_next_stops()):
                time.sleep(1)
                continue

            # otherwise, get updated values
            last_check_dt = underground.dateutils.current_time()
            stops_dt = mta.next_train_times(route_id, stop_id)

            # set values
            db.set_next_stops(stops_dt)
            db.set_last_check(last_check_dt)

            # print if desired
            if echo:
                last_check_str = last_check_dt.strftime("%H:%M")
                next_stops_str = " ".join([i.strftime("%H:%M") for i in stops_dt])
                click.echo(f"[{last_check_str}] {next_stops_str}")

            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
