import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
import os
import traceback
import configparser
import requests
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from inky.inky_uc8159 import CLEAN


def break_fix(text: str, width: int, font: ImageFont, draw: ImageDraw):
    """
    Fix line breaks in text.
    """
    if not text:
        return
    if isinstance(text, str):
        text = text.split()  # this creates a list of words
    lo = 0
    hi = len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        t = ' '.join(text[:mid])  # this makes a string again
        w = int(draw.textlength(text=t, font=font))
        if w <= width:
            lo = mid
        else:
            hi = mid - 1
    t = ' '.join(text[:lo])  # this makes a string again
    w = int(draw.textlength(text=t, font=font))
    yield t, w
    yield from break_fix(text[lo:], width, font, draw)


def fit_text_top_down(img: Image, text: str, text_color: str, shadow_text_color: str, font: ImageFont, y_offset: int, font_size: int, x_start_offset: int = 0, x_end_offset: int = 0, offset_text_px_shadow: int = 0) -> int:
    """
    Fit text into container after applying line breaks. Returns the total
    height taken up by the text
    """
    width = img.width - x_start_offset - x_end_offset - offset_text_px_shadow
    draw = ImageDraw.Draw(img)
    pieces = list(break_fix(text, width, font, draw))
    y = y_offset
    h_taken_by_text = 0
    for t, _ in pieces:
        if offset_text_px_shadow > 0:
            draw.text((x_start_offset+offset_text_px_shadow, y+offset_text_px_shadow), t, font=font, fill=shadow_text_color)
        draw.text((x_start_offset, y), t, font=font, fill=text_color)
        new_height = font_size
        y += font_size
        h_taken_by_text += new_height
    return h_taken_by_text


def fit_text_bottom_up(img: Image, text: str, text_color: str, shadow_text_color: str, font: ImageFont, y_offset: int, font_size: int, x_start_offset: int = 0, x_end_offset: int = 0, offset_text_px_shadow: int = 0) -> int:
    """
    Fit text into container after applying line breaks. Returns the total
    height taken up by the text
    """
    width = img.width - x_start_offset - x_end_offset - offset_text_px_shadow
    draw = ImageDraw.Draw(img)
    pieces = list(break_fix(text, width, font, draw))
    y = y_offset
    if len(pieces) > 1:
        y -= (len(pieces)-1)*font_size
    h_taken_by_text = 0
    for t, _ in pieces:
        if offset_text_px_shadow > 0:
            draw.text((x_start_offset+offset_text_px_shadow, y+offset_text_px_shadow), t, font=font, fill=shadow_text_color)
        draw.text((x_start_offset, y), t, font=font, fill=text_color)
        new_height = font_size
        y += font_size
        h_taken_by_text += new_height
    return h_taken_by_text


def display_clean():
    """cleans the display
    """
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


def display_image(image: Image, saturation: float = 0.5):
    """displays a image on the inky display

    Args:
        image (Image): Image to display
        saturation (float, optional): saturation. Defaults to 0.5.
    """
    try:
        inky = auto()
        inky.set_image(image, saturation=saturation)
        inky.show()
    except Exception as e:
        print(f'Display screenshot error: {e}', file=sys.stderr)


def gen_pic(config: configparser.ConfigParser, image: Image, artist: str, title: str) -> Image:
    """Generates the Picture for the display

    Args:
        config (configparser.ConfigParser): Config parser object
        image (Image): album cover to be used
        artist (str): Artist text
        title (str): Song text

    Returns:
        Image: The finished image
    """
    album_cover_small_px = config.getint('DEFAULT', 'album_cover_small_px')
    offset_px_left = config.getint('DEFAULT', 'offset_px_left')
    offset_px_right = config.getint('DEFAULT', 'offset_px_right')
    offset_px_top = config.getint('DEFAULT', 'offset_px_top')
    offset_px_bottom = config.getint('DEFAULT', 'offset_px_bottom')
    offset_text_px_shadow = config.getint('DEFAULT', 'offset_text_px_shadow')
    text_direction = config.get('DEFAULT', 'text_direction')
    # The width and height of the background
    bg_w, bg_h = image.size
    if bg_w < config.getint('DEFAULT', 'width') or bg_h < config.getint('DEFAULT', 'height'):
        # we need to repeat the background
        # Creates a new empty image, RGB mode, and size of the display
        image_new = Image.new('RGB', (config.getint('DEFAULT', 'width'), config.getint('DEFAULT', 'height')))
        # Iterate through a grid, to place the background tile
        for x in range(0, config.getint('DEFAULT', 'width'), bg_w):
            for y in range(0, config.getint('DEFAULT', 'height'), bg_h):
                # paste the image at location x, y:
                image_new.paste(image, (x, y))
    else:
        # no need to repeat
        image_new = image.crop((0, 0, config.getint('DEFAULT', 'width'), config.getint('DEFAULT', 'height')))
    if config.getboolean('DEFAULT', 'album_cover_small'):
        cover_smaller = image.resize([album_cover_small_px, album_cover_small_px], Image.LANCZOS)
        album_posx = (config.getint('DEFAULT', 'width') - album_cover_small_px) // 2
        image_new.paste(cover_smaller, [album_posx, offset_px_top])
    font_title = ImageFont.truetype(config.get('DEFAULT', 'font_path'), config.getint('DEFAULT', 'font_size_title'))
    font_artist = ImageFont.truetype(config.get('DEFAULT', 'font_path'), config.getint('DEFAULT', 'font_size_artist'))
    if text_direction == 'top-down':
        title_position_y = album_cover_small_px + offset_px_top + 10
        title_height = fit_text_top_down(img=image_new, text=title, text_color='white', shadow_text_color='black', font=font_title, font_size=config.getint('DEFAULT', 'font_size_title'), y_offset=title_position_y, x_start_offset=offset_px_left, x_end_offset=offset_px_right, offset_text_px_shadow=offset_text_px_shadow)
        artist_position_y = album_cover_small_px + offset_px_top + 10 + title_height
        fit_text_top_down(img=image_new, text=artist, text_color='white', shadow_text_color='black', font=font_artist, font_size=config.getint('DEFAULT', 'font_size_artist'), y_offset=artist_position_y, x_start_offset=offset_px_left, x_end_offset=offset_px_right, offset_text_px_shadow=offset_text_px_shadow)
    if text_direction == 'bottom-up':
        artist_position_y = config.getint('DEFAULT', 'height') - (offset_px_bottom + config.getint('DEFAULT', 'font_size_artist'))
        artist_height = fit_text_bottom_up(img=image_new, text=artist, text_color='white', shadow_text_color='black', font=font_artist, font_size=config.getint('DEFAULT', 'font_size_artist'), y_offset=artist_position_y, x_start_offset=offset_px_left, x_end_offset=offset_px_right, offset_text_px_shadow=offset_text_px_shadow)
        title_position_y = config.getint('DEFAULT', 'height') - (offset_px_bottom + config.getint('DEFAULT', 'font_size_title')) - artist_height
        fit_text_bottom_up(img=image_new, text=title, text_color='white', shadow_text_color='black', font=font_title, font_size=config.getint('DEFAULT', 'font_size_title'), y_offset=title_position_y, x_start_offset=offset_px_left, x_end_offset=offset_px_right, offset_text_px_shadow=offset_text_px_shadow)
    return image_new


def display_update_process(song_request: list, config: configparser.ConfigParser, pic_counter: int) -> int:
    """Display update process that judes by the song_request list if a song is playing and we need to download the album cover or not

    Args:
        song_request (list): song_request list
        config (configparser.ConfigParser): config object
        pic_counter (int): picture refresh counter

    Returns:
        int: updated picture refresh counter
    """    
    if song_request:
        # download cover
        image = gen_pic(config, Image.open(requests.get(song_request[1], stream=True).raw), song_request[2], song_request[0])
    else:
        # not song playing use logo
        image = gen_pic(config, Image.open(config.get('DEFAULT', 'no_song_cover')), 'spotipi-eink', 'No song playing')
    # clean screen every x pics
    if pic_counter > config.getint('DEFAULT', 'display_refresh_counter'):
        display_clean()
        pic_counter = 0
    # display screenshot on display
    display_image(image)
    pic_counter += 1
    return pic_counter


def main():
    # Configuration file
    dir = os.path.dirname(__file__)
    config_file = os.path.join(dir, '..', 'config', 'eink_options.ini')
    # Configuration for the matrix
    config = configparser.ConfigParser()
    config.read(config_file)
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %p', filename=config.get('DEFAULT', 'spotipy_log'), level=logging.INFO)
    logger = logging.getLogger('spotipy_logger')
    # automatically deletes logs more than 2000 bytes
    handler = RotatingFileHandler(
        config.get('DEFAULT', 'spotipy_log'), maxBytes=2000,  backupCount=3)
    logger.addHandler(handler)
    # clean screen initially
    display_clean()
    # prep some vars before entering service loop
    song_prev = ''
    pic_counter = 0
    try:
        while True:
            try:
                song_request = getSongInfo(config.get('DEFAULT', 'username'), config.get('DEFAULT', 'token_file'))
                if song_request:
                    if song_prev != song_request[0]+song_request[1]:
                        song_prev = song_request[0]+song_request[1]
                        pic_counter = display_update_process(
                            song_request=song_request, config=config, pic_counter=pic_counter)
                if not song_request:
                    if song_prev != 'NO_SONG':
                        # set fake song name to update only once if no song is playing.
                        song_prev = 'NO_SONG'
                        pic_counter = display_update_process(
                            song_request=song_request, config=config, pic_counter=pic_counter)
            except Exception as e:
                print(f'Error: {e}', file=sys.stderr)
                print(traceback.format_exc())
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
