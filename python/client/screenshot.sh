#!/bin/bash
install_path=$1

echo $install_path

firefox --headless --screenshot --window-size=600,448 file://$install_path/python/client/spotipi.html

sudo mv /screenshot.png $install_path/python/client/screenshot.png

python $install_path/inky/examples/7color/image.py $install_path/python/client/screenshot.png
