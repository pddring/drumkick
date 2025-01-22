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

notes = {
    36: "bass",
    51: "ride_bow",
    38: "snare",
    48: "tom_high",
    53: "ride_bell",
    59: "ride_edge",
    43: "tom_floor",
    45: "tom_low"
}

def play_note(note, vel=127):
    global notes
    if note in notes:
        play_sample(notes[note], vel)

def play_sample(sample, vel=127):
    if sample in samples:
        log("Playing", sample, "at volume:", vel)
        pygame.mixer.Sound.play(samples[sample]).set_volume(vel/127)
        
    else:
        log("Sample", sample, "not found")

pygame.init()
files = get_sample_names()
preload(files)
pygame.mixer.set_num_channels(256)

if __name__ == "__main__":
    for i in range(16):
        play_sample("ride_bow")
        if i % 4 == 0:
            play_sample("bass")
        if i % 2 == 0:
            play_sample("snare")
        time.sleep(.3)
    
    time.sleep(4)