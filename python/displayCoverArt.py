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
import tempfile
from PIL import Image
from inky.auto import auto
from inky.inky_uc8159 import CLEAN


def update_html_file(html_file_path: str, song_name: str, artist_name: str):
    # Edit html file
    with open(html_file_path) as html_file:
        soup = BeautifulSoup(html_file.read(), features='html.parser')
        soup.h1.string.replace_with(song_name)
        soup.h2.string.replace_with(artist_name)
        new_text = soup.prettify()
    # Write new html file
    with open(html_file_path, mode='w') as new_html_file:
        new_html_file.write(new_text)


def display_clean():
    try:
        inky = auto()
        for _ in range(2):
            for y in range(inky.height - 1):
                for x in range(inky.width - 1):
                    inky.set_pixel(x, y, CLEAN)

            inky.show()
            time.sleep(1.0)
    except Exception as e:
        print(f'Display clean error: {e}', file=sys.stderr)


def display_screenshot(screenshot: str, saturation: float = 0.5):
    try:
        inky = auto()
        image = Image.open(screenshot)
        inky.set_image(image, saturation=saturation)
        inky.show()
    except Exception as e:
        print(f'Display screenshot error: {e}', file=sys.stderr)


if len(sys.argv) > 2:
    username = sys.argv[1]
    token_path = sys.argv[2]

    # Configuration file
    dir = os.path.dirname(__file__)
    config_file = os.path.join(dir, '..', 'config', 'eink_options.ini')
    # Configures logger for storing song data
    spotipy_log = os.path.join(dir, 'spotipy.log')
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S %p', filename=spotipy_log, level=logging.INFO)
    logger = logging.getLogger('spotipy_logger')
    # automatically deletes logs more than 2000 bytes
    handler = RotatingFileHandler(spotipy_log, maxBytes=2000,  backupCount=3)
    logger.addHandler(handler)

    # Configuration for the matrix
    config = configparser.ConfigParser()
    config.read(config_file)
    # clean screen initially
    display_clean()
    # prep some vars befor entering service loop
    song_prev = ''
    song_current = ''
    album_cover_path = os.path.join(dir, 'client', 'album_cover.jpg')
    html_file_path = os.path.join(dir, 'client', 'spotipi-eink.html')
    screenshot_file = os.path.join(tempfile.gettempdir(), 'screenshot.png')
    firefox_cmd = ['firefox', '--headless', '--screenshot', screenshot_file,
                   f"--window-size={config['DEFAULT']['width']},{config['DEFAULT']['height']}", f'file://{html_file_path}']
    print(f'screenshot: {screenshot_file}')
    pic_counter = 0
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
                        shutil.copyfile(os.path.join(
                            dir, f'client{os.sep}static{os.sep}default.jpg'), album_cover_path)
                        update_html_file(html_file_path,
                                    'No song playing', 'spotipi-eink')
                        # set fake song name to updae only once if no song is playing.
                        song_prev = 'NO_SONG'
                        song_current = 'NO_SONG'
                        # Update display
                        subprocess.check_call(firefox_cmd, stdout=subprocess.DEVNULL ,stderr=subprocess.DEVNULL)
                         # clean screen every 20 pics
                        if pic_counter > 20:
                            display_clean()
                            pic_counter = 0
                        display_screenshot(screenshot=screenshot_file)
                        pic_counter += 1
                if song_prev != song_current:
                    # download cover
                    urllib.request.urlretrieve(song_current, album_cover_path)
                    song_prev = song_current
                    update_html_file(html_file_path, song_name, artist_name)
                    # Update display
                    subprocess.check_call(firefox_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    # clean screen every 20 pics
                    if pic_counter > 20:
                        display_clean()
                        pic_counter = 0
                    display_screenshot(screenshot=screenshot_file)
                    pic_counter += 1
                time.sleep(1)
            except Exception as e:
                print(f'Error: {e}', file=sys.stderr)
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)
else:
    print(f'Usage: {sys.argv[0]} username token_path', file=sys.stderr)
    sys.exit()
