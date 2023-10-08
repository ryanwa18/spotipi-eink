import sys
from spotipy.oauth2 import SpotifyOAuth


def main():
    if len(sys.argv) > 1:
        username = sys.argv[1]
        scope = 'user-read-currently-playing,user-modify-playback-state'

        # This way removes the need for a browser, it will instead give the URL to visit in the terminal
        auth = SpotifyOAuth(scope=scope, open_browser=False)
        token = auth.get_access_token(as_dict=False)
        if not token:
            print('Error unable to get token', file=sys.stderr)
            sys.exit(-1)
    else:
        print(f"Usage: {sys.argv[0]} username")
        sys.exit()

if __name__ == "__main__":
    main()