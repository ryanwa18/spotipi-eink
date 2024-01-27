#!/bin/bash
install_path=$1
#echo $install_path
firefox --headless --screenshot /tmp/screenshot.png --window-size=600,448 file://$install_path/python/client/spotipi-eink.html
python3 $install_path/inky/examples/7color/image.py /tmp/screenshot.png
