testing_without_pi = False
try:
    import RPi.GPIO
except:
    testing_without_pi = True
midi_in = ""
midi_out = ""
volume = {}

last_midi_note = 0