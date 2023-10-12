import sys
import os
import configparser
import spotipy
import spotipy.util as util
import signal
import RPi.GPIO as GPIO

# some global stuff.
# initial status
current_state = 'context'
# initial Configuration file
dir = os.path.dirname(__file__)
config_file = os.path.join(dir, '..', 'config', 'eink_options.ini')
# Configuration for the matrix
config = configparser.ConfigParser()
config.read(config_file)
# Gpio pins for each button (from top to bottom)
BUTTONS = [5, 6, 16, 24]
# These correspond to buttons A, B, C and D respectively
LABELS = ['A', 'B', 'C', 'D']


def get_state(current_state: str) -> str:
    states = ['track', 'context', 'off']
    index = states.index(current_state)
    if index < (len(states)-1):
        return states[index+1]
    else:
        return states[0]


# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    global current_state
    global config
    # do this every time to load the latest refresh token from the displayCoverArt.py->getSongInfo.py
    scope = 'user-read-currently-playing,user-modify-playback-state'
    token = util.prompt_for_user_token(
        username=config['DEFAULT']['username'],
        scope=scope, cache_path=config['DEFAULT']['token_file'])
    if not token:
        print(f"Error with token: {config['DEFAULT']['token_file']}")
        return
    sp = spotipy.Spotify(auth=token)
    label = LABELS[BUTTONS.index(pin)]
    if label == 'A':
        sp.next_track()
        return
    if label == 'B':
        sp.previous_track()
        return
    if label == 'C':
        try:
            sp.start_playback()
        except spotipy.exceptions.SpotifyException:
            sp.pause_playback()
        return
    if label == 'D':
        current_state = get_state(current_state)
        sp.repeat(state=current_state)
        return


# CTR + C event clean up GPIO setup and exit nicly
def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)


def main():
    # Set up RPi.GPIO with the "BCM" numbering scheme
    GPIO.setmode(GPIO.BCM)

    # Buttons connect to ground when pressed, so we should set them up
    # with a "PULL UP", which weakly pulls the input signal to 3.3V.
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Loop through out buttons and attach the "handle_button" function to each
    # We're watching the "FALLING" edge (transition from 3.3V to Ground) and
    # picking a generous bouncetime of 250ms to smooth out button presses.
    for pin in BUTTONS:
        GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=250)

    # Finally, since button handlers don't require a "while True" loop,
    # We register the callback for CTRL+C handling
    signal.signal(signal.SIGINT, signal_handler)
    # We register the callback for SIGTERM handling
    signal.signal(signal.SIGTERM, signal_handler)
    # we pause the script to prevent it exiting immediately.
    signal.pause()


if __name__ == "__main__":
    main()
