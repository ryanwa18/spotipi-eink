# Spotipi E-Ink
![spotipi-eink Logo](/images/logo.png)
## Overview
This project is to display information on a 4", 5.7" or 7,3" e-ink from the Spotify web api.</br>
Let you control via the 4 Buttons you Spotify player.</br>
Project [Youtube Video](https://www.youtube.com/watch?v=uQYIAYa27ds) from [Ryan Ward ](https://github.com/ryanwa18)

Button functions:
* Button A - next track
* Button B - previos track
* Button C - play/pause
* Button D - toggel repeate order: track, context, off

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
; disable smaller album cover set to False
; if disabled top offset is still calculated like as the following:
; offset_px_top + album_cover_small_px
album_cover_small = True
; cleans the display every 20 picture
; this takes ~60 seconds
display_refresh_counter = 20
username = theRockJohnsons
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
```

## Components: 
* [Raspberry Pi Zero 2](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
* [Inky Impression 4"](https://shop.pimoroni.com/products/inky-impression-4?variant=39599238807635)
* [Inky Impression 5.7"](https://shop.pimoroni.com/products/inky-impression-5-7?variant=32298701324371)
* [Inky Impression 7.3"](https://shop.pimoroni.com/products/inky-impression-7-3?variant=40512683376723)

## Software:
* [Raspberry Pi Imager](https://www.raspberrypi.com/software/)

## 3D printing:
### Free cases:
* [SpotiPi E-Ink - Inky Impression 5.7" Case](https://cults3d.com/en/3d-model/gadget/spotipi-e-ink-inky-impression-5-7-case)
* [Pimoroni Inky Impression Case - 5.7" I guess](https://www.printables.com/de/model/51765-pimoroni-inky-impression-case/files)
* [Inky Impression 5.7" Frame](https://www.printables.com/de/model/603008-inky-impression-57-frame)
* [Inky Impression 7.3 e-Paper frame/case](https://www.printables.com/de/model/585713-inky-impression-73-e-paper-framecase)
* [Pimoroni 7 color EInk display Frame](https://www.thingiverse.com/thing:4666925)
### None free cases from Pimoroni:
* [Desktop Case for pimoroni Inky Impression 4" (7 colour ePaper/eInk HAT) and Raspberry Pi Zero/3 A+](https://cults3d.com/en/3d-model/gadget/desktop-case-for-pimoroni-inky-impression-4-7-colour-epaper-eink-hat-and-raspberry-pi-zero-3-a)
* [Picture frame for pimoroni Inky Impression 5.7" (ePaper/eInk/EPD) and raspberry pi zero](https://cults3d.com/en/3d-model/gadget/picture-frame-for-pimoroni-inky-impression-epaper-eink-epd-and-raspberry-pi-zero)
* [Enclosure for pimoroni Inky Impression (ePaper/eInk/EPD) and raspberry pi zero](https://cults3d.com/en/3d-model/gadget/enclosure-for-pimoroni-inky-impression-epaper-eink-epd-and-raspberry-pi-zero)

## Show case
Example picutre of my 4" display in the Pimoroni Desktop case:
![spotipi-eink Logo](/images/example.jpg)
![spotipi-eink Logo](/images/no_song.jpg)
