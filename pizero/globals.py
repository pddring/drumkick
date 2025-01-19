import datetime
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

last_midi_note = 0