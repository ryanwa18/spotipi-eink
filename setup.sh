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
sudo apt-get install python3-pip python3-venv python3-numpy git libopenjp2-7
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
if ! [ -d "${install_path}/resources" ]; then
    echo "creating ${install_path}/resources path"
    mkdir -p "${install_path}/resources"
fi
echo
echo "###### Display setup"
PS3="Please select your Inky Impression Model: "
options=("Inky Impression 4 (640x400)" "Inky Impression 5.7 (600x448)" "Inky Impression 7.3 (800x480)")
select opt in "${options[@]}"
do
    case $opt in
        "Inky Impression 4 (640x400)")
            cp ${install_path}/setup/config_template/eink_options1.ini ${install_path}/config/eink_options.ini
            echo "[DEFAULT]" >> ${install_path}/config/eink_options.ini
            echo "width = 640" >> ${install_path}/config/eink_options.ini
            echo "height = 400" >> ${install_path}/config/eink_options.ini
            echo "album_cover_small_px = 200" >> ${install_path}/config/eink_options.ini
            break
            ;;
        "Inky Impression 5.7 (600x448)")
            cp ${install_path}/setup/config_template/eink_options2.ini ${install_path}/config/eink_options.ini
            echo "[DEFAULT]" >> ${install_path}/config/eink_options.ini
            echo "width = 600" >> ${install_path}/config/eink_options.ini
            echo "height = 448" >> ${install_path}/config/eink_options.ini
            echo "album_cover_small_px = 250" >> ${install_path}/config/eink_options.ini
            break
            ;;
        "Inky Impression 7.3 (800x480)")
            cp ${install_path}/setup/config_template/eink_options3.ini ${install_path}/config/eink_options.ini
            echo "[DEFAULT]" >> ${install_path}/config/eink_options.ini
            echo "width = 800" >> ${install_path}/config/eink_options.ini
            echo "height = 480" >> ${install_path}/config/eink_options.ini
            echo "album_cover_small_px = 300" >> ${install_path}/config/eink_options.ini
            break
            ;;
        *)
            echo "invalid option $REPLY"
            ;;
    esac
done
echo
echo "###### Creating default config entries and files"
echo "; disable smaller album cover set to False" >> ${install_path}/config/eink_options.ini
echo "; if disabled top offset is still calculated like as the following:" >> ${install_path}/config/eink_options.ini
echo "; offset_px_top + album_cover_small_px" >> ${install_path}/config/eink_options.ini
echo "album_cover_small = True" >> ${install_path}/config/eink_options.ini
echo "; cleans the display every 20 picture" >> ${install_path}/config/eink_options.ini
echo "; this takes ~60 seconds" >> ${install_path}/config/eink_options.ini
echo "display_refresh_counter = 20" >> ${install_path}/config/eink_options.ini
echo "username = ${spotify_username}" >> ${install_path}/config/eink_options.ini
echo "token_file = ${spotify_token_path}" >> ${install_path}/config/eink_options.ini
echo "spotipy_log = ${install_path}/log/spotipy.log" >> ${install_path}/config/eink_options.ini
echo "no_song_cover = ${install_path}/resources/default.jpg" >> ${install_path}/config/eink_options.ini
echo "font_path = ${install_path}/resources/CircularStd-Bold.otf" >> ${install_path}/config/eink_options.ini
echo "font_size_title = 45" >> ${install_path}/config/eink_options.ini
echo "font_size_artist = 35" >> ${install_path}/config/eink_options.ini
echo "offset_px_left = 20" >> ${install_path}/config/eink_options.ini
echo "offset_px_right = 20" >> ${install_path}/config/eink_options.ini
echo "offset_px_top = 0" >> ${install_path}/config/eink_options.ini
echo "offset_px_bottom = 20" >> ${install_path}/config/eink_options.ini
echo "offset_text_px_shadow = 4" >> ${install_path}/config/eink_options.ini
echo "; text_direction possible values: top-down or bottom-up" >> ${install_path}/config/eink_options.ini
echo "text_direction = bottom-up" >> ${install_path}/config/eink_options.ini
echo "; possible modes are fit or repeat" >> ${install_path}/config/eink_options.ini
echo "background_mode = fit" >> ${install_path}/config/eink_options.ini
echo "done creation default config  ${install_path}/config/eink_options.ini"

if ! [ -d "${install_path}/log" ]; then
    echo "creating ${install_path}/log"
    mkdir "${install_path}/log"
fi
echo
echo "###### Spotipi-eink-display update service installation"
echo
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
echo "Creating spotipi-eink-display service:"
sudo cp "${install_path}/setup/service_template/spotipi-eink-display.service" /etc/systemd/system/
sudo sed -i -e "/\[Service\]/a ExecStart=${install_path}/spotipienv/bin/python3 ${install_path}/python/spotipiEinkDisplay.py" /etc/systemd/system/spotipi-eink-display.service
sudo sed -i -e "/ExecStart/a WorkingDirectory=${install_path}" /etc/systemd/system/spotipi-eink-display.service
sudo sed -i -e "/EnvironmentFile/a User=${UID_TO_USE}" /etc/systemd/system/spotipi-eink-display.service
sudo sed -i -e "/User/a Group=${GID_TO_USE}" /etc/systemd/system/spotipi-eink-display.service
sudo mkdir /etc/systemd/system/spotipi-eink-display.service.d
spotipi_env_path=/etc/systemd/system/spotipi-eink-display.service.d/spotipi-eink-display_env.conf
sudo touch $spotipi_env_path
echo "[Service]" | sudo tee -a $spotipi_env_path > /dev/null
echo "Environment=\"SPOTIPY_CLIENT_ID=${spotify_client_id}\"" | sudo tee -a $spotipi_env_path > /dev/null
echo "Environment=\"SPOTIPY_CLIENT_SECRET=${spotify_client_secret}\"" | sudo tee -a $spotipi_env_path > /dev/null
echo "Environment=\"SPOTIPY_REDIRECT_URI=${spotify_redirect_uri}\"" | sudo tee -a $spotipi_env_path > /dev/null
sudo systemctl daemon-reload
sudo systemctl start spotipi-eink-display
sudo systemctl enable spotipi-eink-display
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
sudo sed -i -e "/ExecStart/a WorkingDirectory=${install_path}" /etc/systemd/system/spotipi-eink-buttons.service
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
