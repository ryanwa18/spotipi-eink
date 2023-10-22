import time
import sys
import logging
from logging.handlers import RotatingFileHandler
import spotipy
import spotipy.util as util
import os
import traceback
import configparser
import requests
import signal
from PIL import Image, ImageDraw, ImageFont, ImageOps
from lib import epd4in01f


# recursion limiter for get song info to not go to infinity as decorator
def limit_recursion(limit):
    def inner(func):
        func.count = 0

        def wrapper(*args, **kwargs):
            func.count += 1
            if func.count < limit:
                result = func(*args, **kwargs)
            else:
                result = None
            func.count -= 1
            return result
        return wrapper
    return inner


class SpotipiEinkDisplay:
    def __init__(self, delay=1):
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        self.delay = delay
        # Configuration for the matrix
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), '..', 'config', 'eink_options.ini'))
        # set spotipoy lib logger
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=self.config.get('DEFAULT', 'spotipy_log'), level=logging.INFO)
        logger = logging.getLogger('spotipy_logger')
        # automatically deletes logs more than 2000 bytes
        handler = RotatingFileHandler(self.config.get('DEFAULT', 'spotipy_log'), maxBytes=2000, backupCount=3)
        logger.addHandler(handler)
        # prep some vars before entering service loop
        self.song_prev = ''
        self.pic_counter = 0
        self.logger = self._init_logger()
        self.logger.info('Service instance created')

    def _init_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(logging.Formatter('Spotipi eInk Display - %(message)s'))
        logger.addHandler(stdout_handler)
        return logger

    def _handle_sigterm(self, sig, frame):
        self.logger.warning('SIGTERM received stopping')
        sys.exit(0)

    def _break_fix(self, text: str, width: int, font: ImageFont, draw: ImageDraw):
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
        yield from self._break_fix(text[lo:], width, font, draw)

    def _fit_text_top_down(self, img: Image, text: str, text_color: str, shadow_text_color: str, font: ImageFont, y_offset: int, font_size: int, x_start_offset: int = 0, x_end_offset: int = 0, offset_text_px_shadow: int = 0) -> int:
        """
        Fit text into container after applying line breaks. Returns the total
        height taken up by the text
        """
        width = img.width - x_start_offset - x_end_offset - offset_text_px_shadow
        draw = ImageDraw.Draw(img)
        pieces = list(self._break_fix(text, width, font, draw))
        y = y_offset
        h_taken_by_text = 0
        for t, _ in pieces:
            if offset_text_px_shadow > 0:
                draw.text((x_start_offset + offset_text_px_shadow, y + offset_text_px_shadow), t, font=font, fill=shadow_text_color)
            draw.text((x_start_offset, y), t, font=font, fill=text_color)
            new_height = font_size
            y += font_size
            h_taken_by_text += new_height
        return h_taken_by_text

    def _fit_text_bottom_up(self, img: Image, text: str, text_color: str, shadow_text_color: str, font: ImageFont, y_offset: int, font_size: int, x_start_offset: int = 0, x_end_offset: int = 0, offset_text_px_shadow: int = 0) -> int:
        """
        Fit text into container after applying line breaks. Returns the total
        height taken up by the text
        """
        width = img.width - x_start_offset - x_end_offset - offset_text_px_shadow
        draw = ImageDraw.Draw(img)
        pieces = list(self._break_fix(text, width, font, draw))
        y = y_offset
        if len(pieces) > 1:
            y -= (len(pieces) - 1) * font_size
        h_taken_by_text = 0
        for t, _ in pieces:
            if offset_text_px_shadow > 0:
                draw.text((x_start_offset + offset_text_px_shadow, y + offset_text_px_shadow), t, font=font, fill=shadow_text_color)
            draw.text((x_start_offset, y), t, font=font, fill=text_color)
            new_height = font_size
            y += font_size
            h_taken_by_text += new_height
        return h_taken_by_text

    def _display_clean(self):
        """cleans the display
        """
        try:
            epd = epd4in01f.EPD()
            epd.init()
            epd.Clear()
        except Exception as e:
            self.logger.error(f'Display clean error: {e}')

    def _display_image(self, image: Image, saturation: float = 0.5):
        """displays a image on the inky display

        Args:
            image (Image): Image to display
            saturation (float, optional): saturation. Defaults to 0.5.
        """
        try:
            epd = epd4in01f.EPD()
            epd.init()
            epd.display(epd.getbuffer(image, saturation))
        except Exception as e:
            self.logger.error(f'Display image error: {e}')

    def _gen_pic(self, image: Image, artist: str, title: str) -> Image:
        """Generates the Picture for the display

        Args:
            config (configparser.ConfigParser): Config parser object
            image (Image): album cover to be used
            artist (str): Artist text
            title (str): Song text

        Returns:
            Image: The finished image
        """
        album_cover_small_px = self.config.getint('DEFAULT', 'album_cover_small_px')
        offset_px_left = self.config.getint('DEFAULT', 'offset_px_left')
        offset_px_right = self.config.getint('DEFAULT', 'offset_px_right')
        offset_px_top = self.config.getint('DEFAULT', 'offset_px_top')
        offset_px_bottom = self.config.getint('DEFAULT', 'offset_px_bottom')
        offset_text_px_shadow = self.config.getint('DEFAULT', 'offset_text_px_shadow')
        text_direction = self.config.get('DEFAULT', 'text_direction')
        # The width and height of the background
        bg_w, bg_h = image.size
        if self.config.get('DEFAULT', 'background_mode') == 'fit':
            if bg_w < self.config.getint('DEFAULT', 'width') or bg_w > self.config.getint('DEFAULT', 'width'):
                image_new = ImageOps.fit(image=image, size=(self.config.getint('DEFAULT', 'width'), self.config.getint('DEFAULT', 'height')), centering=(0, 0))
            else:
                # no need to expand just crop
                image_new = image.crop((0, 0, self.config.getint('DEFAULT', 'width'), self.config.getint('DEFAULT', 'height')))
        if self.config.get('DEFAULT', 'background_mode') == 'repeat':
            if bg_w < self.config.getint('DEFAULT', 'width') or bg_h < self.config.getint('DEFAULT', 'height'):
                # we need to repeat the background
                # Creates a new empty image, RGB mode, and size of the display
                image_new = Image.new('RGB', (self.config.getint('DEFAULT', 'width'), self.config.getint('DEFAULT', 'height')))
                # Iterate through a grid, to place the background tile
                for x in range(0, self.config.getint('DEFAULT', 'width'), bg_w):
                    for y in range(0, self.config.getint('DEFAULT', 'height'), bg_h):
                        # paste the image at location x, y:
                        image_new.paste(image, (x, y))
            else:
                # no need to repeat just crop
                image_new = image.crop((0, 0, self.config.getint('DEFAULT', 'width'), self.config.getint('DEFAULT', 'height')))
        if self.config.getboolean('DEFAULT', 'album_cover_small'):
            cover_smaller = image.resize([album_cover_small_px, album_cover_small_px], Image.LANCZOS)
            album_pos_x = (self.config.getint('DEFAULT', 'width') - album_cover_small_px) // 2
            image_new.paste(cover_smaller, [album_pos_x, offset_px_top])
        font_title = ImageFont.truetype(self.config.get('DEFAULT', 'font_path'), self.config.getint('DEFAULT', 'font_size_title'))
        font_artist = ImageFont.truetype(self.config.get('DEFAULT', 'font_path'), self.config.getint('DEFAULT', 'font_size_artist'))
        if text_direction == 'topDown':
            title_position_y = album_cover_small_px + offset_px_top + 10
            title_height = self._fit_text_top_down(img=image_new, text=title, text_color='white', shadow_text_color='black', font=font_title, font_size=self.config.getint('DEFAULT', 'font_size_title'), y_offset=title_position_y, x_start_offset=offset_px_left, x_end_offset=offset_px_right, offset_text_px_shadow=offset_text_px_shadow)
            artist_position_y = album_cover_small_px + offset_px_top + 10 + title_height
            self._fit_text_top_down(img=image_new, text=artist, text_color='white', shadow_text_color='black', font=font_artist, font_size=self.config.getint('DEFAULT', 'font_size_artist'), y_offset=artist_position_y, x_start_offset=offset_px_left, x_end_offset=offset_px_right, offset_text_px_shadow=offset_text_px_shadow)
        if text_direction == 'bottom-up':
            artist_position_y = self.config.getint('DEFAULT', 'height') - (offset_px_bottom + self.config.getint('DEFAULT', 'font_size_artist'))
            artist_height = self._fit_text_bottom_up(img=image_new, text=artist, text_color='white', shadow_text_color='black', font=font_artist, font_size=self.config.getint('DEFAULT', 'font_size_artist'), y_offset=artist_position_y, x_start_offset=offset_px_left, x_end_offset=offset_px_right, offset_text_px_shadow=offset_text_px_shadow)
            title_position_y = self.config.getint('DEFAULT', 'height') - (offset_px_bottom + self.config.getint('DEFAULT', 'font_size_title')) - artist_height
            self._fit_text_bottom_up(img=image_new, text=title, text_color='white', shadow_text_color='black', font=font_title, font_size=self.config.getint('DEFAULT', 'font_size_title'), y_offset=title_position_y, x_start_offset=offset_px_left, x_end_offset=offset_px_right, offset_text_px_shadow=offset_text_px_shadow)
        return image_new

    def _display_update_process(self, song_request: list):
        """Display update process that jude by the song_request list if a song is playing and we need to download the album cover or not

        Args:
            song_request (list): song_request list
            config (configparser.ConfigParser): config object
            pic_counter (int): picture refresh counter

        Returns:
            int: updated picture refresh counter
        """
        if song_request:
            # download cover
            image = self._gen_pic(Image.open(requests.get(song_request[1], stream=True).raw), song_request[2], song_request[0])
        else:
            # not song playing use logo
            image = self._gen_pic(Image.open(self.config.get('DEFAULT', 'no_song_cover')), 'spotipi-eink', 'No song playing')
        # clean screen every x pics
        if self.pic_counter > self.config.getint('DEFAULT', 'display_refresh_counter'):
            self._display_clean()
            self.pic_counter = 0
        # display picture on display
        self._display_image(image)
        self.pic_counter += 1

    @limit_recursion(limit=10)
    def _get_song_info(self) -> list:
        """get the current played song from Spotifys Web API

        Returns:
            list: with song name, album cover url, artist's name's
        """
        scope = 'user-read-currently-playing,user-modify-playback-state,user-library-read'
        token = util.prompt_for_user_token(username=self.config.get('DEFAULT', 'username'), scope=scope, cache_path=self.config.get('DEFAULT', 'token_file'))
        if token:
            sp = spotipy.Spotify(auth=token)
            result = sp.currently_playing(additional_types='episode')
            if result:
                try:
                    if result['currently_playing_type'] == 'episode':
                        song = result["item"]["name"]
                        artist_name = result["item"]["show"]["name"]
                        song_pic_url = result["item"]["images"][0]["url"]
                        return [song, song_pic_url, artist_name]
                    if result['currently_playing_type'] == 'track':
                        song = result["item"]["name"]
                        artist_name = ''
                        for artists_tmp in result["item"]["artists"]:
                            if artist_name:
                                artist_name += ', '
                            artist_name += artists_tmp["name"]
                        song_pic_url = result["item"]["album"]["images"][0]["url"]
                        return [song, song_pic_url, artist_name]
                    if result['currently_playing_type'] == 'unknown':
                        # we hit the moment when spotify api has no known state about the client
                        # simply lets retry a short moment again
                        time.sleep(0.01)
                        return self._get_song_info()
                    if result['currently_playing_type'] == 'ad':
                        # a ad is playing.. lets say no song is playing....
                        return []
                    # we should never hit this
                    self.logger.error(f'Error: Unsupported currently_playing_type: {result["currently_playing_type"]}')
                    self.logger.error(f'Error: Spotify currently_playing result content: {result}')
                except TypeError:
                    # https://stackoverflow.com/questions/69253296/spotipy-typeerror-nonetype-object-is-not-subscriptable-when-trying-to-acce
                    # catch this error and simply try again.
                    # try to get it again a short amount of time later
                    self.logger.error('Error: TypeError')
                    time.sleep(0.01)
                    return self._get_song_info()
            return []
        else:
            self.logger.error(f"Error: Can't get token for {self.config.get('DEFAULT', 'username')}")
            return []

    def start(self):
        self.logger.info('Service started')
        # clean screen initially
        self._display_clean()
        try:
            while True:
                try:
                    song_request = self._get_song_info()
                    if song_request:
                        if self.song_prev != song_request[0] + song_request[1]:
                            self.song_prev = song_request[0] + song_request[1]
                            self._display_update_process(song_request=song_request)
                    if not song_request:
                        if self.song_prev != 'NO_SONG':
                            # set fake song name to update only once if no song is playing.
                            self.song_prev = 'NO_SONG'
                            self._display_update_process(song_request=song_request)
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                    self.logger.error(traceback.format_exc())
                time.sleep(self.delay)
        except KeyboardInterrupt:
            self.logger.info('Service stopping')
            sys.exit(0)


if __name__ == "__main__":
    service = SpotipiEinkDisplay()
    service.start()
