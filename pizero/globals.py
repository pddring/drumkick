testing_without_pi = False
try:
    import GPIO
except:
    testing_without_pi = True
midi_in = ""
midi_out = ""
volume = 127

last_midi_note = 0