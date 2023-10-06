import spotipy
import spotipy.util as util

def getSongInfo(username: str, token_path:str) -> list:

  scope = 'user-read-currently-playing'
  token = util.prompt_for_user_token(username, scope, cache_path=token_path)
  if token:
      sp = spotipy.Spotify(auth=token)
      result = sp.current_user_playing_track()
    
      if result is None:
         print("No song playing")
         return []
      else:  
        song = result["item"]["name"]
        artist = result["item"]["artists"][0]["name"]
        image_url = result["item"]["album"]["images"][0]["url"]
        return [song, image_url, artist]
  else:
    print(f"Can't get token for {username}")
    return []
