#!/bin/bash
echo "Ensure packages are installed:"
sudo apt-get install python3-numpy git firefox-esr

echo "Clone repositories:"
git clone https://github.com/ryanwa18/spotipi-eink
cd spotipi-eink
git clone https://github.com/pimoroni/inky

echo "Add font to system:"
sudo cp ./fonts/CircularStd-Bold.otf /usr/share/fonts/opentype/CircularStd-Bold/CircularStd-Bold.otf

echo "Installing spotipy library:"
pip install spotipy --upgrade

echo "Installing pillow library:"
pip install pillow --upgrade

echo "Installing inky impression libraries:"
pip3 install inky[rpi,example-depends]

echo "Remove numpy:"
pip3 uninstall numpy

echo "Enter your Spotify Client ID:"
read spotify_client_id
export SPOTIPY_CLIENT_ID=$spotify_client_id

echo "Enter your Spotify Client Secret:"
read spotify_client_secret
export SPOTIPY_CLIENT_SECRET=$spotify_client_secret

echo "Enter your Spotify Redirect URI:"
read spotify_redirect_uri
export SPOTIPY_REDIRECT_URI=$spotify_redirect_uri

echo "Enter your spotify username:"
read spotify_username

python python/generateToken.py $spotify_username

echo
echo "###### Spotify Token Created ######"
echo "Filename: .cache"

echo "Enter the full path to your spotify token:"
read spotify_token_path

install_path=$(pwd)

echo "Removing spotipi service if it exists:"
sudo systemctl stop spotipi
sudo rm -rf /etc/systemd/system/spotipi.*
sudo systemctl daemon-reload
echo "...done"

echo "Creating spotipi service:"
sudo cp ./config/spotipi.service /etc/systemd/system/
sudo sed -i -e "/\[Service\]/a ExecStart=python ${install_path}/python/displayCoverArt.py ${spotify_username} ${spotify_token_path}" /etc/systemd/system/spotipi.service
sudo mkdir /etc/systemd/system/spotipi.service.d
spotipi_env_path=/etc/systemd/system/spotipi.service.d/spotipi_env.conf
sudo touch $spotipi_env_path
sudo echo "[Service]" >> $spotipi_env_path
sudo echo "Environment=\"SPOTIPY_CLIENT_ID=${spotify_client_id}\"" >> $spotipi_env_path
sudo echo "Environment=\"SPOTIPY_CLIENT_SECRET=${spotify_client_secret}\"" >> $spotipi_env_path
sudo echo "Environment=\"SPOTIPY_REDIRECT_URI=${spotify_redirect_uri}\"" >> $spotipi_env_path
sudo systemctl daemon-reload
sudo systemctl start spotipi
sudo systemctl enable spotipi
echo "...done"

echo "SETUP IS COMPLETE"
