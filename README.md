# Spotipi E-Ink
![spotipi-eink Logo](/images/logo.png)</br>
Table of Content
- [Spotipi E-Ink](#spotipi-e-ink)
  - [Overview](#overview)
  - [Getting Started](#getting-started)
  - [Configuration](#configuration)
  - [Supported Hardware](#supported-hardware)
  - [Software](#software)
  - [3D printing](#3d-printing)
    - [Free cases](#free-cases)
    - [None free cases from Pimoroni](#none-free-cases-from-pimoroni)
  - [Show case](#show-case)
## Overview
This project is to display information on a 4", 5.7" or 7,3" e-ink display from the Spotify web api.</br>
Let you control via the 4 Buttons on the Pimoroni Display your Spotify playback.</br>
Project [Youtube Video](https://www.youtube.com/watch?v=uQYIAYa27ds) from [Ryan Ward ](https://github.com/ryanwa18)

Button functions:
* Button A - next track
* Button B - previous track
* Button C - play/pause
* Button D - toggle repeat order: track, context(playlist), off

I is recommendation to use Raspberry Pi Zero 2.

The display refresh time is ~30 seconds.

## Getting Started
* Create a new application within the [Spotify developer dashboard](https://developer.spotify.com/dashboard/applications)
* Edit the settings of the application within the dashboard.
    * Set the redirect uri to any local url such as http://localhost/redirect

* Enable SPI and I2C under "Interface Options" with the command:
```
sudo raspi-config
```

* Download the install script
```
wget https://raw.githubusercontent.com/Gabbajoe/spotipi-eink/main/setup.sh
chmod +x setup.sh
```

* Install the software: 
```
bash setup.sh
```

After the spotipi-eink is installed you have 2 systemd services:
* spotipi-eink-display.service
* spotipi-eink-buttons.service (only for Pimoroni displays)

This services run as the user with that you executed the setup.sh.

You control the services via systemctl **start, stop, status** *(services-name)*. Example get the status of *spotipi-eink-display.service*:
```
spotipi@spotipi:~ $ sudo systemctl status spotipi-eink-display.service
● spotipi-eink-display.service - Spotipi eInk Display service
     Loaded: loaded (/etc/systemd/system/spotipi-eink-display.service; enabled; preset: enabled)
    Drop-In: /etc/systemd/system/spotipi-eink-display.service.d
             └─spotipi-eink-display_env.conf
     Active: active (running) since Tue 2023-10-31 09:30:05 CET; 27min ago
   Main PID: 4108 (python3)
      Tasks: 1 (limit: 383)
        CPU: 5min 13.455s
     CGroup: /system.slice/spotipi-eink-display.service
             └─4108 /home/spotipi/spotipi-eink/spotipienv/bin/python3 /home/spotipi/spotipi-eink/python/spotipiEinkDisplay.py

Oct 31 09:30:05 spotipi systemd[1]: Started spotipi-eink-display.service - Spotipi eInk Display service.
Oct 31 09:30:06 spotipi spotipi-eink-display[4108]: Spotipi eInk Display - Service instance created
Oct 31 09:30:07 spotipi spotipi-eink-display[4108]: Spotipi eInk Display - Loading Pimoroni inky lib
Oct 31 09:30:07 spotipi spotipi-eink-display[4108]: Spotipi eInk Display - Service started
```

With the latest Raspberry PI OS **Bookworm** you have no more */var/log/syslog* you have to use *journalctl*. To view the *spotipi-eink-display.service* and *spotipi-eink-buttons.service* logs use the following command:

```
# see all time logs
journalctl -u spotipi-eink-display.service -u spotipi-eink-buttons.service
```
or
```
# see only today logs
journalctl -u spotipi-eink-display.service -u spotipi-eink-buttons.service --since today
```

Spotipi-eink creates its own Python environment because since Raspberry PI OS **Bookworm** the system Python environment is protect See:
* [Python on Raspberry Pi](https://www.raspberrypi.com/documentation/computers/os.html#python-on-raspberry-pi)
* [PEP668](https://peps.python.org/pep-0668/)

If you like to manual execute the Python script you have to load into the Virtual Python environment like the following commands shows. You will see then in front of you terminal a **(spotipienv)**:
```
cd ~
. spotipi/spotipi-eink/spotipienv/bin/activate
```
Additional you need to export the following 3 environment variable on you shell that the spotipy library is working.
```
export SPOTIPY_CLIENT_ID=''
export SPOTIPY_CLIENT_SECRET=''
export SPOTIPY_REDIRECT_URI=''
```
If you like to leave the Virtual Python environment just type: **deactivate**


## Configuration
In the file **spotipi/config/eink_options.ini** you can modify:
* the displayed *title* and *artist* text size
* the direction of how the title or artist text line break will be done, **top-down** or **bottom-up**
* the offset from display borders
* disable the small album cover
* the size of the small album cover
* the font that will be used

Example config:

```
[DEFAULT]
width = 640
height = 400
album_cover_small_px = 200
; possible values are inky or waveshare4
model = inky
; disable smaller album cover set to False
; if disabled top offset is still calculated like as the following:
; offset_px_top + album_cover_small_px
album_cover_small = True
; cleans the display every 20 picture
; this takes ~60 seconds
display_refresh_counter = 20
username = theRockJohnson
token_file = /home/spotipi/spotipi-eink/config/.cache
spotipy_log = /home/spotipi/spotipi-eink/log/spotipy.log
no_song_cover = /home/spotipi/spotipi-eink/resources/default.jpg
font_path = /home/spotipi/spotipi-eink/resources/CircularStd-Bold.otf
font_size_title = 45
font_size_artist = 35
offset_px_left = 20
offset_px_right = 20
offset_px_top = 0
offset_px_bottom = 20
offset_text_px_shadow = 4
; text_direction possible values: top-down or bottom-up
text_direction = bottom-up
; possible modes are fit or repeat
background_mode = fit
```

## Supported Hardware
* [Raspberry Pi Zero 2](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
* [Pimoroni Inky Impression 4"](https://shop.pimoroni.com/products/inky-impression-4?variant=39599238807635)
* [Waveshare 4.01inch ACeP 7-Color E-Paper E-Ink Display HAT](https://www.waveshare.com/product/displays/e-paper/epaper-2/4.01inch-e-paper-hat-f.htm)
* [Pimoroni Inky Impression 5.7"](https://shop.pimoroni.com/products/inky-impression-5-7?variant=32298701324371)
* [Pimoroni Inky Impression 7.3"](https://shop.pimoroni.com/products/inky-impression-7-3?variant=40512683376723)


## Software
* [Raspberry Pi Imager](https://www.raspberrypi.com/software/)

## 3D printing
### Free cases
* [SpotiPi E-Ink - Inky Impression 5.7" Case](https://cults3d.com/en/3d-model/gadget/spotipi-e-ink-inky-impression-5-7-case)
* [Pimoroni Inky Impression Case - 5.7" I guess](https://www.printables.com/de/model/51765-pimoroni-inky-impression-case/files)
* [Inky Impression 5.7" Frame](https://www.printables.com/de/model/603008-inky-impression-57-frame)
* [Inky Impression 7.3 e-Paper frame/case](https://www.printables.com/de/model/585713-inky-impression-73-e-paper-framecase)
* [Pimoroni 7 color EInk display Frame](https://www.thingiverse.com/thing:4666925)
### None free cases from Pimoroni
* [Desktop Case for pimoroni Inky Impression 4" (7 colour ePaper/eInk HAT) and Raspberry Pi Zero/3 A+](https://cults3d.com/en/3d-model/gadget/desktop-case-for-pimoroni-inky-impression-4-7-colour-epaper-eink-hat-and-raspberry-pi-zero-3-a)
* [Picture frame for pimoroni Inky Impression 5.7" (ePaper/eInk/EPD) and raspberry pi zero](https://cults3d.com/en/3d-model/gadget/picture-frame-for-pimoroni-inky-impression-epaper-eink-epd-and-raspberry-pi-zero)
* [Enclosure for pimoroni Inky Impression (ePaper/eInk/EPD) and raspberry pi zero](https://cults3d.com/en/3d-model/gadget/enclosure-for-pimoroni-inky-impression-epaper-eink-epd-and-raspberry-pi-zero)

## Show case
Example picture of my 4" display in the Pimoroni Desktop case:
![spotipi-eink Logo](/images/example.jpg)
![spotipi-eink Logo](/images/no_song.jpg)
