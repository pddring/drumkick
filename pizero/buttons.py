import globals
from diagnostics import log
import mido
import time
import midi


# The buttons on Pirate Audio are connected to pins 5, 6, 16 and 24
# Boards prior to 23 January 2020 used 5, 6, 16 and 20 
# try changing 24 to 20 if your Y button doesn't work.
BUTTONS = [5, 6, 16, 24]

# These correspond to buttons A, B, X and Y respectively
LABELS = ['A', 'B', 'X', 'Y']
if not globals.testing_without_pi:
    import RPi.GPIO as GPIO
    # Set up RPi.GPIO with the "BCM" numbering scheme
    GPIO.setmode(GPIO.BCM)

    # Buttons connect to ground when pressed, so we should set them up
    # with a "PULL UP", which weakly pulls the input signal to 3.3V.
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

notes = [42, 46, 44, 57, 48, 48, 43, 36, 51, 59, 53]
note_index = 0

def handle_button(label):
    global notes, note_index
    log("Button", label, "pressed")
    if label == "A":
        note_index += 1
        if note_index > len(notes) - 1:
            note_index = 0
    elif label == "B":
        note_index -= 1
        if note_index < 0:
            note_index = len(notes) - 1
    elif label == "X":
        note = notes[note_index]    
        midi.send(mido.Message('note_on', note=note, channel=9, velocity=127))
    

def poll_buttons():
    global note
    if globals.testing_without_pi:
        log("No GPIO buttons detected: press A, B, X or Y to emulate a button press")
        while True:
            b = input("Press a button:")
            handle_button(b)
    else:
        while True:
            for i in range(len(BUTTONS)):
                if GPIO.input(BUTTONS[i]) == False:
                    handle_button(LABELS[i])
            time.sleep(.5)

if __name__ == "__main__":
    poll_buttons()