#!/usr/bin/python3

import subprocess
import pprint
from datetime import datetime
from datetime import timedelta
from pathlib import Path
import yaml
import re

class READ_SENSORS():

    def __init__(self):

        self.cmd = ["/usr/bin/tdtool", "--list"]
        self.logFilename = '/home/pi/PROJECTS/temperatureLogg/temperature_log.yml'

        self.deviceNames = {
            107: None,
            123: None,
            199: 'Köket',
            215: 'Filips rum',
            231: 'MPs rum',
            247: 'Teos rum',
            255: None, # 'Unknown',
        }

        self.deviceFeatures = {
            199: ['temp', 'humidity'],
            215: ['temp', 'humidity'],
            231: ['temp', 'humidity'],
            247: ['temp', 'humidity'],
            255: ['temp'],
        }

        self.lastReading = {}
        self.readLogFile()

        self.timeLastFileStorage = datetime.now()

    def getFeatures(self, id):
        if id in self.deviceFeatures:
            features = self.deviceFeatures[id]
        else: # If new sensor, at least temperature is expected
            features = ['temp']
        return features

    def readLogFile(self):
        try:
            oldLog = yaml.safe_load(Path(self.logFilename).read_text())
            if oldLog == None:
                oldLog = {}
            print("Read: {}".format(self.logFilename))

        except:
            print("No historical data found")
            self.datalog = {}
            return

        self.datalog = oldLog


    def writeLogFile(self):
        self.cleanupLog()

        with open(self.logFilename, 'w') as outfile:
            yaml.dump(self.datalog, outfile, default_flow_style=False)
        print("Wrote: {}".format(self.logFilename))


    def readSensors(self):

        # TODO: Why /dev/null ??!
        res = subprocess.run(["/usr/bin/tdtool", "--list", "/dev/null"], capture_output=True, text=True)

        for l in res.stdout.split('\n'):
            lSplit = l.split()

            # Skip headers and stuff
            if len(lSplit) < 5: 
                continue

            # Extract values and only keep correct "model"
            #protocol = lSplit[0]
            model = lSplit[1]
            if model != "temperaturehumidity":
                continue
            idRaw = lSplit[2]
            tempRaw = lSplit[3]
            humidityRaw = lSplit[4]
            #rainRaw = lSplit[5]
            #windRaw = lSplit[6]
            dateRaw = lSplit[-2] # 7
            timeRaw = lSplit[-1] # 8

            # Add data to struct
            id = int(idRaw)
            self.lastReading[id] = {}

            # Get timestamp
            date_obj = datetime.strptime(dateRaw, '%Y-%m-%d').date()
            time_obj = datetime.strptime(timeRaw, '%H:%M:%S').time()
            datetime_obj = datetime.combine(date_obj, time_obj)
            self.lastReading[id]['datetime'] = datetime_obj

            # Get temperature
            try:
                temp = float(re.sub('[^\d\.]', '', tempRaw))
            except:
                print("Failed converting temperature: {}".format(tempRaw))
                temp = "NA"
            self.lastReading[id]['temp'] = temp

            # Get humidity
            try:
                humidity = int(re.sub('[^\d\.]', '', humidityRaw))
            except:
                print("Failed converting humidity: {}".format(humidityRaw))
                humidity = "NA"
            self.lastReading[id]['humidity'] = humidity


    def addToLog(self):
        updated = False

        for id, newData in self.lastReading.items():

            # Create new entry for ID if needed
            if id not in self.datalog:
                self.datalog[id] = {}
                self.datalog[id]['datetime'] = []
                for feat in self.getFeatures(id):
                    self.datalog[id][feat] = []

            # Only update if timestamp has changed
            updateLogItem = True
            if len(self.datalog[id]['datetime']) > 0:
                lastTS = self.datalog[id]['datetime'][-1]
                if lastTS == newData['datetime']:
                    updateLogItem = False

            if not updateLogItem:
                continue

            # Only update timestamp if same numbers
            addNewValues = False
            for feat in self.getFeatures(id):
                if len(self.datalog[id][feat]) == 0:
                    addNewValues = True
                    break
                if self.datalog[id][feat][-1] != newData[feat]:
                    addNewValues = True
                    break

            # Do the update
            if addNewValues:
                self.datalog[id]['datetime'].append( newData['datetime'] )
                for feat in self.getFeatures(id):
                    self.datalog[id][feat].append( newData[feat] )
            else:
                self.datalog[id]['datetime'][-1] = newData['datetime']

            updated = True
            print("ID:{}, T:{}, H:{} Time:{}".format(id, newData['temp'], newData['humidity'], newData['datetime']))

        return updated


    def update(self):
        self.readSensors()
        isUpdated = self.addToLog()

        if isUpdated:
            now = datetime.now()
            if now > self.timeLastFileStorage + timedelta(hours=1):
                self.writeLogFile()
                self.timeLastFileStorage = now

        return isUpdated

    def cleanupLog(self):
        newDict = {}

        maxArrayLength = 10000 # 69 days if every 10th minute
        # Limit samplerate to 10 min
        for id, idDict in self.datalog.items():
            # Create a copy
            newIdDict = {}
            newIdDict['datetime'] = []
            for feat in self.getFeatures(id):
                newIdDict[feat] = []

            # Ignore any empty IDs
            if len(idDict['datetime']) == 0:
                continue

            # Force to add first iteraion
            lastTime = idDict['datetime'][-1] + timedelta(days=1)

            itemCnt = 0
            for idx, t in reversed(list(enumerate(idDict['datetime']))):

                if t < lastTime - timedelta(hours=0, minutes=10):
                    newIdDict['datetime'].insert(0, t)
                    for feat in self.getFeatures(id):
                        newIdDict[feat].insert(0, idDict[feat][idx])

                    lastTime = t

                    itemCnt += 1
                    if itemCnt > maxArrayLength:
                        break
            
            newDict[id] = newIdDict

        #pprint.pprint(newDict)
        self.datalog = newDict


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
        y = None
        if 'temp' in self.datalog[id]:
            y = list(self.datalog[id]['temp'])
        return x,y

    def getHumidity(self, id):
        x = list(self.datalog[id]['datetime'])
        y = None
        if 'humidity' in self.datalog[id]:
            y = list(self.datalog[id]['humidity'])
        return x,y
    

if __name__ == "__main__":
    o = READ_SENSORS()

    o.readSensors()
    o.addToLog()
    pprint.pprint(o.datalog)
