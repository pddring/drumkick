import datetime
import json
from diagnostics import log
testing_without_pi = False
try:
    import RPi.GPIO
except:
    testing_without_pi = True
midi_in = ""
midi_out = ""
volume = {}
last_activity = datetime.datetime.now()

pad_settings = {
    "default": {
        "max_in": 1023, 
        "max_out": 127,             # max volume
        "min_out": 0
    }
}

def save():
    with open("settings.json", "w") as f:
        json.dump(pad_settings, f) 

def load():
    try:    
        with open("settings.json", "r") as f:
            pad_settings = json.load(f)
    except:
        log("Could not load settings file settings.json - creating a new one")
        save()

last_midi_note = 0

if __name__ == "__main__":
    while True:
        cmd = input("load or save?")
        if cmd == "load":
            load()
            print(pad_settings)
        elif cmd == "save":
            save()