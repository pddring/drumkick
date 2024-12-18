import signal
import RPi.GPIO as GPIO
import mido
import time

print("""drumkick.py - Detect which button has been pressed and play a midi note

This example should demonstrate how to:
1. set up RPi.GPIO to read buttons,
2. determine which button has been pressed

Press Ctrl+C to exit!

""")

# The buttons on Pirate Audio are connected to pins 5, 6, 16 and 24
# Boards prior to 23 January 2020 used 5, 6, 16 and 20 
# try changing 24 to 20 if your Y button doesn't work.
BUTTONS = [5, 6, 16, 24]

# These correspond to buttons A, B, X and Y respectively
LABELS = ['A', 'B', 'X', 'Y']

# Set up RPi.GPIO with the "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)

# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    label = LABELS[BUTTONS.index(pin)]
    print("Button press detected on pin: {} label: {}".format(pin, label))
    vel = 127
    vel_lookup = {"A":25, "B":50, "X":75, "Y":100}
    if label in vel_lookup:
       vel = vel_lookup[label]

    if midi_out != '':
    	midi_out.send(mido.Message('note_on', note=36, channel=9, velocity=vel))
    print("Playing bass drum with velocty {}".format(vel))


# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 100ms to smooth out button presses.
for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=100)

# Connect to midi devices
output_devices = mido.get_output_names()
allowed_devices = ['MPK mini Play mk3:MPK mini Play mk3 MIDI 1 24:0', 'USBMIDI:USBMIDI USBMIDI 24:0']
output_device_name = ""
for dev in output_devices:
  print("Found midi output device: ", dev)
  if dev in allowed_devices:
    print("Found MIDI device:", dev)
    output_device_name = dev
print("Connecting to MIDI output:", output_device_name)
if output_device_name == "":
  print("Sorry - no compatable MIDI output devices detected: debug mode only")
  midi_out = ""
else:
  midi_out = mido.open_output(output_device_name)

# Finally, since button handlers don't require a "while True" loop,
# we pause the script to prevent it exiting immediately.
signal.pause()
