# Spotipi E-Ink
## Overview
This project is to display information on a 4", 5.7" or 7,3" e-ink from the Spotify web api. Project [Youtube Video](https://www.youtube.com/watch?v=uQYIAYa27ds)

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
wget https://raw.githubusercontent.com/ryanwa18/spotipi-eink/main/setup.sh
chmod +x setup.sh
```

* Install the software: 
```
sudo bash setup.sh
```

## Components: 
* [Raspberry Pi Zero 2](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
* [Inky Impression 4"](https://shop.pimoroni.com/products/inky-impression-4?variant=39599238807635)
* [Inky Impression 5.7"](https://shop.pimoroni.com/products/inky-impression-5-7?variant=32298701324371)
* [Inky Impression 7.3"](https://shop.pimoroni.com/products/inky-impression-7-3?variant=40512683376723)

## Software:
* [Raspberry Pi Imager](https://www.raspberrypi.com/software/)