#!/bin/bash
install_path=$1
res=$2
firefox --headless --screenshot /tmp/screenshot.png --window-size=$res file://$install_path/python/client/spotipi-eink.html &> /dev/null
python3 $install_path/inky/examples/7color/image.py /tmp/screenshot.png
