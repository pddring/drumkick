from diagnostics import log
import time
import mido
import globals
import serial

def connect_trigger(port_number):
  trigger = ""
  while True:
    try:
      port = "/dev/ttyUSB" + str(port_number)
      trigger = serial.Serial(port, 115200)
      log("Connected to " + port)
    except:
      log("Could not detect drum trigger via port", port_number)

    if trigger!= "":
      while True:
        line = trigger.readline().decode('ascii').strip()
        pad,vol = line.split(":")
        vol = int(vol)
        handle_trigger(pad,vol)
        if vol > globals.volume:
          globals.volume = vol
    else:
      time.sleep(5)      

def handle_trigger(pad, volume):
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
    if globals.midi_out == '':
      os.system("aplay samples/" + sample + ".wav &")
    else:
      midi.send(mido.Message('note_on', note=midi_note, channel=9, velocity=vel))
    log("Playing {} (midi note {}) with velocty {}".format(pad, midi_note, vel))
    globals.last_midi_note = midi_note

