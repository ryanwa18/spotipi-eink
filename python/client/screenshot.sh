#!/bin/bash
install_path=$1
res=$2
echo $install_path
firefox --headless --screenshot  --window-size=$res file://$install_path/python/client/spotipi-eink.html
python3 $install_path/inky/examples/7color/image.py /tmp/screenshot.png
