"""CLI handler for the MTA subway monitor.

``main`` provides a tool which infinitely loops, updating a JSON file when new checks
are needed.
"""

import os
import time

import click
import pygame

import underground
from traindisplay import db, display


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
    "-e",
    "--echo",
    "echo",
    is_flag=True,
    help="Option to print out the updates to the console.",
)
def main(route_id, echo):
    """Run the main CLI Program."""
    loop = True  # for control flow later
    pygame.init()

    # hide mouse if on rpi through fbi
    if os.getenv("SDL_VIDEODRIVER") == "fbcon":
        pygame.mouse.set_visible(False)

    # Set up the screen
    screen = pygame.display.set_mode((480, 320))

    # update once to init the display
    display.display_train_times(route_id, db.get_last_check(), db.get_next_stops())
    db.set_last_display(underground.dateutils.current_time())

    try:
        while loop:

            # get up to date data
            stops_dt = db.get_next_stops()[:3]
            last_check_dt = db.get_last_check()
            last_display_dt = db.get_last_display()

            # update if needed
            if display.needs_update(last_check_dt, last_display_dt):
                display.display_train_times(route_id, last_check_dt, stops_dt)

            # control flow
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    loop = False

            # set last update in database
            db.set_last_display(underground.dateutils.current_time())

            pygame.display.flip()

            if echo:
                last_display_str = last_display_dt.strftime("%H:%M:%S")
                update_flag_str = (
                    "updated"
                    if display.needs_update(last_check_dt, last_display_dt)
                    else "not updated"
                )
                click.echo(f"[{last_display_str}] {update_flag_str}.")

            time.sleep(10)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
