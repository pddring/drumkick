import signal
import RPi.GPIO as GPIO
import mido
import time
import serial
import os
import threading
from PIL import Image, ImageDraw
from st7789 import ST7789

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

def handle_trigger(pad, volume):
    global last_midi_note
    vel = volume

    if vel > 127:
      vel = 127

    if vel < 25:
      vel = 25

    sample = "bass"
    midi_note = 36

    if pad == "KICK":
      sample = "bass"
      midi_note = 36
    elif pad == "EDGE":
      sample = "ride_edge"
      midi_note = 59
    elif pad == "BOW":
      sample = "ride_bow"
      midi_note = 51
    elif pad == "BELL":
      sample = "ride_bell"
      midi_note = 53
    if midi_out == '':
      os.system("aplay samples/" + sample + ".wav &")
    else:
      midi_out.send(mido.Message('note_on', note=midi_note, channel=9, velocity=vel))
      #midi_out.send(mido.Message('note_on', note=midi_note, channel=9, velocity=0))
    print("Playing {} (midi note {}) with velocty {}".format(pad, midi_note, vel))
    last_midi_note = midi_note

# Connect to midi devices

def detect_midi():
  global midi_out
  global output_device_name
  global midi_in
  global input_device_name
  input_devices = mido.get_input_names()
  output_devices = mido.get_output_names()
  allowed_devices = ['MPK mini Play', 'USBMIDI', 'TD-17']
  output_device_name = ""
  input_device_name = ""
  for dev in output_devices:
    print("Found midi output device: ", dev)
    for allowed in allowed_devices:
      if allowed in dev:
        print("Found MIDI device:", dev)
        output_device_name = dev
  print("Connecting to MIDI output:", output_device_name)
  if output_device_name == "":
    print("Sorry - no compatable MIDI output devices detected: debug mode only")
    midi_out = ""
  else:
    midi_out = mido.open_output(output_device_name)

  for dev in input_devices:
    print("Found midi input device: ", dev)
    for allowed in allowed_devices:
      if allowed in dev:
        print("Found MIDI device:", dev)
        input_device_name = dev
  print("Connecting to MIDI output:", input_device_name)
  if input_device_name == "":
    print("Sorry - no compatable MIDI input devices detected: debug mode only")
    midi_in = ""
  else:
    midi_in = mido.open_input(input_device_name)

detect_midi()

def log_midi_in():
  global volume, last_midi_note
  while True:
    if midi_in != "":
      msg = midi_in.receive()
      print("Received MIDI note {} at velocity {}".format(msg.note, msg.velocity))
      last_midi_note = msg.note
      if msg.velocity > volume:
        volume = msg.velocity
      

def connect_trigger(port_number):
  trigger = ""
  global volume
  while True:
    try:
      port = "/dev/ttyUSB" + str(port_number)
      trigger = serial.Serial(port, 115200)
      print("Connected to " + port)
    except:
      print("Could not detect drum trigger via USB")

    if trigger!= "":
      while True:
        line = trigger.readline().decode('ascii').strip()
        pad,vol = line.split(":")
        vol = int(vol)
        handle_trigger(pad,vol)
        if vol > volume:
          volume = vol
    else:
      time.sleep(5)      


print("Loaded successfully: playing cymbal crash sound as indicator")
os.system("aplay samples/ride_edge.wav&")

def poll_buttons():
  note = 1
  while True:
    for i in range(len(BUTTONS)):
      if GPIO.input(BUTTONS[i]) == False:
        
        if LABELS[i] == "A":
          note+= 1
        elif LABELS[i] == "B":
          note-= 1
        if note < 1:
          note = 1
        if note > 127:
          note = 127
        print("Button", LABELS[i], "pressed", note)
        midi_out.send(mido.Message('note_on', note=note, channel=9, velocity=127))
    time.sleep(.5)

# check if any devices are disconnected
def detect_usb_changes():
  while True:
    print("Checking USB devices")
    detect_midi()
    time.sleep(10)

def update_screen():
  global volume
  SPI_SPEED_MHZ = 80

  image = Image.new("RGB", (240, 240), (0, 0, 0))
  draw = ImageDraw.Draw(image)

  st7789 = ST7789(
      rotation=90,  # Needed to display the right way up on Pirate Audio
      port=0,       # SPI port
      cs=1,         # SPI port Chip-select channel
      dc=9,         # BCM pin used for data/command
      backlight=13,
      spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
  )
  global volume
  global last_midi_note
  color = (0,0,255)
  COLORS = {
    42: (255,255,0), # Hi hat closed
    46: (255,255,0), # Hi hat open
    44: (255,255,0), # Hi hat foot
    57: (255,255,0), # Crash
    48: (255,100,255), # Low tom
    45: (0,255,255), # Low tom
    43: (155,0,0), # Floor tom
    36: (255,255,255), # Kick
    51: (100,255,50), # Ride bow
    59: (100,255,50), # Ride edge
    53: (100,255,50), # Ride bell
  }
  while True:
      draw.rectangle((0, 0, 240, 240), (0,0,0))
      color = "red"
      if last_midi_note in COLORS:
        color = COLORS[last_midi_note]
      draw.ellipse((115-volume/2, 115-volume/2, 125+volume/2, 125+volume/2), fill=color)
      draw.text((0,0), "Connected:", (100,100,100))
      draw.text((0,20), output_device_name, (100, 100, 100))

      if volume > 0:
          volume = int(volume * .8)
      
      st7789.display(image)

      time.sleep(1.0 / 30)



# Finally, since button handlers don't require a "while True" loop,
# we pause the script to prevent it exiting immediately.

# start thread to detect MIDI device connect / disconnect
t_check_usb = threading.Thread(target = detect_usb_changes)
t_check_usb.start()

# start thread to update screen
t_update_screen = threading.Thread(target = update_screen)
t_update_screen.start()

# start thread to poll buttons (edge detection isn't working)
t_poll_buttons = threading.Thread(target = poll_buttons)
t_poll_buttons.start()

# start thread to log midi input
t_midi_in = threading.Thread(target = log_midi_in)
t_midi_in.start()

volume = 127
last_midi_note = 0
t_triggers = []
print("Connecting to serial ports")
for i in range(2):
  t_triggers.append(threading.Thread(target = connect_trigger, args=[i]))
  t_triggers[i].start()