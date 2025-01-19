from diagnostics import log
import time
import mido
import midi
import globals
import serial
import audio

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
        pad,vol = handle_line(line)
        handle_trigger(pad,vol)
    else:
      time.sleep(5)

def handle_line(line):
  # detect loudest signal
  parts = line.split(" ")
  max_vol = 0
  max_pad = ""
  for part in parts:
    try:
      pad,vol = part.split(":")
      vol = int(vol)

      pad_settings = globals.pad_settings["default"]
      if pad in globals.pad_settings:
        pad_settings = globals.pad_settings[pad]

      vol = vol / pad_settings["max_in"]
      range = pad_settings["max_out"] - pad_settings["min_out"]
      vol = int(pad_settings["min_out"] + (vol * range))
      if vol > 127:
        vol = 127
      if vol < 0:
        vol = 0

      print(pad,vol)

      if vol > max_vol:
        max_vol = vol
        max_pad = pad
    except:
      log("Invalid trigger input:", line)
      
  return max_pad, max_vol
  

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
      audio.play_sample(sample)
    else:
      midi.send(mido.Message('note_on', note=midi_note, channel=9, velocity=vel))
    log("Playing {} (midi note {}) with velocty {}".format(pad, midi_note, vel))
    globals.last_midi_note = midi_note

if __name__ == "__main__":
  import random
  while True:
    line = input("Enter sensor input (e.g. BOW:512 EDGE:321 BELL:54) or leave blank for random values:")
    if line == "":
      bow = random.randint(1, 1023)
      edge = random.randint(1, 1023)
      bell = random.randint(1, 1023)
      line = "BOW:{} BELL:{} EDGE:{}".format(bow, edge, bell)
      print(line)
    print(handle_line(line))

