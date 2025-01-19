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

def key_handler_event(event):
   key_handler_label(event.char.upper())

def key_handler_label(label):
   if globals.state == globals.STATE_TIME:
        globals.state = globals.STATE_MIXER
        globals.last_activity = datetime.datetime.now()
    
   if globals.state == globals.STATE_MIXER:
      if label == "A":
         globals.state = globals.STATE_SENSOR_SETTINGS
   
   elif globals.state == globals.STATE_SENSOR_SETTINGS:
      if label == "A":
         globals.sensor_state -= 1
         if globals.sensor_state < globals.SENSOR_STATE_SELECT_PAD:
            globals.sensor_state = globals.SENSOR_STATE_BACK
      elif label == "B":
         globals.sensor_state += 1
         if globals.sensor_state > globals.SENSOR_STATE_BACK:
            globals.sensor_state = globals.SENSOR_STATE_SELECT_PAD
      if globals.sensor_state == globals.SENSOR_STATE_SELECT_PAD:
         if label == "X":
            globals.selected_sensor += 1
            if globals.selected_sensor > len(globals.SENSOR_NAMES) - 1:
               globals.selected_sensor = 0
         if label == "Y":
            globals.selected_sensor -= 1
            if globals.selected_sensor < 0:
               globals.selected_sensor = len(globals.SENSOR_NAMES) - 1
      elif globals.sensor_state == globals.SENSOR_STATE_BACK:
         if label in ["X", "Y"]:
            globals.state = globals.STATE_MIXER
            globals.last_activity = datetime.datetime.now()

def update_screen():
  SPI_SPEED_MHZ = 80
  SLEEP_S = 5
  globals.state = globals.STATE_MIXER
  image = Image.new("RGB", (240, 240), (0, 0, 0))
  draw = ImageDraw.Draw(image)
  if globals.testing_without_pi:
    window = tk.Tk()
    window.bind("<Key>", key_handler_event)
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

      if globals.state == globals.STATE_MIXER:
         if inactive.seconds > SLEEP_S:
            globals.state = globals.STATE_TIME
         
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
      
      elif globals.state == globals.STATE_SENSOR_SETTINGS:
         draw.rectangle((0, 0, 240, 10), (255,255,255))

         def centre_text(y, txt, colour):
            _,_,w,h = draw.textbbox((0,0), txt)
            draw.text((120 - w/2, y), txt, colour)
            
         centre_text(0, "Sensor settings", (0,0,0))

         if globals.sensor_state == globals.SENSOR_STATE_SELECT_PAD:
            y = 10
         elif globals.sensor_state == globals.SENSOR_STATE_SET_MAX_IN:
            y = 30
         elif globals.sensor_state == globals.SENSOR_STATE_RESET:
            y = 40
         elif globals.sensor_state == globals.SENSOR_STATE_SAVE:
            y = 50
         elif globals.sensor_state == globals.SENSOR_STATE_BACK:
            y = 60
         c = (255, 255, 255)
         draw.rectangle((0, y, 240, y+10), (90, 60, 60))
         draw.text((0, y), "<", (0,0,0))
         draw.text((230, y), ">", (0,0,0))

         sensor = globals.SENSOR_NAMES[globals.selected_sensor]
         centre_text(10, sensor, c)

         pad_settings = globals.pad_settings["default"]
         if sensor in globals.pad_settings:
            pad_settings = globals.pad_settings[sensor]
         centre_text(30, "Max sensor value: {}".format(
            pad_settings["max_in"]
         ), c)

         centre_text(40, "Reset", c)
         centre_text(50, "Save", c)
         centre_text(60, "Back", c)
      
      elif globals.state == globals.STATE_TIME:
         draw.text((0,0), now.strftime("%I:%M:%S"), (100, 100, 100), font=time_font)
         draw.text((30,80), now.strftime("%a %d %b %y"), (100, 100, 100), font=date_font)
         if inactive.seconds < SLEEP_S:
           globals.state = globals.STATE_MIXER
      
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
