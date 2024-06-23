#!/usr/bin/python3

import signal
import sys
import pprint
import time
import matplotlib.pyplot as plt

import t_read

rs = t_read.READ_SENSORS()

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    rs.writeLogFile()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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
            name = self.rs.getName(self.id)

            self.lineTemp, = ax[0].plot(xT, yT, label=name, **{'marker': 'o'})
            if yH != None:
                self.lineHumi, = ax[1].plot(xH, yH, label=name, **{'marker': 'o'})

            self.firstTime = False

        else:
            self.lineTemp.set_xdata(xT)
            self.lineTemp.set_ydata(yT)
            if yH != None:
                self.lineHumi.set_xdata(xH)
                self.lineHumi.set_ydata(yH)

if __name__ == "__main__":

    myLines = {}
    plt.ion()
    
    figure, ax = plt.subplots(nrows=2, figsize=(10, 8))
    
    ax[0].set_title("TEMPERATURE")
    ax[0].set_xlabel("Time")
    ax[0].set_ylabel("Celcius")

    ax[1].set_title("HUMIDITY")
    ax[1].set_xlabel("Time")
    ax[1].set_ylabel("%")

    while True:
        if rs.update():
            for id in rs.getIDs():
                if id not in myLines:
                    myLines[id] = ROOM(rs, id, ax)

                myLines[id].update()

            for a in ax:
                a.legend()
            figure.canvas.draw()

        figure.canvas.flush_events()
        time.sleep(1)
