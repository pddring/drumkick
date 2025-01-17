import globals
import midi
import time
import datetime
from diagnostics import log

from PIL import Image, ImageDraw, ImageFont
if globals.testing_without_pi:
    import tkinter as tk
    from PIL import ImageTk
else:
   from st7789 import ST7789

def update_screen():
  SPI_SPEED_MHZ = 80
  SLEEP_S = 5
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
  
  CATEGORIES = {
     "Hi Hat": {
        "pads": [42, 46, 44],
        "colour": (255,255,0)
     },
     "Crash": {
        "pads": [57],
        "colour": (255,255,0)
     },
     "Snare": {
        "pads": [38],
        "colour": (100,255,50)
     },
     "Hi Tom": {
        "pads": [48],
        "colour": (255,100,255)
     },
     "Low Tom": {
        "pads": [45],
        "colour": (0, 255, 255),
     },
     "Floor Tom": {
        "pads": [43],
        "colour": (0, 255, 255),
     },
     "Kick": {
        "pads": [36],
        "colour": (255,255,255)
     },
     "Ride": {
        "pads": [51, 59, 53],
        "colour": (100, 255, 50)
     }
  }
  running = True
  time_font = ImageFont.truetype("fonts/dimitri.ttf", size=66)
  date_font = ImageFont.truetype("fonts/dimitri.ttf", size=30)
  while running:
      now = datetime.datetime.now()
      inactive = now - globals.last_activity
      draw.rectangle((0, 0, 240, 240), (0,0,0))
      if inactive.seconds > SLEEP_S:
         draw.text((0,0), now.strftime("%I:%M:%S"), (100, 100, 100), font=time_font)
         draw.text((30,80), now.strftime("%a %d %b %y"), (100, 100, 100), font=date_font)
      else:
         
         draw.text((0,0), "IN: " + midi.output_device_name, (200,100,100))
         draw.text((0,10), "OUT: " + midi.output_device_name, (100,200,100))      
            
         y = 50
         others = []
         for pad in globals.volume:
            if globals.volume[pad] > 1:
               others.append(pad)
         for category in CATEGORIES:
            v = 1
            for pad in CATEGORIES[category]["pads"]:
               if pad in globals.volume:
                  if pad in others:
                     others.remove(pad)
                  if globals.volume[pad] > v:
                     v = globals.volume[pad]
            
            draw.rectangle((100, y, v+100, y+10), CATEGORIES[category]["colour"])
            draw.text((0, y), category, (255,255,255))      
            y += 20
         
         # show other category
         v = 1
         for pad in others:
            if globals.volume[pad] > v:
               v = globals.volume[pad]
         draw.rectangle((100, y, v+100, y+10), (255, 0, 0))
         draw.text((0, y), "Other", (255,255,255))      
      
      for pad in globals.volume:
        if globals.volume[pad] > 1:
            globals.volume[pad] = int(globals.volume[pad] * .8)
      
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