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

last_midi_note = 0