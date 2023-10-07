import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
import os
import configparser
from bs4 import BeautifulSoup
import subprocess
import urllib.request
import shutil

def update_html(html_file_path: str, song_name: str, artist_name: str):
              # Edit html file
            with open(html_file_path) as html_file:
              soup = BeautifulSoup(html_file.read(), features='html.parser')
              soup.h1.string.replace_with(song_name)
              soup.h2.string.replace_with(artist_name)
              new_text = soup.prettify()
            # Write new html file
            with open(html_file_path, mode='w') as new_html_file:
              new_html_file.write(new_text)

if len(sys.argv) > 2:
    username = sys.argv[1]
    token_path = sys.argv[2]

    # Configuration file    
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, f'..{os.sep}config{os.sep}eink_options.ini')

    # Configures logger for storing song data    
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %p', filename=os.path.join(dir, 'spotipy.log'), level=logging.INFO)

    #logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %p', filename='/var/log/spotipy.log', level=logging.INFO)
    logger = logging.getLogger('spotipy_logger')

    # automatically deletes logs more than 2000 bytes
    handler = RotatingFileHandler(os.path.join(dir, 'spotipy.log'), maxBytes=2000,  backupCount=3)
    logger.addHandler(handler)

    # Configuration for the matrix
    config = configparser.ConfigParser()
    config.read(filename)

    # prep some vars befor entering service loop
    song_prev = ''
    song_current = ''
    album_cover_path = os.path.join(dir, f'client{os.sep}album_cover.jpg')
    screenshot_file_path = os.path.join(dir, f'client{os.sep}screenshot.sh')
    install_path = os.path.dirname(dir)
    display_res = f"{config['DEFAULT']['width']},{config['DEFAULT']['height']}"
    html_file_path = os.path.join(dir, f'client{os.sep}spotipi-eink.html')
    try:
      while True:
        try:
          song_request = getSongInfo(username, token_path)
          if song_request:
            song_name = song_request[0]
            song_current = song_request[1]
            artist_name = song_request[2]
          if not song_request:
            if song_prev != 'NO_SONG':
              # copy the default logo as cover.
              shutil.copyfile(os.path.join(dir, f'client{os.sep}static{os.sep}default.jpg'), album_cover_path)
              update_html(html_file_path, 'No song playing', 'spotipi-eink')
              # set fake song name to updae only once if no song is playing.
              song_prev = 'NO_SONG'
              song_current = 'NO_SONG'
              # Update display
              print(subprocess.check_call([screenshot_file_path, install_path, display_res]))
          if song_prev != song_current:
            # download cover
            urllib.request.urlretrieve(song_current, album_cover_path)
            song_prev = song_current
            update_html(html_file_path, song_name, artist_name)
            # Update display
            print(subprocess.check_call([screenshot_file_path, install_path, display_res]))
          time.sleep(1)
        except Exception as e:
          print(f"Error: {e}")
          time.sleep(1)
    except KeyboardInterrupt:
      sys.exit(0)
else:
    print(f"Usage: {sys.argv[0]} username token_path")
    sys.exit()
