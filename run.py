#!/usr/bin/python

from pad4pi import rpi_gpio
import time
import sys
import queue

#Our Imports
from lights import Lights 
from tv import TV

#Queues
light_q = queue.Queue()
tv_q = queue.Queue()

def cleanup():
    global keypad
    keypad.cleanup()

def key_pressed(key):
    print("INPUT: " + str(key))
    if key == "A":
        light_q.put("light_toggle")
    elif key == "B":
        light_q.put("brightness_toggle")
    elif key == "D":
        light_q.put("red_alert_toggle")
        tv_q.put("red_alert_toggle")
        print("RED ALERT")
    else:
        print("UNKNOWN REQUEST")

try:
    global light_q
    #Setup GPIO Keypad
    KEYPAD = [
       [1, 2, 3, "A"],
       [4, 5, 6, "B"],
       [7, 8, 9, "C"],
       ["*", 0, "#", "D"]
    ]
    factory = rpi_gpio.KeypadFactory()
    ROW_PINS = [2, 3, 4, 17] # BCM numbering
    COL_PINS = [22, 27, 10, 9] # BCM numbering
    keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
    keypad.registerKeyPressHandler(key_pressed)

    #Register Lights
    light_thread = Lights(dir_q=light_q)
    light_thread.start()

    #Register RV
    tv_thread = TV(dir_q=tv_q)
    tv_thread.start()

    #loop forever and ever
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Goodbye")
finally:
    cleanup()
