import os, time
import threading, queue
from omxplayer import OMXPlayer
import atexit

class TV(threading.Thread):
    def __init__(self, dir_q):
        super(TV, self).__init__()
        self.RED_ALERT_ON = False
        self.dir_q = dir_q
        self.stoprequest = threading.Event()
        self.player = OMXPlayer("http://repo.posttwo.pt/redalert.mp4", args=['--no-osd', '--no-keys', '-b', '--loop'])
        self.player.pause()
        atexit.register(self.join)

    def run(self):
        while not self.stoprequest.isSet():
            try:
                #check queue for command
                workRequest = self.dir_q.get(True, 0.05)
                print("TV: " + str(workRequest))
                if workRequest == "red_alert_toggle":
                    self.red_alert()
            except queue.Empty:
                continue
    def tv_set_pi(self):
        os.system('echo "as" | cec-client -s')

    def tv_set_chrome(self):
        os.system('echo "txn 4f:82:20:00" | cec-client -s')

    def red_alert(self):
        if not self.RED_ALERT_ON:
            self.RED_ALERT_ON = True
            threading._start_new_thread(self.tv_set_pi, ())
            time.sleep(5)
            print("RED ALERT ON")
            self.player.seek(0)
            self.player.play()
        else:
            self.RED_ALERT_ON = False
            threading._start_new_thread(self.tv_set_chrome, ())
            self.player.pause()

    def join(self, timeout=None):
        print("TV EXITING")
        self.stoprequest.set()
        self.player.quit()
        super(TV, self).join(timeout)