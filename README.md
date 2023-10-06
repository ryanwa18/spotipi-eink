# Spotipi E-Ink
## Overview
This project is to display information on a 5.7" e-ink from the Spotify web api.
[Youtube Video](https://www.youtube.com/watch?v=uQYIAYa27ds)

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
* [Inky Impression 5.7"](https://shop.pimoroni.com/products/inky-impression-5-7?variant=32298701324371)

## Software:
* [Raspberry Pi Imager](https://www.raspberrypi.com/software/)