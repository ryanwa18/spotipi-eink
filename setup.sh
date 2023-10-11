#!/bin/bash
if [[ $EUID -eq 0 ]]; then
  echo "This script must NOT be run as root" 1>&2
  exit 1
fi
echo "Update Packages list"
sudo apt update
echo
echo "Update to the latest"
sudo apt -y upgrade
echo
echo "Ensure system packages are installed:"
sudo apt-get install python3-pip python3-venv python3-numpy git firefox-esr
echo
if [ -d "spotipi-eink" ]; then
    echo "Old installation found deleting it"
    sudo rm -rf spotipi-eink
fi
echo
echo "Clone spotipy-eink git"
git clone https://github.com/Gabbajoe/spotipi-eink
echo "Switching into instalation directory"
cd spotipi-eink
install_path=$(pwd)
if ! [ -f "/usr/share/fonts/opentype/CircularStd-Bold/CircularStd-Bold.otf" ]; then
    echo "Add font CircularStd-Bold to system"
    if ! [ -d "/usr/share/fonts/opentype/CircularStd-Bold" ]; then
        sudo mkdir -p "/usr/share/fonts/opentype/CircularStd-Bold"
    fi
    sudo cp "${install_path}/setup/font/CircularStd-Bold.otf" /usr/share/fonts/opentype/CircularStd-Bold/CircularStd-Bold.otf
else
    echo "Font CircularStd-Bold already installed"
fi
echo
echo "##### Creating Spotipi Python environment"
python3 -m venv --system-site-packages spotipienv
echo "Activating Spotipi Python environment"
source ${install_path}/spotipienv/bin/activate
echo Install Python packages: spotipy, pillow, inky impression
pip3 install -r requirements.txt
echo "##### Spotipi Python environment created" 
echo
echo "###### Generate Spotify Token"
if ! [ -d "${install_path}/config" ]; then
    echo "creating  ${install_path}/config path"
    mkdir -p "${install_path}/config"
fi
cd ${install_path}/config
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

python3 ${install_path}/python/generateToken.py $spotify_username

if [ -f "${install_path}/config/.cache" ]; then
    spotify_token_path="${install_path}/config/.cache"
    echo "Use $spotify_token_path"
else
    echo "Unable to find ${install_path}/.cache"
    echo "Please enter the full path to your spotify token file (including /.cache):"
    read spotify_token_path
fi
echo "###### Spotify Token Created"
cd ${install_path}
echo
if ! [ -d "${install_path}/client" ]; then
    echo "creating ${install_path}/client path"
    mkdir -p "${install_path}/client"
fi
echo
echo "###### Display setup"
PS3="Please select your Inky Impression Model: "
options=("Inky Impression 4 (640x400)" "Inky Impression 5.7 (600x488)" "Inky Impression 7.3 (800x480)")
select opt in "${options[@]}"
do
    case $opt in
        "Inky Impression 4 (640x400)")
            cp ${install_path}/setup/html_template/spotipi-eink1.html ${install_path}/client/spotipi-eink.html
            cp ${install_path}/setup/config_template/eink_options1.ini ${install_path}/config/eink_options.ini
            break
            ;;
        "Inky Impression 5.7 (600x488)")
            cp ${install_path}/setup/html_template/spotipi-eink2.html ${install_path}/client/spotipi-eink.html
            cp ${install_path}/setup/config_template/eink_options2.ini ${install_path}/config/eink_options.ini
            break
            ;;
        "Inky Impression 7.3 (800x480)")
            cp ${install_path}/python/client/static/spotipi-eink3.html ${install_path}/client/spotipi-eink.html
            cp ${install_path}/setup/config_template/eink_options3.ini ${install_path}/config/eink_options.ini
            break
            ;;
        *)
            echo "invalid option $REPLY"
            ;;
    esac
done
echo
echo "###### Creating default config entries and files"
echo "display_refresh_counter = 20" >> ${install_path}/config/eink_options.ini
echo "username = ${spotify_username}" >> ${install_path}/config/eink_options.ini
echo "token_file = ${spotify_token_path}" >> ${install_path}/config/eink_options.ini
echo "screenshot_filename = screenshot.png" >> ${install_path}/config/eink_options.ini
echo "spotipy_log = ${install_path}/log/spotipy.log" >> ${install_path}/config/eink_options.ini
echo "album_cover_path = ${install_path}/client/album_cover.jpg" >> ${install_path}/config/eink_options.ini
echo "html_file_path = ${install_path}/client/spotipi-eink.html" >> ${install_path}/config/eink_options.ini
echo "no_song_cover = ${install_path}/client/default.jpg" >> ${install_path}/config/eink_options.ini
cp "${install_path}/setup/html_template/default.jpg" "${install_path}/client/album_cover.jpg"
cp "${install_path}/setup/html_template/default.jpg" "${install_path}/client/default.jpg"
cp "${install_path}/setup/font/CircularStd-Bold.otf" "${install_path}/client/CircularStd-Bold.otf"
if ! [ -d "${install_path}/log" ]; then
    echo "creating ${install_path}/log"
    mkdir "${install_path}/log"
fi
echo
echo "###### Spotipi-eink display update service installation"
echo
if [ -f "/etc/systemd/system/spotipi-eink.service" ]; then
    echo
    echo "Removing old spotipi-eink service:"
    sudo systemctl stop spotipi-eink
    sudo systemctl disable spotipi-eink
    sudo rm -rf /etc/systemd/system/spotipi-eink.*
    sudo systemctl daemon-reload
    echo "...done"
fi
UID_TO_USE=$(id -u)
GID_TO_USE=$(id -g)
echo
echo "Creating spotipi-eink service:"
sudo cp "${install_path}/setup/service_template/spotipi-eink.service" /etc/systemd/system/
sudo sed -i -e "/\[Service\]/a ExecStart=${install_path}/spotipienv/bin/python3 ${install_path}/python/displayCoverArt.py" /etc/systemd/system/spotipi-eink.service
sudo sed -i -e "/ExecStart/a WorkingDirectory=${install_path}" /etc/systemd/system/spotipi-eink.service
sudo sed -i -e "/EnvironmentFile/a User=${UID_TO_USE}" /etc/systemd/system/spotipi-eink.service
sudo sed -i -e "/User/a Group=${GID_TO_USE}" /etc/systemd/system/spotipi-eink.service
sudo mkdir /etc/systemd/system/spotipi-eink.service.d
spotipi_env_path=/etc/systemd/system/spotipi-eink.service.d/spotipi-eink_env.conf
sudo touch $spotipi_env_path
echo "[Service]" | sudo tee -a $spotipi_env_path > /dev/null
echo "Environment=\"SPOTIPY_CLIENT_ID=${spotify_client_id}\"" | sudo tee -a $spotipi_env_path > /dev/null
echo "Environment=\"SPOTIPY_CLIENT_SECRET=${spotify_client_secret}\"" | sudo tee -a $spotipi_env_path > /dev/null
echo "Environment=\"SPOTIPY_REDIRECT_URI=${spotify_redirect_uri}\"" | sudo tee -a $spotipi_env_path > /dev/null
sudo systemctl daemon-reload
sudo systemctl start spotipi-eink
sudo systemctl enable spotipi-eink
echo "...done"
echo
echo "###### Spotipi-eink button action service installation"
echo
if [ -f "/etc/systemd/system/spotipi-eink-buttons.service" ]; then
    echo
    echo "Removing old spotipi-eink-buttons service:"
    sudo systemctl stop spotipi-eink-buttons
    sudo systemctl disable spotipi-eink-buttons
    sudo rm -rf /etc/systemd/system/spotipi-eink-buttons.*
    sudo systemctl daemon-reload
    echo "...done"
fi
echo
echo "Creating spotipi-eink-buttons service:"
sudo cp "${install_path}/setup/service_template/spotipi-eink-buttons.service" /etc/systemd/system/
sudo sed -i -e "/\[Service\]/a ExecStart=${install_path}/spotipienv/bin/python3 ${install_path}/python/buttonActions.py" /etc/systemd/system/spotipi-eink-buttons.service
sudo sed -i -e "/ExecStart/a WorkingDirectory=${install_path}" /etc/systemd/system/spotipi-eink.service
sudo sed -i -e "/EnvironmentFile/a User=${UID_TO_USE}" /etc/systemd/system/spotipi-eink-buttons.service
sudo sed -i -e "/User/a Group=${GID_TO_USE}" /etc/systemd/system/spotipi-eink-buttons.service
sudo mkdir /etc/systemd/system/spotipi-eink-buttons.service.d
spotipi_buttons_env_path=/etc/systemd/system/spotipi-eink-buttons.service.d/spotipi-eink-buttons_env.conf
sudo touch $spotipi_buttons_env_path
echo "[Service]" | sudo tee -a $spotipi_buttons_env_path > /dev/null
echo "Environment=\"SPOTIPY_CLIENT_ID=${spotify_client_id}\"" | sudo tee -a $spotipi_buttons_env_path > /dev/null
echo "Environment=\"SPOTIPY_CLIENT_SECRET=${spotify_client_secret}\"" | sudo tee -a $spotipi_buttons_env_path > /dev/null
echo "Environment=\"SPOTIPY_REDIRECT_URI=${spotify_redirect_uri}\"" | sudo tee -a $spotipi_buttons_env_path > /dev/null
sudo systemctl daemon-reload
sudo systemctl start spotipi-eink-buttons
sudo systemctl enable spotipi-eink-buttons
echo "...done"
echo
echo "SETUP IS COMPLETE"
