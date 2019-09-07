"""CLI handler for the MTA subway monitor.

``main`` provides a tool which infinitely loops, updating a JSON file when new checks
are needed.
"""

import os

import click
import pygame

import underground
from traindisplay import db, display


def check_continue_loop():
    """Handle pygame events to determine if we should be looping."""
    loop = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            loop = False
    return loop


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
    "-e", "--echo", "echo", is_flag=True, help="Option to print updates to the console."
)
def main(route_id, echo):
    """Run the main CLI Program."""
    loop = True  # for control flow later
    pygame.init()

    # hide mouse if on rpi through fbi
    if os.getenv("SDL_VIDEODRIVER") == "fbcon" and os.getenv("SDL_FBDEV") == "/dev/fb1":
        pygame.display.init()
        pygame.mouse.set_visible(False)

    # Set up the screen
    screen = pygame.display.set_mode((480, 320))

    # update once to init the display
    display.display_train_times(route_id, db.get_last_check(), db.get_next_stops())
    db.set_last_display(underground.dateutils.current_time())

    try:
        while True:

            # get up to date data
            stops_dt = db.get_next_stops()
            last_check_dt = db.get_last_check()
            last_display_dt = db.get_last_display()

            # check if update to display is needed
            update_needed = display.needs_update(last_check_dt, last_display_dt)

            # update if needed
            if update_needed:
                display.display_train_times(route_id, last_check_dt, stops_dt)
                db.set_last_display(underground.dateutils.current_time())

            # echo if needed
            if echo:
                now_str = underground.dateutils.current_time().strftime("%H:%M:%S")
                update_flag_str = (
                    "Display updated" if update_needed else "Display not updated"
                )
                click.echo(f"[{now_str}] {update_flag_str}.")

            if not check_continue_loop():
                break

            # wait ms until next iteration
            pygame.time.wait(10000)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
