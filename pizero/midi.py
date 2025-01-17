import mido
import time
import globals
from diagnostics import log
import audio

output_device_name = ""
input_device_name = ""

def send(msg):
    pad = msg.note
    volume = msg.velocity

    if pad in globals.volume:
      if volume > globals.volume[pad]:
        globals.volume[pad] = volume
    else:
      globals.volume[pad] = volume

    if globals.midi_out == "":
        log("No MIDI output device to send", msg)
        audio.play_note(pad)
    else:
        log("Sending to midi device", msg)
        globals.midi_out.send(msg)


# scans for and connects to MIDI devices
def detect_usb_changes():
  
  global output_device_name
  
  global input_device_name

  allowed_devices = ['MPK mini Play', 'USBMIDI', 'TD-17', 'MPK Mini']

  while True:   
    # scan for output devices
    output_devices = mido.get_output_names()
    if output_device_name == "" or output_device_name not in output_devices:
        output_device_name = ""
        log("Checking for USB MIDI output devices")
        output_device_name = ""

        for dev in output_devices:
            for allowed in allowed_devices:
                if allowed in dev:
                    log("Found MIDI output device:", dev)
                    output_device_name = dev
            if output_device_name != "":
                break
            else:
                log("Ignoring MIDI output device:", dev)
    
        if output_device_name == "":
            log("No compatable MIDI output devices detected: debug mode only")
            globals.midi_out = ""
        else:
            log("Connecting to MIDI output:", output_device_name)
            globals.midi_out = mido.open_output(output_device_name)

    # scan for input devices
    input_devices = mido.get_input_names()    
    if input_device_name == "" or input_device_name not in input_devices:
        input_device_name = ""
        for dev in input_devices:
            for allowed in allowed_devices:
                if allowed in dev:
                    log("Found MIDI input device:", dev)
                    input_device_name = dev
            if input_device_name != "":
                break
            else:
                log("Ingoring MIDI input device:", dev)
        
        if input_device_name == "":
            log("No compatable MIDI input devices detected: debug mode only")
            globals.midi_in = ""
        else:
            log("Connecting to MIDI input:", input_device_name)
            globals.midi_in = mido.open_input(input_device_name)
    time.sleep(5)

def log_midi_in():
  while True:
    if globals.midi_in != "":
      msg = globals.midi_in.receive()
      log("Received MIDI note {} at velocity {}".format(msg.note, msg.velocity))
      last_midi_note = msg.note
      if msg.note in globals.volume:
        if msg.velocity > globals.volume[msg.note]:
            globals.volume[msg.note] = msg.velocity
      else:
          globals.volume[msg.note] = msg.velocity


if __name__ == "__main__":
    detect_usb_changes()