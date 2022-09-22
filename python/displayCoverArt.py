import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
import requests
from io import BytesIO
from PIL import Image
import sys,os,re
import configparser
from bs4 import BeautifulSoup

if len(sys.argv) > 2:
    username = sys.argv[1]
    token_path = sys.argv[2]

    # Configuration file    
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, '../config/rgb_options.ini')

    # Configures logger for storing song data    
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='spotipy.log',level=logging.INFO)
    logger = logging.getLogger('spotipy_logger')

    # automatically deletes logs more than 2000 bytes
    handler = RotatingFileHandler('spotipy.log', maxBytes=2000,  backupCount=3)
    logger.addHandler(handler)

    # Configuration for the matrix
    config = configparser.ConfigParser()
    config.read(filename)

    default_image = os.path.join(dir, config['DEFAULT']['default_image'])

    prevSong    = ""
    currentSong = ""
    try:
      while True:
        try:
          imageURL = getSongInfo(username, token_path)[1]
          songName = getSongInfo(username, token_path)[0]
          artistName = getSongInfo(username, token_path)[2]
          currentSong = imageURL

          if ( prevSong != currentSong ):
            response = requests.get(imageURL)
            image = Image.open(BytesIO(response.content))
            image.thumbnail((250, 250), Image.ANTIALIAS)
            prevSong = currentSong

            # Edit html file
            with open('/home/pi/workspace/spotipi-eink/python/client/spotipi.html') as html_file:
              soup = BeautifulSoup(html_file.read(), features='html.parser')
              soup.h1.string.replace_with(songName)
              soup.image['src'] = imageURL
              soup.body['style'] = "background-image: url('" + imageURL + "')"
              soup.h2.string.replace_with(artistName)
              new_text = soup.prettify()
            
            with open('/home/pi/workspace/spotipi-eink/python/client/spotipi.html', mode='w') as new_html_file:
              new_html_file.write(new_text)

          time.sleep(1)
        except Exception as e:
          image = Image.open(default_image)
          image.thumbnail((250, 250), Image.ANTIALIAS)
          print(e)
          time.sleep(1)
    except KeyboardInterrupt:
      sys.exit(0)

else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()
