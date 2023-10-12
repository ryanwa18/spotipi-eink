import sys
import spotipy
import spotipy.util as util


def getSongInfo(username: str, token_path: str) -> list:
    scope = 'user-read-currently-playing,user-modify-playback-state'
    token = util.prompt_for_user_token(username, scope, cache_path=token_path)
    if token:
        sp = spotipy.Spotify(auth=token)
        result = sp.current_user_playing_track()
        if result:
            song = result["item"]["name"]
            artist_name = ''
            for artists_tmp in result["item"]["artists"]:
                if artist_name:
                    artist_name += ', '
                artist_name += artists_tmp["name"]
            # artist_urn = result["item"]["artists"][0]["uri"]
            song_pic_url = result["item"]["album"]["images"][0]["url"]
            # artist_details = sp.artist(artist_urn)
            # artist_pic_url = artist_details['images'][0]['url']
            return [song, song_pic_url, artist_name]  # , artist_pic_url]
        return []
    else:
        print(f"Error: Can't get token for {username}", file=sys.stderr)
        return []
