#!/bin/bash
echo "Update Packages list"
sudo apt update
echo "Update to the latest"
sudo apt -y upgrade
echo "Ensure packages are installed:"
sudo apt-get install python3-pip python3-numpy git firefox-esr

if [ -d "spotipi-eink" ]; then
    echo "Old installation found deleting it"
    sudo rm -rf spotipi-eink
echo
echo "Clone spotipy-eink git"
git clone https://github.com/Gabbajoe/spotipi-eink
cd spotipi-eink
echo "Init git submodules"
git submodule init

echo "Add font to system:"
sudo cp .python/client/static/CircularStd-Bold.otf /usr/share/fonts/opentype/CircularStd-Bold/CircularStd-Bold.otf

echo "Installing spotipy library:"
pip3 install spotipy --upgrade

echo "Installing beautifulsoup4 library:"
pip3 install beautifulsoup4 --upgrade

echo "Installing pillow library:"
pip3 install pillow --upgrade

echo "Installing inky impression libraries:"
pip3 install inky[rpi,example-depends]

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

python3 python/generateToken.py $spotify_username

echo
echo "###### Spotify Token Created ######"

install_path=$(pwd)

if [ -f "${install_path}/.cache" ]; then
    spotify_token_path="${install_path}/.cache"
    echo "Use $spotify_token_path"
else
    echo "Unable to finde ${install_path}/.cache"
    echo "Please enter the full path to your spotify token file (including /.cache):"
    read spotify_token_path
fi

echo
echo "Display setup"
PS3="Please select your Inky Impression Model: "
options=("Inky Impression 4 (640x400)" "Inky Impression 5.7 (600x488)" "Inky Impression 7.3 (800x480)")
select opt in "${options[@]}"
do
    case $opt in
        "Inky Impression 4 (640x400)")
            cp ./python/client/static/spotipi-eink1.html ./python/client/spotipi-eink.html
            cp ./python/client/static/default.jpg ./python/client/album_cover.jpg
            echo -e "[DEFAULT]\nwidth = 640\nheight = 400" > ./config/eink_options.ini
            break
            ;;
        "Inky Impression 5.7 (600x488)")
            cp ./python/client/static/spotipi-eink2.html ./python/client/spotipi-eink.html
            cp ./python/client/static/default.jpg ./python/client/album_cover.jpg
            echo -e "[DEFAULT]\nwidth = 600\nheight = 488" > ./config/eink_options.ini
            break
            ;;
        "Inky Impression 7.3 (800x480")
            cp ./python/client/static/spotipi-eink3.html ./python/client/spotipi-eink.html
            cp ./python/client/static/default.jpg ./python/client/album_cover.jpg
            echo -e "[DEFAULT]\nwidth = 800\nheight = 480" > ./config/eink_options.ini
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done

if [ -f "/etc/systemd/system/spotipi-eink.service" ]; then
    echo
    echo "Removing spotipi-eink service:"
    sudo systemctl stop spotipi-eink
    sudo rm -rf /etc/systemd/system/spotipi-eink.*
    sudo systemctl daemon-reload
    echo "...done"
fi
echo
echo "Creating spotipi-eink service:"
sudo cp ./config/spotipi-eink.service /etc/systemd/system/
sudo sed -i -e "/\[Service\]/a ExecStart=python3 ${install_path}/python/displayCoverArt.py ${spotify_username} ${spotify_token_path}" /etc/systemd/system/spotipi-eink.service
sudo mkdir /etc/systemd/system/spotipi-eink.service.d
spotipi_env_path=/etc/systemd/system/spotipi-eink.service.d/spotipi-eink_env.conf
sudo touch $spotipi_env_path
echo "[Service]" | sudo tee -a $spotipi_env_path
echo "Environment=\"SPOTIPY_CLIENT_ID=${spotify_client_id}\"" | sudo tee -a $spotipi_env_path
echo "Environment=\"SPOTIPY_CLIENT_SECRET=${spotify_client_secret}\"" | sudo tee -a $spotipi_env_path
echo "Environment=\"SPOTIPY_REDIRECT_URI=${spotify_redirect_uri}\"" | sudo tee -a $spotipi_env_path
sudo systemctl daemon-reload
sudo systemctl start spotipi-eink
sudo systemctl enable spotipi-eink
echo "...done"
echo

read -p "Do you want to install the buttons action service? (y/Y) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "/etc/systemd/system/spotipi-eink-buttons.service" ]; then
        echo
        echo "Removing spotipi-eink-buttons service:"
        sudo systemctl stop spotipi-eink-buttons
        sudo rm -rf /etc/systemd/system/spotipi-eink-buttons.*
        sudo systemctl daemon-reload
        echo "...done"
    fi
    echo
    echo "Creating spotipi-eink-buttons service:"
    sudo cp ./config/spotipi-eink-buttons.service /etc/systemd/system/
    sudo sed -i -e "/\[Service\]/a ExecStart=python3 ${install_path}/python/buttonActions.py ${spotify_username} ${spotify_token_path}" /etc/systemd/system/spotipi-eink-buttons.service
    sudo mkdir /etc/systemd/system/spotipi-eink-buttons.service.d
    spotipi_buttons_env_path=/etc/systemd/system/spotipi-eink-buttons.service.d/spotipi-eink-buttons_env.conf
    sudo touch $spotipi_buttons_env_path
    echo "[Service]" | sudo tee -a $spotipi_buttons_env_path
    echo "Environment=\"SPOTIPY_CLIENT_ID=${spotify_client_id}\"" | sudo tee -a $spotipi_buttons_env_path
    echo "Environment=\"SPOTIPY_CLIENT_SECRET=${spotify_client_secret}\"" | sudo tee -a $spotipi_buttons_env_path
    echo "Environment=\"SPOTIPY_REDIRECT_URI=${spotify_redirect_uri}\"" | sudo tee -a $spotipi_buttons_env_path
    sudo systemctl daemon-reload
    sudo systemctl start spotipi-eink-buttons
    sudo systemctl enable spotipi-eink-buttons
    echo "...done"
fi
echo
echo "SETUP IS COMPLETE"
