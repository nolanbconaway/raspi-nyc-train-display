"""CLI handler for the MTA subway monitor.

``main`` provides a tool which infinitely loops, updating a JSON file when new checks
are needed.
"""

import json
import time

import click

import traindisplay.mta as mta
from underground.metadata import VALID_ROUTES

# next_train_times
# needs_update
# update_json_file


@click.command()
@click.option(
    "-r",
    "--route",
    "route_id",
    envvar="TRAIN_DISPLAY_ROUTE_ID",
    required=True,
    type=click.Choice(VALID_ROUTES),
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
    "-f",
    "--file",
    "json_file_path",
    envvar="TRAIN_DISPLAY_JSON_FILE",
    type=click.Path(writable=True),
    required=True,
    help="File to store update data within. This is temp file and can be destroyed "
    "at any time. Can be read from $TRAIN_DISPLAY_JSON_FILE.",
)
@click.option(
    "-e",
    "--echo",
    "echo",
    is_flag=True,
    help="Option to print out the updates to the console.",
)
def main(route_id, stop_id, json_file_path, echo):
    """Run the main CLI Program."""
    try:
        while True:

            # wait a second if updates are not needed
            if not mta.needs_update(json_file_path):
                time.sleep(1)
                continue

            # otherwise update the file and optionally print the data
            data = mta.update_json_file(route_id, stop_id, json_file_path)
            if echo:
                click.echo(json.dumps(data))

    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
