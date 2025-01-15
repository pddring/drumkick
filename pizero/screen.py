import globals
import midi
import time
from diagnostics import log

try:
    import RPi.GPIO as GPIO
except:
    globals.testing_without_pi = True

from PIL import Image, ImageDraw
if globals.testing_without_pi:
    import tkinter as tk
    from PIL import ImageTk
else:
   from st7789 import ST7789

def update_screen():
  volume = globals.volume
  SPI_SPEED_MHZ = 80

  image = Image.new("RGB", (240, 240), (0, 0, 0))
  draw = ImageDraw.Draw(image)
  if globals.testing_without_pi:
    window = tk.Tk()
    lbl = None
  else:
    st7789 = ST7789(
        rotation=90,  # Needed to display the right way up on Pirate Audio
        port=0,       # SPI port
        cs=1,         # SPI port Chip-select channel
        dc=9,         # BCM pin used for data/command
        backlight=13,
        spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
    )
  global last_midi_note
  color = (0,0,255)
  COLORS = {
    42: (255,255,0), # Hi hat closed
    46: (255,255,0), # Hi hat open
    44: (255,255,0), # Hi hat foot
    57: (255,255,0), # Crash
    48: (255,100,255), # Low tom
    45: (0,255,255), # Low tom
    43: (155,0,0), # Floor tom
    36: (255,255,255), # Kick
    51: (100,255,50), # Ride bow
    59: (100,255,50), # Ride edge
    53: (100,255,50), # Ride bell
  }
  running = True
  while running:
      draw.rectangle((0, 0, 240, 240), (0,0,0))
      color = "red"
      if globals.last_midi_note in COLORS:
        color = COLORS[globals.last_midi_note]
      draw.ellipse((115-volume/2, 115-volume/2, 125+volume/2, 125+volume/2), fill=color)
      draw.text((0,0), "MIDI in:", (200,100,100))
      draw.text((20,20), midi.output_device_name, (200, 100, 100))
      draw.text((0,40), "MIDI out:", (100,200,100))
      draw.text((20,60), midi.input_device_name, (100, 200, 100))

      if volume > 0:
          volume = int(volume * .8)
      
      if globals.testing_without_pi:
        if lbl == None:
          img = ImageTk.PhotoImage(image)
          lbl = tk.Label(window, image=img)
          lbl.pack()
          window.update()
        else:
          try:
            img = ImageTk.PhotoImage(image)
            lbl.configure(image = img)
            lbl.image = img
            
            window.update()
          except:
             # Probably because the user has closed the window
             running = False
          
      else:
        st7789.display(image)
        

      time.sleep(1.0 / 30)

if __name__ == "__main__":
  update_screen()