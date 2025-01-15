

import signal
import globals
from diagnostics import log
    
import mido
import time
import serial
import os
import threading

import midi
import screen
import trigger
import buttons
import audio

log("Loaded successfully: playing cymbal crash sound as indicator")
audio.play_sample("ride_edge")

# start thread to detect MIDI device connect / disconnect
t_check_usb = threading.Thread(target = midi.detect_usb_changes)
t_check_usb.start()

# start thread to update screen
t_update_screen = threading.Thread(target = screen.update_screen)
t_update_screen.start()

# start thread to poll buttons (edge detection isn't working)
t_poll_buttons = threading.Thread(target = buttons.poll_buttons)
t_poll_buttons.start()

# start thread to log midi input
t_midi_in = threading.Thread(target = midi.log_midi_in)
t_midi_in.start()

t_triggers = []
log("Connecting to serial ports")
for i in range(2):
  t_triggers.append(threading.Thread(target = trigger.connect_trigger, args=[i]))
  t_triggers[i].start()