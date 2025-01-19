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

SENSOR_NAMES = ["KICK", "BOW", "BELL", "EDGE"]
selected_sensor = 0


STATE_MIXER = 1
STATE_TIME = 2
STATE_SENSOR_SETTINGS = 3

SENSOR_STATE_SELECT_PAD = 1
SENSOR_STATE_SET_MAX_IN = 2
SENSOR_STATE_SET_MIN_OUT = 3
SENSOR_STATE_SET_MAX_OUT = 4
SENSOR_STATE_RESET = 5
SENSOR_STATE_SAVE = 6
SENSOR_STATE_BACK = 7
sensor_state = SENSOR_STATE_SELECT_PAD
state = STATE_MIXER

def save():
    with open("settings.json", "w") as f:
        json.dump(pad_settings, f) 

def load():
    global pad_settings
    log("Loading settings from file")
    try:    
        with open("settings.json", "r") as f:
            pad_settings = json.load(f)
    except:
        log("Could not load settings file settings.json - creating a new one")
        save()

last_midi_note = 0
load()

if __name__ == "__main__":
    while True:
        cmd = input("load or save?")
        if cmd == "load":
            load()
            print(pad_settings)
        elif cmd == "save":
            save()