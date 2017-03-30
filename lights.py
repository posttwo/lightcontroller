import os, time
import threading, queue
from lifxlan import *
import atexit

class Lights(threading.Thread):
    """ TODO: Make it query the light for changes from elsewhere """
    def __init__(self, dir_q):
        super(Lights, self).__init__()
        self.dir_q = dir_q
        self.stoprequest = threading.Event()
        self.RED_ALERT_ON = False
        self.CURRENT_ON = True
        self.CURRENT_COLOR = 0
        self.CURRENT_SATURATION = 0
        self.CURRENT_BRIGHTNESS = 65535
        self.CURRENT_KELVIN = 2500
        self.lifx = LifxLAN(1)
        self.force_current()
        atexit.register(self.join)

    def run(self):
        while not self.stoprequest.isSet():
            try:
                #check queue for command
                workRequest = self.dir_q.get(True, 0.05)
                print("LIGHT: " + str(workRequest))
                if workRequest == "light_toggle":
                    self.toggle_on()
                elif workRequest == "brightness_toggle":
                    self.toggle_brightness() 
                elif workRequest == "red_alert_toggle":
                    if not self.RED_ALERT_ON:
                        self.RED_ALERT_ON = True
                        t1 = threading.Thread(target=self.red_alert)
                        t1.start()
                    else:
                        self.RED_ALERT_ON = False
            except queue.Empty:
                continue

    def join(self, timeout=None):
        print("LIGHTS EXITING")
        self.stoprequest.set()
        super(Lights, self).join(timeout)

    def force_current(self):
        self.set_color(self.CURRENT_COLOR, self.CURRENT_SATURATION, self.CURRENT_KELVIN)

    def set_color(self, hue, saturation, kelvin=2500):
        self.lifx.set_color_all_lights([hue, saturation, self.CURRENT_BRIGHTNESS, kelvin], 500, True)
    
    def toggle_on(self):
        if self.CURRENT_ON:
            self.lifx.set_power_all_lights('off')
            self.CURRENT_ON = False
        else:
            self.lifx.set_power_all_lights('on')
            self.CURRENT_ON = True
    
    def toggle_brightness(self):
        print("SETTING BRIGHTNESS")
        if self.CURRENT_BRIGHTNESS < 65535:
            self.CURRENT_BRIGHTNESS = self.CURRENT_BRIGHTNESS + 13107
        else:
            self.CURRENT_BRIGHTNESS = 13107
        self.force_current()

    def red_alert(self):
        print("RED ALERT TRIGGERED")
        self.lifx.set_power_all_lights("on")
        while self.RED_ALERT_ON:
            self.lifx.set_color_all_lights([0, 65535, 65535, 2500], 500, True)
            sleep(0.8)
            self.lifx.set_color_all_lights([0, 0, 65535, 2500], 500, True)
            sleep(0.8)
