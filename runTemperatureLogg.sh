#!/usr/bin/bash

binDir="/home/pi/PROJECTS/temperatureLogg"
logDir=$binDir

mkdir -p $logDir

$binDir/main.py > $logDir/runLog.txt 2>&1
