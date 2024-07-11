#!/usr/bin/bash

logDir="/var/log/temperatureLogg"

mkdir -p $logDir

/home/pi/PROJECTS/temperatureLogg/main.py > $logDir/runLog.txt 2>&1
