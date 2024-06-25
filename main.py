#!/usr/bin/python3

import signal
import sys
import pprint
import time
import matplotlib.pyplot as plt
import matplotlib
import atexit

import t_read

rs = t_read.READ_SENSORS()
atexit.register( rs.writeLogFile )

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
# SIGKILL seems tricky. ADded timer for continously storage

class ROOM:
    def __init__(self, rs, id, ax):
        self.rs = rs
        self.id = id
        self.ax = ax
    
        self.firstTime = True

    def update(self):
        xT,yT = self.rs.getTemp(self.id)
        xH,yH = self.rs.getHumidity(self.id)

        if self.firstTime:
            self.name = self.rs.getName(self.id)
            # Do not plot None sensors
            if self.name == None:
                return

            self.lineTemp = None
            if yT != None:
                self.lineTemp, = ax[0].plot(xT, yT, label=self.name)#, **{'marker': 'o'})

            self.lineHumi = None
            if yH != None:
                self.lineHumi, = ax[1].plot(xH, yH, label=self.name)#, **{'marker': 'o'})

            self.firstTime = False

        else:
            if self.lineTemp is not None:
                self.lineTemp.set_xdata(xT)
                self.lineTemp.set_ydata(yT)
                self.lineTemp.set_label("{}: {}".format(self.name, yT[-1]))

            if self.lineHumi is not None:
                self.lineHumi.set_xdata(xH)
                self.lineHumi.set_ydata(yH)
                self.lineHumi.set_label("{}: {}".format(self.name, yH[-1]))


if __name__ == "__main__":

    myLines = {}
    
    matplotlib.rcParams['toolbar'] = 'None'
    plt.style.use('dark_background')
    plt.ion()

    figure, ax = plt.subplots(nrows=2) #, figsize=(10, 8))
    
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    plt.tight_layout()

    ax[0].set_title("TEMPERATURE")
    #ax[0].set_xlabel("Time")
    ax[0].set_ylabel("Celcius")

    ax[1].set_title("HUMIDITY")
    #ax[1].set_xlabel("Time")
    ax[1].set_ylabel("%")

    while True:
        if rs.update():
            for id in rs.getIDs():
                if id not in myLines:
                    myLines[id] = ROOM(rs, id, ax)

                myLines[id].update()

            for a in ax:
                a.legend(loc='lower left', shadow=True)
                a.relim()
                a.autoscale_view()

            figure.canvas.draw()

        figure.canvas.flush_events()
        time.sleep(10)
