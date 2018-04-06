#!/usr/bin/python

import helpers
import sys
import matplotlib.pyplot as plt
import os.path
import OFFSET
import re
import subprocess
from scipy import stats
#options: -s: save figure; -g: run get_aggregate_data.py
#arguments: trialfolder (xvar)

save = False
run_get_aggregate = False
xvars = ['sL3MISSls', 'hiL3CLKls', 'skt1READ', 'skt1WRITE']
# parse if save figure or view
if '-s' in sys.argv:
	save = True
	sys.argv.remove('-s')
#parse if need to run get aggregate
if '-g' in sys.argv:
	run_get_aggregate = True
	sys.argv.remove('-g')

trialFolder = str(sys.argv[1])
if len(sys.argv) > 2 and sys.argv[2] in xvars:
	xvars = [ sys.argv[2] ] #parse if user wants to plot anything in particular
#confirm both trial and base folder exists
if not os.path.isdir(trialFolder):
	helpers.pErr('Folder' + trialFolder +' does not exist', 1)
if 'q' in trialFolder:
	qpsStr = (re.split('q|k|f',trialFolder))[1]
baseFolder = 'q'+qpsStr+'base'
if not os.path.isdir(baseFolder):
	helpers.pErr('Base folder ' + baseFolder + ' does not exist', 1)

#get spark start time from time file in trial folder
timeFile = trialFolder +'/' + trialFolder+'.time'
if not os.path.isfile(timeFile):
	helpers.pErr('File ' + timeFile + ' does not exist' , 1)
#find spark starting time
sparkStartingTime = helpers.getSparkTime(timeFile)
if not sparkStartingTime > 0:
	helpers.pErr('Spark starting time not recorded in file ' + timeFile, 2)

#check to see if user wants to run get aggregate
scriptDir = helpers.getDir(sys.argv[0])
if run_get_aggregate:
	print 'Running get_aggregate_data_from_csv.py'
	csvFile = trialFolder+'/'+trialFolder+'.csv'
	if not subprocess.call([scriptDir + 'get_aggregate_data_from_csv.py', csvFile]) == 0:
		helpers.pErr('Unable to get aggregate data from csv file')
#check to see if aggregate data exist, if not, run script to obtain it
aggFile = trialFolder+'/'+trialFolder+'.agg'
if not os.path.isfile(aggFile):
	helpers.pWarn('No aggregate data file exists, running script to obtain from csv file')
	csvFile = trialFolder+'/'+trialFolder+'.csv'
	if not subprocess.call([scriptDir + 'get_aggregate_data_from_csv.py', csvFile]) == 0:
		helpers.pErr('Unable to get aggregate data from csv file')

print 'Reading all lines from aggregate data file'
aggFd = open(aggFile,'r')
aggLines = aggFd.readlines()
aggDatas = []
#pre-process for ease of using later
for aggline in aggLines:
	aggDatas.append(aggline.strip().split())
	aggLines.remove(aggline)




#read through trial bin file and record
#dict to record: ID, service time, corresponding L3CLK and L3MISS
#if server processing happens in one interval

#bascially I could calcualte end time based on service start time and service time
#if out of collection interval, ignore it


#two dict: preSpark and postSpark
preSparkTime = {} #match id to dict
postSparkTime = {}
firstReqGenTime = -1
trialBin = trialFolder + '/' + trialFolder +'.bin'
aggLineNum = 0 #always correspond to higher bound
interval_lower_bound = 0
interval_higher_bound = float(aggDatas[0][OFFSET.AGG['elapsed']])
print 'Reading from trial bin file and matching with aggregate data'
with open (trialBin, 'r') as f:
	
	while True:
		line = f.readline()
		if line == '': #EOF
			break
		data = line.strip().split()
		rid = int(data[OFFSET.BIN['id']])
		rgen = int(data[OFFSET.BIN['generation']])
		rsvc = int(data[OFFSET.BIN['service']])
		rltc = int(data[OFFSET.BIN['latency']])
		rsvcStart = int(data[OFFSET.BIN['svcStart']])
		if firstReqGenTime < 0:
			firstReqGenTime = rgen
		rsvcStartSinceFirstGen = rsvcStart - firstReqGenTime
		assert rsvcStartSinceFirstGen > 0
		rsvcFinishSinceFirstGen = rsvcStartSinceFirstGen + rsvc
		#find interval that contains start time
		#check if interval also contains end time
		#if not, ignore
		#if so, add data to corresponding dictionary
		# print 'Matching request ' + str(rid)
		# print rsvcStartSinceFirstGen
		# print interval_lower_bound
		while rsvcStartSinceFirstGen >= interval_higher_bound:
			aggLineNum = aggLineNum + 1
			interval_lower_bound = interval_higher_bound
			try:
				interval_higher_bound = float(aggDatas[aggLineNum][OFFSET.AGG['elapsed']])
			except IndexError:
				break
		while rsvcStartSinceFirstGen < interval_lower_bound:
			aggLineNum = aggLineNum - 1
			interval_higher_bound = interval_lower_bound
			if aggLineNum > 0:
				interval_lower_bound = float(aggDatas[aggLineNum - 1][OFFSET.AGG['elapsed']])
			else:
				interval_lower_bound = 0
		if rsvcFinishSinceFirstGen > interval_higher_bound :
			continue
		valueDict = {}
		valueDict['service'] = rsvc
		for xvar in xvars:
			xvarValue = float(aggDatas[aggLineNum][OFFSET.AGG[xvar]])
			valueDict[xvar] = xvarValue
		if rgen >= sparkStartingTime:
			assert rid not in postSparkTime		
			postSparkTime[rid] = valueDict
		else:
			assert rid not in preSparkTime
			preSparkTime[rid] = valueDict

# preSparkIds = []
preSparkSvcDiffs = []
preSparkAggDatas = {}

# postSparkIds = []
postSparkSvcDiffs = []
postSparkAggDatas = {}

#create empty lists for dictionary
for xvar in xvars:
	preSparkAggDatas[xvar] = []
	postSparkAggDatas[xvar] = []


#read through base file
#get service time, calculate difference, append 
#also append aggregate data the user seeks

baseBin = baseFolder + '/' + baseFolder + '.bin'
print 'Reading from base bin file'
with open (baseBin,'r') as f:
	while True:
		line = f.readline()
		if line == '':
			break
		data = line.strip().split()
		rid = int(data[OFFSET.BIN['id']])
		rsvc = int(data[OFFSET.BIN['service']])
		# rltc = int(data[OFFSET.BIN['latency']])

		if rid in preSparkTime:
			# preSparkIds.append(rid)
			svcDiff = preSparkTime[rid]['service'] - rsvc
			preSparkSvcDiffs.append(svcDiff)
			for xvar in xvars:
				xvarValue = preSparkTime[rid][xvar]
				preSparkAggDatas[xvar].append(xvarValue)
			del preSparkTime[rid]
		elif rid in postSparkTime:
			# postSparkIds.append(rid)
			svcDiff = postSparkTime[rid]['service'] - rsvc
			postSparkSvcDiffs.append(svcDiff)
			for xvar in xvars:
				xvarValue = postSparkTime[rid][xvar]
				postSparkAggDatas[xvar].append(xvarValue)
			del postSparkTime[rid]
		if len(preSparkTime) == 0 and len(postSparkTime) == 0:
			break

print 'Plotting service time diffrence against aggregate data'

for xvar in xvars:
	fig = plt.figure()
	fig.suptitle('Service Time Difference against ' + xvar, fontsize=16)
	ax1 = plt.subplot('211')
	ax1.set_title('Before sprak started',fontsize=12)
	plt.plot(preSparkAggDatas[xvar],preSparkSvcDiffs,'b.',label='svcDiff')
	ax1.set_xlabel(xvar, fontsize=12)
	ax1.set_ylabel('difference (ns)', fontsize=12)
	plt.axhline(y=0,color='k',linestyle='-')

	ax2 = plt.subplot('212')
	ax2.set_title('After sprak started',fontsize=12)
	ax2.plot(postSparkAggDatas[xvar],postSparkSvcDiffs,'r.',label='svcDiff')
	ax2.set_xlabel(xvar, fontsize=12)
	ax2.set_ylabel('difference (ns)', fontsize=12)
	plt.axhline(y=0,color='k',linestyle='-')

	fig.subplots_adjust(hspace=.4)

	# do linear regression
	slope, intercept, r_value, p_value, std_err = stats.linregress(postSparkAggDatas[xvar],postSparkSvcDiffs)
	leftEndx = min(postSparkAggDatas[xvar])
	rightEndx = max(postSparkAggDatas[xvar])
	leftEndy = leftEndx * slope + intercept
	rightEndy = rightEndx * slope + intercept
	ax2.plot([leftEndx, rightEndx], [leftEndy, rightEndy], 'k-', label = 'line of best fit')
	ax2.text(leftEndx, leftEndy, 'y = ' + str(slope) + ' * x + ' + str(intercept) + '\nr = ' + str(r_value), \
		fontsize=14)
	if save:
		path = trialFolder + '/' +'diff_against_' + xvar + '.jpg'
		print 'Saving plot to ' + path
		fig.savefig(path, dpi=1200)
		plt.close(fig)
	else:
		plt.show()
		plt.close(fig)







