import sys
import spotipy
import spotipy.util as util
import signal
import RPi.GPIO as GPIO


def get_state(current_state:str) -> str:
    states = ['track', 'context', 'off']
    index = states.index(current_state)
    if index < (len(states)-1):
        return states[index+1]
    else:
        return states[0]
    
# CTR + C event clean up GPIO setup and exit nicly
def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

if len(sys.argv) > 2:
    username = sys.argv[1]
    token_path = sys.argv[2]
    scope = 'user-modify-playback-state'
    token = util.prompt_for_user_token(username=username, scope=scope, cache_path=token_path)
    if not token:
        print(f'Error with token: {token_path}')
    sp = spotipy.Spotify(auth=token)
    # Gpio pins for each button (from top to bottom)
    BUTTONS = [5, 6, 16, 24]

    # These correspond to buttons A, B, C and D respectively
    LABELS = ['A', 'B', 'C', 'D']

    # Set up RPi.GPIO with the "BCM" numbering scheme
    GPIO.setmode(GPIO.BCM)

    # Buttons connect to ground when pressed, so we should set them up
    # with a "PULL UP", which weakly pulls the input signal to 3.3V.
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)


    current_state = 'context'
    # "handle_button" will be called every time a button is pressed
    # It receives one argument: the associated input pin.
    def handle_button(pin):
        label = LABELS[BUTTONS.index(pin)]
        print("Button press detected on pin: {} label: {}".format(pin, label))
        if label == 'A':
            print('next trak')
            sp.next_track()
        if label == 'B':
            print('previos rack')
            sp.previous_track()
        if label == 'C':
            try:
                sp.start_playback()
            except spotipy.exceptions.SpotifyException as e:
                print(f'error: {e}')
                print('allready playing so we pause')
                sp.pause_playback()
        if label == 'D':
            current_state = get_state(current_state)
            print(f'repeat: {current_state}')
            sp.repeat(state=current_state)

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
else:
    print(f"Usage: {sys.argv[0]} username token_path")
    sys.exit()