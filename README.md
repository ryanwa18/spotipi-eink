# Spotipi E-Ink
## Overview
This project is to display information on a 4", 5.7" or 7,3" e-ink from the Spotify web api. Project [Youtube Video](https://www.youtube.com/watch?v=uQYIAYa27ds)</br>
Buttton functions:
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

## Components: 
* [Raspberry Pi Zero 2](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
* [Inky Impression 4"](https://shop.pimoroni.com/products/inky-impression-4?variant=39599238807635)
* [Inky Impression 5.7"](https://shop.pimoroni.com/products/inky-impression-5-7?variant=32298701324371)
* [Inky Impression 7.3"](https://shop.pimoroni.com/products/inky-impression-7-3?variant=40512683376723)

## Software:
* [Raspberry Pi Imager](https://www.raspberrypi.com/software/)

## 3D printing:
* [4" Case - none free](https://cults3d.com/en/3d-model/gadget/desktop-case-for-pimoroni-inky-impression-4-7-colour-epaper-eink-hat-and-raspberry-pi-zero-3-a)
* [5.7" Case - free](https://cults3d.com/en/3d-model/gadget/spotipi-e-ink-inky-impression-5-7-case)
* [5.7" Case - none free](https://cults3d.com/en/3d-model/gadget/picture-frame-for-pimoroni-inky-impression-epaper-eink-epd-and-raspberry-pi-zero)
* [5.7" Case - none free](https://cults3d.com/en/3d-model/gadget/enclosure-for-pimoroni-inky-impression-epaper-eink-epd-and-raspberry-pi-zero)