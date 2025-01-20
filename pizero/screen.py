import globals
import midi
import time
import datetime
import copy
from diagnostics import log
import diagnostics
import trigger

from PIL import Image, ImageDraw, ImageFont
if globals.testing_without_pi:
    import tkinter as tk
    from PIL import ImageTk
else:
   from st7789 import ST7789

def key_handler_event(event):
   key_handler_label(event.char.upper())

def key_handler_label(label):
   # When on timer, press any key to go back to the mixer
   if globals.state == globals.STATE_TIME:
        globals.state = globals.STATE_MIXER
        globals.last_activity = datetime.datetime.now()
    
   # when on mixer press A to change pad settings
   if globals.state == globals.STATE_MIXER:
      if label == "A":
         globals.state = globals.STATE_SENSOR_SETTINGS
   
   elif globals.state == globals.STATE_SENSOR_SETTINGS:
      # A moves up
      if label == "A":
         globals.sensor_state -= 1
         if globals.sensor_state < globals.SENSOR_STATE_SELECT_PAD:
            globals.sensor_state = globals.SENSOR_STATE_SAVE
      # B moves down
      elif label == "B":
         globals.sensor_state += 1
         if globals.sensor_state > globals.SENSOR_STATE_SAVE:
            globals.sensor_state = globals.SENSOR_STATE_SELECT_PAD
      
      # X and Y changes currently selected item
      if globals.sensor_state == globals.SENSOR_STATE_SELECT_PAD:
         if label == "X":
            globals.selected_sensor += 1
            if globals.selected_sensor > len(globals.SENSOR_NAMES) - 1:
               globals.selected_sensor = 0
         if label == "Y":
            globals.selected_sensor -= 1
            if globals.selected_sensor < 0:
               globals.selected_sensor = len(globals.SENSOR_NAMES) - 1

      
      elif globals.sensor_state == globals.SENSOR_STATE_RESET:
         # Reset to default
         if label  == "X": 
            globals.pad_settings[globals.SENSOR_NAMES[globals.selected_sensor]] = copy.deepcopy(globals.pad_settings["default"])
         
         # auto (load from max hit detected)
         if label == "Y":
            pad = globals.SENSOR_NAMES[globals.selected_sensor]
            if pad in globals.loudest:
               globals.pad_settings[pad]["max_in"] = globals.loudest[pad]
            else:
               log("Play " + pad + " as loud as you can then try again")

            

      elif globals.sensor_state == globals.SENSOR_STATE_SAVE:
         if label in ["X", "Y"]:
            globals.save()
            globals.state = globals.STATE_MIXER
            globals.last_activity = datetime.datetime.now()
      
      elif globals.sensor_state == globals.SENSOR_STATE_SET_MAX_IN:
         pad_settings = copy.deepcopy(globals.pad_settings["default"])
         pad = globals.SENSOR_NAMES[globals.selected_sensor]
         if pad in globals.pad_settings:
            pad_settings = globals.pad_settings[pad]
         else:
            globals.pad_settings[pad] = pad_settings
         if label == "Y":
            pad_settings["max_in"] += 1
            if pad_settings["max_in"] > 1023:
               pad_settings["max_in"] = 1023
         elif label == "X":
            pad_settings["max_in"] -= 1
            if pad_settings["max_in"] < 0:
               pad_settings["max_in"] = 0

      elif globals.sensor_state == globals.SENSOR_STATE_SET_MIN_OUT:
         pad_settings = copy.deepcopy(globals.pad_settings["default"])
         pad = globals.SENSOR_NAMES[globals.selected_sensor]
         if pad in globals.pad_settings:
            pad_settings = globals.pad_settings[pad]
         else:
            globals.pad_settings[pad] = pad_settings
         if label == "Y":
            pad_settings["min_out"] += 1
            if pad_settings["min_out"] > 127:
               pad_settings["min_out"] = 127
         elif label == "X":
            pad_settings["min_out"] -= 1
            if pad_settings["min_out"] < 0:
               pad_settings["min_out"] = 0

      elif globals.sensor_state == globals.SENSOR_STATE_SET_MAX_OUT:
         pad_settings = copy.deepcopy(globals.pad_settings["default"])
         pad = globals.SENSOR_NAMES[globals.selected_sensor]
         if pad in globals.pad_settings:
            pad_settings = globals.pad_settings[pad]
         else:
            globals.pad_settings[pad] = pad_settings
         if label == "Y":
            pad_settings["max_out"] += 1
            if pad_settings["max_out"] > 127:
               pad_settings["max_out"] = 127
         elif label == "X":
            pad_settings["max_out"] -= 1
            if pad_settings["max_out"] < 0:
               pad_settings["max_out"] = 0

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
  menu_font = ImageFont.truetype("fonts/dimitri.ttf", size=18)
  time_font = ImageFont.truetype("fonts/dimitri.ttf", size=66)
  date_font = ImageFont.truetype("fonts/dimitri.ttf", size=30)
  while running:
      now = datetime.datetime.now()
      inactive = now - globals.last_activity
      draw.rectangle((0, 0, 240, 240), (0,0,0))

      if globals.state == globals.STATE_MIXER:
         if inactive.seconds > SLEEP_S:
            globals.state = globals.STATE_TIME
         
         draw.text((0,0), "IN: " + midi.output_device_name, (200,100,100), font=menu_font)
         draw.text((0,20), "OUT: " + midi.output_device_name, (100,200,100), font=menu_font)      
            
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
            draw.text((0, y), category, (255,255,255), font=menu_font)      
            y += 20
         
         # show other category
         v = 1
         for pad in others:
            if globals.volume[pad] > v:
               v = globals.volume[pad]
         draw.rectangle((100, y, v+100, y+10), (255, 0, 0))
         draw.text((0, y), "Other", (255,255,255), font=menu_font)
      
      elif globals.state == globals.STATE_SENSOR_SETTINGS:
         draw.rectangle((0, 0, 240, 20), (255,255,255))

         def centre_text(y, txt, colour):
            _,_,w,h = draw.textbbox((0,0), txt, font=menu_font)
            draw.text((120 - w/2, y), txt, colour, font=menu_font)
            
         centre_text(0, "Sensor settings", (0,0,0))

         if globals.sensor_state == globals.SENSOR_STATE_SELECT_PAD:
            y = 20
         elif globals.sensor_state == globals.SENSOR_STATE_SET_MAX_IN:
            y = 40
         elif globals.sensor_state == globals.SENSOR_STATE_SET_MIN_OUT:
            y = 60
         elif globals.sensor_state == globals.SENSOR_STATE_SET_MAX_OUT:
            y = 80
         elif globals.sensor_state == globals.SENSOR_STATE_RESET:
            y = 100
         elif globals.sensor_state == globals.SENSOR_STATE_SAVE:
            y = 120

         c = (255, 255, 255)
         draw.rectangle((0, y, 240, y+20), (90, 60, 60))
         draw.text((0, y+5), "<-", (0,0,0))
         draw.text((230, y+5), "->", (0,0,0))

         sensor = globals.SENSOR_NAMES[globals.selected_sensor]
         centre_text(20, sensor, c)

         pad_settings = copy.deepcopy(globals.pad_settings["default"])
         if sensor in globals.pad_settings:
            pad_settings = globals.pad_settings[sensor]
         centre_text(40, "Max sensor value: {}".format(
            pad_settings["max_in"]
         ), c)

         centre_text(60, "Min output value: {}".format(
            pad_settings["min_out"]
         ), c)

         centre_text(80, "Max output value: {}".format(
            pad_settings["max_out"]
         ), c)

         centre_text(100, "X: Reset | Y: Auto", c)
         centre_text(120, "Save", c)
         latest = 0
         if sensor in globals.latest:
            latest = globals.latest[sensor]
         loudest = 0
         if sensor in globals.loudest:
            loudest = globals.loudest[sensor]
         centre_text(140, "Latest: {}/1023 => {}/127".format(latest, trigger.scale(sensor, latest)), (0, 0, 255))
         centre_text(160, "Loudest: {}/1023 => {}/127".format(loudest, trigger.scale(sensor, loudest)), (0, 0, 255))

         y = 180
         for msg in diagnostics.buffer:
            draw.text((0, y), msg, (255,0,0))
            y+= 10
            if y > 240:
               break
      
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
