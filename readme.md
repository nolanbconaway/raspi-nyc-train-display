# Raspberry Pi Subway Stop Monitor

[![GitHub Actions status](https://github.com/nolanbconaway/raspi-nyc-train-display/workflows/Main%20Workflow/badge.svg)](https://github.com/nolanbconaway/raspi-nyc-train-display/actions)

This is a raspberry pi application designed to run on a [PiTFT](https://www.adafruit.com/product/2441) which displays upcoming trains to a NYC subway stop.

## Quickstart

> todo

### Raspberry Pi Setup

> todo

## Architecture

For the curious, below are some details concerning how this is all set up. I am terrible at design so this is probably garbage.

This program consists of two processes: an MTA checker, and a Display updater. These processes communicate through a SQLite database so that the display updater knows when updated arrival times are available.

### MTA Checker

The MTA realtime API is queried efficiently, only when I (Nolan) have decided new.information is needed. The rules are based on:

1. The last time the API was queried. At a minimum checking every `N` seconds, default 300, but not more than once per `M` seconds (default 60).
2. When upcoming arrivals are scheduled, checking if a known arrival has elapsed.
3. Check every `M` seconds during "peak" hours, set through an environment variable. This is useful to ensure up-to-date data during hours you usually take the train.

When an update is needed, upcoming arrivals for a specified route and stop are stored within the SQLite database
so that the display can show them.

You can run the process via command line:

``` sh
python -m traindisplay.mta.cli --help
Usage: cli.py [OPTIONS]

  Run the main CLI Program.

Options:
  -r, --route [FS|4|W|H|SI|6|Q|2|G|E|1|Z|5|M|R|L|C|F|7|GS|B|N|D|A|J]
                                  Route ID to find stops for. Can be read from
                                  $TRAIN_DISPLAY_ROUTE_ID.  [required]
  -s, --stop TEXT                 Stop ID (from stops.txt) to target. Can be
                                  read from $TRAIN_DISPLAY_STOP_ID.
                                  [required]
  -e, --echo                      Option to print out the updates to the
                                  console.
  --api-key TEXT                  MTA API key. Read from $MTA_API_KEY if not
                                  provided.
  --help                          Show this message and exit.
```

### Display Updater

The display is updated whenever new information is available from the MTA checker. It is based on Pygame, which lets me develop on my personal computer but also can work on a Raspberry Pi.

``` sh
python -m traindisplay.display.cli --help
Usage: cli.py [OPTIONS]

  Run the main CLI Program.

Options:
  -r, --route [2|E|FS|R|B|GS|D|4|C|M|5|Z|G|F|A|SI|H|L|N|W|1|6|J|7|Q]
                                  Route ID to find stops for. Can be read from
                                  $TRAIN_DISPLAY_ROUTE_ID.  [required]
  -e, --echo                      Option to print updates to the console.
  --help                          Show this message and exit.
```

On a raspberry pi, you will want this run using under `sudo -E` , otherwise the 
framebuffer interface is not accessible.

