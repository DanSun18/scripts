#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import sys
import csv 

import os.path

import helpers





interestedTrace = ['EXEC', 'IPC', 'FREQ', 'AFREQ', 'L3MISS', 'L2MISS', 'L3HIT','L2HIT', 'L3CLK', 'L2CLK']

if len(sys.argv) < 3:
	helpers.pErr('Format: ' + sys.argv[0] + ' [ csvFile coreGroup ]',1)

csvFile = str(sys.argv[1])
CoreGroup = str(sys.argv[2])

trialName = ''

if csvFile.endswith('.csv'):
	trialName = csvFile[:-4]
else:
	trialName = csvFile
	csvFile = csvFile + '.csv'
#print trialName

if not os.path.isfile(csvFile):
	print "Input csv file does not exist"
	exit(1)

setupFile = trialName + '.setup'

if not os.path.isfile(setupFile):
	print "Cannot find setup file for trial " + setupFile
	exit(1)

helpers.readSetup(setupFile)
cores = helpers.getCores(helpers.params[CoreGroup])



core_start_column = [0] * helpers.NUMCORE
core_start_column[0] = helpers.getColNum("CF")

for i in range(1,helpers.NUMCORE):
	core_start_column[i] = core_start_column[i-1] + helpers.COL_PER_CORE

startTime = 0
endTime = -1


#If bin file exists
if os.path.isfile(trialName+'.bin'):
	firstRequestGenTime = -1
	lastRequestGenTime = -1
	with open(trialName+'.bin', 'r') as f:
		lines = f.readlines()
		firstRequestGenTime = float((lines[0].split())[1])
		lastRequestGenTime = float((lines[-1].split())[1])
	print 'first request generated at' + str(firstRequestGenTime)
	print 'last request generated at ' + str(lastRequestGenTime)
	startTime = firstRequestGenTime
	endTime = lastRequestGenTime
else:
	timeFile = trialName + '.time'
	if not os.path.isfile(timeFile):
		helpers.pErr('File ' + timeFile + ' does not exist' , 1)
	#find spark starting time
	sparkStartingTime = helpers.getSparkTime(timeFile)
	if not sparkStartingTime > 0:
		helpers.pErr('Spark starting time not recorded in file ' + timeFile, 2)
	startTime = sparkStartingTime

#initialize data dict
datas = {}
times = []
for core  in cores:
	datas[core] = {}
	for trace in interestedTrace:
		datas[core][trace] = []

print 'Reading data from csv file'
lineN = 0
warmupLines = 2
with open(csvFile, 'rb') as csvfile:
	dataReader = csv.reader(csvfile, delimiter=';')
	for row in dataReader:
		lineN +=1

		if lineN <= warmupLines: #ignore the first two rows
			continue

		dataTime = helpers.getCsvTime(row[0], row[1])
		# print dataTime
		if dataTime < startTime:
			continue
		if dataTime > endTime and endTime > startTime:
			break
		elapsedTime = dataTime - startTime
		times.append(elapsedTime)
		for core in cores:
			for trace in interestedTrace:
				data = float(row[core_start_column[core] + helpers.CDISP[trace] ])
				datas[core][trace].append(data)

print 'Plotting'

for core in cores:
	print 'Plotting core ' + str(core)
	for trace in interestedTrace:
		plt.suptitle('Core' + str(core) + ' ' + trace)
		plt.plot(times, datas[core][trace])
		plt.savefig(trialName+ '_core' + str(core) + '_' + trace + '.jpg', dpi=1200 )
		plt.close()