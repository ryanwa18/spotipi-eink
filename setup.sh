#!/bin/bash
if [[ $EUID -eq 0 ]]; then
  echo "This script must NOT be run as root" 1>&2
  exit 1
fi
echo "Update Packages list"
sudo apt update
echo
echo "Update to the latest"
sudo apt upgrade -y
echo
echo "Ensure system packages are installed:"
sudo apt-get install python3-pip python3-venv python3-numpy git

echo "Clone repositories:"
git clone https://github.com/ryanwa18/spotipi-eink
echo "Switching into installation directory"
cd spotipi-eink
install_path=$(pwd)
echo "Clone inky repo:"
git clone https://github.com/pimoroni/inky

echo "Add font to system:"
sudo cp ./fonts/CircularStd-Bold.otf /usr/share/fonts/opentype/CircularStd-Bold/CircularStd-Bold.otf

echo "Creating Spotipi Python environment"
python3 -m venv --system-site-packages spotipienv
echo "Activating Spotipi Python environment"
source ${install_path}/spotipienv/bin/activate
echo Install Python packages: spotipy, pillow, requests, inky impression
pip3 install -r requirements.txt --upgrade
echo "Spotipi Python environment created" 
echo

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

if [ -f "/etc/systemd/system/spotipi-eink-display.service" ]; then
    echo
    echo "Removing old spotipi-eink-display service:"
    sudo systemctl stop spotipi-eink-display
    sudo systemctl disable spotipi-eink-display
    sudo rm -rf /etc/systemd/system/spotipi-eink-display.*
    sudo systemctl daemon-reload
    echo "...done"
fi

UID_TO_USE=$(id -u)
GID_TO_USE=$(id -g)
echo
echo "Creating spotipi-eink service:"
sudo cp "${install_path}/config/spotipi.service" /etc/systemd/system/
sudo sed -i -e "/\[Service\]/a ExecStart=${install_path}/spotipienv/bin/python3  ${install_path}/python/displayCoverArt.py ${spotify_username} ${spotify_token_path}" /etc/systemd/system/spotipi.service
sudo sed -i -e "/ExecStart/a WorkingDirectory=${install_path}" /etc/systemd/system/spotipi.service
sudo sed -i -e "/EnvironmentFile/a User=${UID_TO_USE}" /etc/systemd/system/spotipi.service
sudo sed -i -e "/User/a Group=${GID_TO_USE}" /etc/systemd/system/spotipi.service
sudo mkdir /etc/systemd/system/spotipi.service.d
spotipi_env_path=/etc/systemd/system/spotipi.service.d/spotipi_env.conf
sudo touch $spotipi_env_path
echo "[Service]" | sudo tee -a $spotipi_env_path > /dev/null
echo "Environment=\"SPOTIPY_CLIENT_ID=${spotify_client_id}\"" | sudo tee -a $spotipi_env_path > /dev/null
echo "Environment=\"SPOTIPY_CLIENT_SECRET=${spotify_client_secret}\"" | sudo tee -a $spotipi_env_path > /dev/null
echo "Environment=\"SPOTIPY_REDIRECT_URI=${spotify_redirect_uri}\"" | sudo tee -a $spotipi_env_path > /dev/null
sudo systemctl daemon-reload
sudo systemctl start spotipi
sudo systemctl enable spotipi
echo "...done"

echo "SETUP IS COMPLETE"