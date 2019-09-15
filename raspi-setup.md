# Setting up a raspberry pi for the display

This document will assume that you:

1. Have a modern Raspberry Pi. I use a model 3 B+ but anything 2+ should work. Maybe even earlier, I don't know.
2. Have an [Adafruit PiTFT](https://www.adafruit.com/product/2441) display to connect to it. This should be the 3.5in (320x480) model, as the display is set up to fit on that resolution.
3. Live in NYC and want the PiTFT to show train stop times at your stop :-).

I suppose I am also assuming you have some familiarity with command line tools (ssh, nano, etc).

## Before you do anything: get an API Key

To request MTA realtime data, you'll need an API key, [register here](https://datamine.mta.info/user/register).

## Step 1: Install the 2018-03-14 raspbian image to a microSD card

This is the most recent image which has been tested by Adafruit for the PiTFT.

Download [here](https://downloads.raspberrypi.org/raspbian/images/raspbian-2018-03-14/), and it install it to your pi via the [raspberrypi.org docs](https://www.raspberrypi.org/documentation/installation/installing-images/) for your OS.

Pop that card into your Pi and power up. You'll need to connect it to your network via ethernet or to a display via HDMI. Log in with the default credentials ( `pi : raspberry` ).

### If connecting via ethernet

I run everything headless so this is important for _me_. Add a blank file called `ssh` to the root directory of the image before you pop it in. That way you can SSH in without configuring anything.

## Step 2: Mandatory apt-get update and upgrade

Just do it. It'll take awhile.

``` sh
sudo apt-get update && sudo apt-get upgrade -y
```

## Step 3: Run the Adafruit PiTFT installer script

This sets up your Pi to use the PiTFT as a framebuffer interface. Per [adafruit docs](https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/easy-install-2), run:

``` sh
cd ~
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/adafruit-pitft.sh
chmod +x adafruit-pitft.sh
sudo ./adafruit-pitft.sh
```

That'll walk you through a menu in which you configure the display. I did the following:

### PiTFT Selection

``` 
Select configuration:

1. PiTFT 2.4", 2.8" or 3.2" resistive (240x320)
2. PiTFT 2.2" no touch (240x320)
3. PiTFT 2.8" capacitive touch (240x320)
4. PiTFT 3.5" resistive touch (320x480)
5. Braincraft 1.54" display (240x240)
6. Quit without installing

```

I chose 4 (3.5in resistive touch) since that's what I have. I set up the display to fit in 320x480, so it's ideally also what you have.

### Rotation

``` 
SELECT 1-6: 4
Select rotation:

1. 90 degrees (landscape)
2. 180 degrees (portait)
3. 270 degrees (landscape)
4. 0 degrees (portait)

```

I chose **3**, landscape, so that the power cable is at the top of the display.

### PiTFT as Text Console

``` 
Would you like the console to appear on the PiTFT display? [y/n]
```

`Y` . We'll use Pygame to display images on the framebuffer, so you won't need the GUI.

### Reboot

After you reboot, you should see a console appear on the PiTFT!

## Step 4: Install Python 3.6+

By default 2.7 is the only python installed on a Raspberry Pi. Maybe 3.5 is on there but that's still not good enough (this application needs 3.6+).

Here are instructions for installing 3.7.4 (basically copied from [here](https://github.com/instabot-py/instabot.py/wiki/Installing-Python-3.7-on-Raspberry-Pi)):

I ended up having to fix my apt-get by running:

``` sh
sudo apt-get update --fix-missing
```

Then I could install build tools:

``` sh
sudo apt-get install\
    build-essential \
    git \
    libbz2-dev \
    libc6-dev \
    libdb4o-cil-dev \
    libdb5.3-dev \
    libexpat1-dev \
    libffi-dev \
    libgdbm-dev \
    libgdm-dev \
    liblzma-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libpcap-dev \
    libreadline6-dev \
    libsqlite3-dev \
    libssl-dev \
    libtk8.5 \
    openssl \
    tk-dev \
    zlib1g-dev \
    -y
```

Then install python:

``` sh
cd ~
wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tar.xz
tar xf Python-3.7.4.tar.xz
cd Python-3.7.4
./configure
make -j 4
sudo make altinstall

# cleanup
cd ../
sudo rm -rf Python-3.7.4*
```

You should be able to access your new Python installation via `python3.7` and `pip3.7` commands.

## Step 5: Clone the repo and install the python requirements

You'll need to install using `sudo` , since superuser is required to access the frame buffer.

``` 
git clone https://github.com/nolanbconaway/raspi-nyc-train-display.git
cd raspi-nyc-train-display
sudo pip3.7 install .
```

## Step 6: Export your MTA API key

Now you'll need that API key you registered at the start of this tutorial. Export it as an environment variable like:

``` sh
export MTA_API_KEY="..."
```

## Step 7: Edit supervisord-rpi.conf

Edit the file with `nano` or whatever text editor you'd like.

``` sh
nano supervisord-rpi.conf
```

Below are the (current as of Sept 2019) default values set within the sections you'll want to edit.

``` ini
[program:display]
command=python -m traindisplay.display.cli -e --route Q
user=root
environment=PYGAME_HIDE_SUPPORT_PROMPT='hide',SDL_VIDEODRIVER="fbcon",SDL_FBDEV="/dev/fb1"
priority=2

[program:mta]
command=python -m traindisplay.mta.cli -e --route Q --stop D27N
priority=1
```

The following subsections will explain what you ought to change.

### Change the train route and stop ID to your needs

You can use the [underground](https://github.com/nolanbconaway/underground) command line tool (installed with this repo!) to find your stop ID like:

``` sh
$ underground findstops "bedford av"

ID: L08N    Direction: NORTH    Lat/Lon: 40.717304,-73.956872    Name: BEDFORD AV
ID: L08S    Direction: SOUTH    Lat/Lon: 40.717304,-73.956872    Name: BEDFORD AV
```

Find the stop you want to track and put that value within the `mta` section.

### Change `python` to `python3.7` 

Right now the name `python` points to python 2.7 on your raspberry pi. Change it to python3.7 in the display and mta sections.

### You should now have something like

``` ini
[program:display]
command=python3.7 -m traindisplay.display.cli -e --route <ROUTE>
user=root
environment=PYGAME_HIDE_SUPPORT_PROMPT='hide',SDL_VIDEODRIVER="fbcon",SDL_FBDEV="/dev/fb1"
priority=2

[program:mta]
command=python3.7 -m traindisplay.mta.cli -e --route <ROUTE> --stop <STOP>
priority=1
```

## Step 8: Test out the display

Now you can use supervisor to run the display and mta processes! To control the frame buffer, you'll need sudo privileges. You'll also need to add the `-E` flag so that supervisor has access to the `MTA_API_KEY` you exported. Here is the command:

``` sh
sudo -E supervisord -c supervisord-rpi.conf --nodaemon
```

Wait a minute, and you should see your PiTFT display updated with upcoming trains! In your terminal, you'll see something like:

``` 
2019-09-13 23:34:22,756 CRIT Supervisor is running as root.  Privileges were not dropped because no user is specified in the config file.  If you intend to run as root, you can set user=root in the config file to avoid this message.
2019-09-13 23:34:22,811 INFO RPC interface 'supervisor' initialized
2019-09-13 23:34:22,812 CRIT Server 'inet_http_server' running without any HTTP authentication checking
2019-09-13 23:34:22,813 INFO RPC interface 'supervisor' initialized
2019-09-13 23:34:22,814 CRIT Server 'unix_http_server' running without any HTTP authentication checking
2019-09-13 23:34:22,815 INFO supervisord started with pid 1749
2019-09-13 23:34:23,824 INFO spawned: 'mta' with pid 1752
2019-09-13 23:34:23,836 INFO spawned: 'display' with pid 1753
2019-09-13 23:34:24,841 INFO success: mta entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
2019-09-13 23:34:24,842 INFO success: display entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
```

Your display might say there are no trains at first. You can either wait a few minutes for the database to sync up or  restart supervisor.

## Step 9: Running on startup as a daemon

At this point you've configured the entire train display application and can run it using supervisor.

In the above command, we specifically configured that supervisor runs within the shell (using the `--nodaemon` flag). But we can set things up to run under the hood. This is my default approach, since I want the display to be always-on and to restart itself in the case that there is a power outage or something similar.

One way to run things at boot is through crontab. Edit your crontab like:

``` sh
crontab -e
```

Add an entry at the bottom so your crontab looks like:

``` 
# Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
#
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command

@reboot cd /home/pi/raspi-nyc-train-display && sudo -E supervisord -c supervisord-rpi.conf
```

That command runs on reboot. It moves the shell into the train display directory and runs supervisor.

### But wait! hardcode your API key in supervisord-rpi.conf first

When you reboot your pi, you'll lose all exported variables. You might notice that we didn't `export MTA_API_KEY='...'` in crontab, so the application should and will break as soon as your API key is needed.

To make sure your API key is always available, we can hardcode it in supervisord-rpi.conf. This probably isn't the best approach in terms of security but it will do for now :-).

Looking into the `supervisord` section of supervisord-rpi.conf, you can see where the API key is read from the user environment.

``` ini
[supervisord]
logfile=/tmp/supervisord.log
pidfile=/tmp/supervisord.pid
nodaemon=false
environment=MTA_API_KEY="%(ENV_MTA_API_KEY)s" ; <<<< HERE
```

Change that into this so that the application has access to the key:

``` ini
[supervisord]
logfile=/tmp/supervisord.log
pidfile=/tmp/supervisord.pid
nodaemon=false
environment=MTA_API_KEY="<YOUR KEY>"
```

### Install mailutils

If you're running things through crontab, you'll also want to install mailutils so that you can read error messages that might've been generated.

``` sh
sudo apt-get install mailutils
```

Now, if something goes wrong, you'll get a mail message within your shell.

### Reboot

Now you can test out your new train display by rebooting the raspberry pi. With any luck, it'll boot up and automatically show upcoming trains to your stop.

## Problems?

I wrote this as I set up my own raspberry pi and only validated it by running through from scratch. Your results may vary. Please let me know if you run into trouble!

