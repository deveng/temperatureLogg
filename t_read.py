#!/usr/bin/python3

import subprocess
import pprint
from datetime import datetime
from pathlib import Path
import yaml
import re

class READ_SENSORS():

    def __init__(self):

        self.cmd = ["/usr/bin/tdtool", "--list"]
        self.logFilename = '/home/pi/PROJECTS/temperatureLogg/temperature_log.yml'

        self.deviceNames = {
            199: 'rum1',
            231: 'rum2',
            247: 'rum3',
            255: 'rum4',
            215: 'rum5',
        }

        self.deviceFeatures = {
            199: ['temp', 'humidity'],
            231: ['temp', 'humidity'],
            247: ['temp', 'humidity'],
            255: ['temp'],
            215: ['temp', 'humidity'],
        }

        self.lastReading = {}
        self.readLogFile()


    def readLogFile(self):
        try:
            oldLog = yaml.safe_load(Path(self.logFilename).read_text())
        except:
            print("No historical data found")
            self.datalog = {}
            return

        self.datalog = oldLog


    def writeLogFile(self):
        with open(self.logFilename, 'w') as outfile:
            yaml.dump(self.datalog, outfile, default_flow_style=False)
        print("Wrote: {}".format(self.logFilename))


    def readSensors(self):

        res = subprocess.run(["/usr/bin/tdtool", "--list", "/dev/null"], capture_output=True, text=True)

        for l in res.stdout.split('\n'):
            lSplit = l.split()

            if len(lSplit) > 4:

                if lSplit[1] == "temperaturehumidity":
                    id = int(lSplit[2])

                    # Translate ID to name/room
                    if id in self.deviceFeatures:
                        features = self.deviceFeatures[id]
                    else:
                        features = ['temp']

                    self.lastReading[id] = {}

                    # Get temperature
                    if 'temp' in features:
                        tempRaw = lSplit[3]
                        try:
                            temp = float(re.sub('[^\d\.]', '', tempRaw))
                        except:
                            print("Failed converting temperature: {}".format(tempRaw))
                            temp = 0
                        self.lastReading[id]['temp'] = temp
                    else:
                        self.lastReading[id]['temp'] = None

                    # Get humidity
                    if 'humidity' in features:
                        humidityRaw = lSplit[4]
                        try:
                            humidity = int(re.sub('[^\d\.]', '', humidityRaw))
                        except:
                            print("Failed converting humidity: {}".format(humidityRaw))
                            humidity = 0
                        self.lastReading[id]['humidity'] = humidity
                    else:
                        self.lastReading[id]['humidity'] = None

                    # Get timestamp
                    dateRaw = lSplit[-2]
                    timeRaw = lSplit[-1]
                    date_obj = datetime.strptime(dateRaw, '%Y-%m-%d').date()
                    time_obj = datetime.strptime(timeRaw, '%H:%M:%S').time()
                    datetime_obj = datetime.combine(date_obj, time_obj)

                    self.lastReading[id]['datetime'] = datetime_obj



    def addToLog(self):
        updated = False

        for id, newData in self.lastReading.items():

            updateLogItem = True
            if id not in self.datalog:
                self.datalog[id] = {}
                self.datalog[id]['temp'] = []
                self.datalog[id]['humidity'] = []
                self.datalog[id]['datetime'] = []
            else:
                lastTS = self.datalog[id]['datetime'][-1]
                if newData['datetime'] <= lastTS:
                    updateLogItem = False

            if updateLogItem:
                self.datalog[id]['temp'].append( newData['temp'] )
                self.datalog[id]['humidity'].append( newData['humidity'] )
                self.datalog[id]['datetime'].append( newData['datetime'] )
                updated = True

        return updated


    def update(self):
        self.readSensors()
        return self.addToLog()


    def getName(self, id):
        # Translate ID to name/room
        if id in self.deviceNames:
            name = self.deviceNames[id]
        else:
            name = str(id)
        return name

    def getIDs(self):
        return list(self.datalog.keys())

    def getTemp(self, id):
        x = list(self.datalog[id]['datetime'])
        y = list(self.datalog[id]['temp'])
        if None in y:
            y = None
        return x,y


    def getHumidity(self, id):
        x = list(self.datalog[id]['datetime'])
        y = list(self.datalog[id]['humidity'])
        if None in y:
            y = None
        return x,y
    

if __name__ == "__main__":
    o = READ_SENSORS()

    o.readSensors()
    o.addToLog()
    pprint.pprint(o.datalog)
