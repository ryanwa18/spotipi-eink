import sys
import time
import spotipy
import spotipy.util as util


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


@limit_recursion(limit=10)
def getSongInfo(username: str, token_path: str) -> list:
    scope = 'user-read-currently-playing,user-modify-playback-state'
    token = util.prompt_for_user_token(username, scope, cache_path=token_path)
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
                    return getSongInfo(username, token_path)
                if result['currently_playing_type'] == 'ad':
                    # a ad is playing.. lets say no song is playing....
                    return []
                # we should never hit this
                print(f'Error: Unsupported currently_playing_type: {result["currently_playing_type"]}', file=sys.stderr)
                print(f'Error: Spotify currently_playing result content: {result}', file=sys.stderr)
            except TypeError:
                # https://stackoverflow.com/questions/69253296/spotipy-typeerror-nonetype-object-is-not-subscriptable-when-trying-to-acce
                # catch this error and simply try again.
                # try to get it in a short moment again.
                time.sleep(0.01)
                return getSongInfo(username, token_path)
        return []
    else:
        print(f"Error: Can't get token for {username}", file=sys.stderr)
        return []
