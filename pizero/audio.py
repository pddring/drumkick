from diagnostics import log
import os
import globals
def play_sample(sample):
    if globals.testing_without_pi:
        log("Playing", sample)
    else:
        os.system("aplay samples/" + sample + ".wav&")