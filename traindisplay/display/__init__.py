"""Utilities for the time displayer."""

import datetime
import typing
from pathlib import Path

import pygame

from traindisplay.display.metadata import ROUTE_COLORS

from .. import current_time

DATA_PATH = Path(__file__).parent.parent / "data"


def datetime_to_timestring(dttm: datetime.datetime) -> str:
    """Convert a datetime to a time string reading HH:MM."""
    res = dttm.strftime("%I:%M")
    return res if res[0] != "0" else res[1:]


def hex2rgb(hexstr: str) -> typing.Tuple[int]:
    """Convert a hex string into RGB colors."""
    return tuple(int(hexstr[i : i + 2], 16) for i in (0, 2, 4))


def needs_update(
    last_check_dt: datetime.datetime, last_display_dt: datetime.datetime
) -> bool:
    """Implement logic to determine if current display is out of date."""
    # Nothing to do if there is no last check
    if last_check_dt is None:
        return False

    # Display if last display is not known
    if last_display_dt is None:
        return True

    now_dt = current_time()

    # defensive programming
    if last_check_dt > now_dt:
        raise ValueError("Last check is in the future. Something is wrong.")

    if last_display_dt > now_dt:
        raise ValueError("Last display is in the future. Something is wrong.")

    # display if there is updated data since the last round
    if last_check_dt > last_display_dt:
        return True

    return False


def display_train_times(
    route_id: str,
    last_check_dt: datetime.datetime,
    stops_dt: typing.Iterable[datetime.datetime],
):
    """Make pygame widgets to show the upcoming trains."""
    # get the surface and its size
    screen = pygame.display.get_surface()
    width, height = screen.get_size()

    # get text properties
    logo_back_color = hex2rgb(ROUTE_COLORS[route_id].lstrip("#"))
    logo_text_color = (0, 0, 0) if route_id in "NQRW" else (255, 255, 255)
    stops_text_color = logo_back_color if route_id in "NQRW" else (255, 255, 255)
    text_font_path = str(DATA_PATH / "fonts" / "helvetica.ttf")
    screen.fill((0, 0, 0))

    # make strings out of stop datetimes
    if stops_dt:
        stops_dt_str = [datetime_to_timestring(i) for i in stops_dt[:3]]
    else:
        stops_dt_str = ["No", "trains", ":-("]

    # add stop times
    for num, dt in enumerate(stops_dt_str):
        text = pygame.font.SysFont(text_font_path, 90).render(
            dt, True, stops_text_color
        )

        xpos = width * 4 / 5 - text.get_width() // 2
        ypos = (
            30
            + (height - 60) / len(stops_dt_str) * num
            + (height - 60) / len(stops_dt_str) / 2
            - text.get_height() // 2
        )

        screen.blit(text, (xpos, ypos))

    # add train logo circle
    pygame.draw.circle(
        screen, logo_back_color, (int(width / 3.5), int(height / 2)), 120
    )

    # add train logo letter
    text = pygame.font.SysFont(text_font_path, 200).render(
        route_id, True, logo_text_color
    )
    screen.blit(
        text, (width / 3.5 - text.get_width() // 2, height / 2 - text.get_height() // 2)
    )

    # add last update dt
    if last_check_dt:
        last_check_str = datetime_to_timestring(last_check_dt)
        last_check_str = f"Schedule updated {last_check_str}"
    else:
        last_check_str = ""

    text = pygame.font.SysFont(text_font_path, 25).render(
        last_check_str, True, (50, 50, 50)
    )
    screen.blit(text, (width - text.get_width() - 10, height - text.get_height() - 10))

    pygame.display.flip()
