import spotipy
import spotipy.util as util
import time


def get_state(current_state:str) -> str:
    states = ['track', 'context', 'off']
    index = states.index(current_state)
    if index < (len(states)-1):
        return states[index+1]
    else:
        return states[0]

urn = 'spotify:artist:6OQBBEvC35PrW087ClDpNk'
scope = 'user-read-currently-playing,user-modify-playback-state'
token = util.prompt_for_user_token(username='gabbaj03', scope=scope, cache_path=r'C:\Users\mail\Documents\Python\spotipi-eink\python\.cache')
if token:
    sp = spotipy.Spotify(auth=token)
    #artist = sp.artist(urn)
    #print(artist)
    current_state = 'context'
    print(f'repeat: {current_state}')
    sp.repeat(state=current_state)
    time.sleep(5)
    current_state = get_state(current_state)
    print(f'repeat: {current_state}')
    sp.repeat(state=current_state)
    time.sleep(5)
    current_state = get_state(current_state)
    print(f'repeat: {current_state}')
    sp.repeat(state=current_state)
    time.sleep(5)
    current_state = get_state(current_state)
    print(f'repeat: {current_state}')
    sp.repeat(state=current_state)
    