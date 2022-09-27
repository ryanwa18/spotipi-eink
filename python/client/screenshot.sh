#!/bin/bash

CWD=`pwd`
filename=$1

firefox --headless --screenshot --window-size=600,448 file://'/home/pi/workspace/spotipi-eink/python/client/spotipi.html' 

python /home/pi/workspace/spotipi-eink/inky/examples/7color/image.py /home/pi/workspace/spotipi-eink/python/screenshot.png
