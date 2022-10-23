# Spotipi E-Ink
### Overview
This project is to display information on a 5.7" e-ink from the Spotify web api.
### Getting Started
* Create a new application within the [Spotify developer dashboard](https://developer.spotify.com/dashboard/applications) <br />
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

* Install the software: <br />
```
sudo bash setup.sh
```
