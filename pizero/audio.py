from diagnostics import log
import os
import globals
import time

import pygame

samples = {}


def get_sample_names():
    files = []
    for file in os.listdir("samples"):
        if file.endswith(".wav"):
            files.append(file.replace(".wav", ""))
    return files

def preload(sounds):
    for sound in sounds:
        samples[sound] = pygame.mixer.Sound("samples/" + sound +".wav")


def play_sample(sample):
    
    if globals.testing_without_pi:
        if sample in samples:
            log("Playing", sample)
            pygame.mixer.Sound.play(samples[sample])
            
        else:
            log("Sample", sample, "not found")
    else:
        os.system("aplay samples/" + sample + ".wav")



if __name__ == "__main__":
    pygame.init()
    files = get_sample_names()
    preload(files)
    pygame.mixer.set_num_channels(256)
    for i in range(16):
        play_sample("ride_bow")
        if i % 4 == 0:
            play_sample("bass")
        if i % 2 == 0:
            play_sample("snare")
        time.sleep(.3)
    
    time.sleep(4)