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


def update_html_file(file_path: str, song_name: str, artist_name: str):
    # Edit html file
    with open(file_path) as html_file:
        soup = BeautifulSoup(html_file.read(), features='html.parser')
        soup.h1.string.replace_with(song_name)
        soup.h2.string.replace_with(artist_name)
        new_text = soup.prettify()
    # Write new html file
    with open(file_path, mode='w') as new_html_file:
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


def display_update_process(song_request: list, config: configparser.ConfigParser, firefox_cmd: list, screenshot_file: str, pic_counter: int) -> int:
    if song_request:
        # download cover
        urllib.request.urlretrieve(url=song_request[1], filename=config['DEFAULT']['album_cover_path'])
        # update html file with song details
        update_html_file(file_path=config['DEFAULT']['html_file_path'], song_name=song_request[0], artist_name=song_request[2])
    else:
        # not song playing copy logo
        shutil.copyfile(config['DEFAULT']['no_song_cover'], config['DEFAULT']['album_cover_path'])
        # update html file
        update_html_file(file_path=config['DEFAULT']['html_file_path'], song_name='No song playing', artist_name='spotipi-eink')
    # create screenshot of html file
    subprocess.check_call(firefox_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # clean screen every x pics
    if pic_counter > int(config['DEFAULT']['display_refresh_counter']):
        display_clean()
        pic_counter = 0
    # display screenshot on display
    display_screenshot(screenshot=screenshot_file)
    pic_counter += 1
    return pic_counter


def main():
    # Configuration file
    dir = os.path.dirname(__file__)
    config_file = os.path.join(dir, '..', 'config', 'eink_options.ini')
    # Configuration for the matrix
    config = configparser.ConfigParser()
    config.read(config_file)
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S %p', filename=config['DEFAULT']['spotipy_log'], level=logging.INFO)
    logger = logging.getLogger('spotipy_logger')
    # automatically deletes logs more than 2000 bytes
    handler = RotatingFileHandler(config['DEFAULT']['spotipy_log'], maxBytes=2000,  backupCount=3)
    logger.addHandler(handler)
    # clean screen initially
    display_clean()
    # prep some vars befor entering service loop
    song_prev = ''
    screenshot_file = os.path.join(tempfile.gettempdir(), config['DEFAULT']['screenshot_filename'])
    firefox_cmd = ['firefox', '--headless', '--screenshot', screenshot_file,
                f"--window-size={config['DEFAULT']['width']},{config['DEFAULT']['height']}", f"file://{config['DEFAULT']['html_file_path']}"]
    pic_counter = 0
    try:
        while True:
            try:
                song_request = getSongInfo(config['DEFAULT']['username'], config['DEFAULT']['token_file'])
                if song_request:
                    if song_prev != song_request[1]:
                        song_prev = song_request[1]
                        pic_counter = display_update_process(song_request=song_request, config=config, firefox_cmd=firefox_cmd, screenshot_file=screenshot_file, pic_counter=pic_counter)
                if not song_request:
                    if song_prev != 'NO_SONG':
                        # set fake song name to updae only once if no song is playing.
                        song_prev = 'NO_SONG'
                        pic_counter = display_update_process(song_request=song_request, config=config, firefox_cmd=firefox_cmd, screenshot_file=screenshot_file, pic_counter=pic_counter)
                time.sleep(1)
            except Exception as e:
                print(f'Error: {e}', file=sys.stderr)
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)



if __name__ == "__main__":
    main()