#!/usr/bin/python

import matplotlib.pyplot as plt
import sys
import csv 
import subprocess
import os.path

import helpers



#creates plot that shows aggregated Cpu and socket parameters
#also creates file suitable for future comparison
#argumets:  csvfile

toPlot = False
if '-p' in sys.argv:
	toPlot = True
	sys.argv.remove('-p')


if len(sys.argv) < 2:
	print "please provide csv file"
	exit(1)

csvFile = str(sys.argv[1])


if csvFile.endswith('.csv'):
	noSuffix = csvFile[:-4]
else:
	noSuffix = csvFile
	csvFile = csvFile + '.csv'

if not os.path.isfile(csvFile):
	helpers.pErr("Input csv file does not exist")

scriptDir = helpers.getDir(sys.argv[0])
if not os.path.isfile(csvFile + '.correctionLog'):
	helpers.pWarn('csv correction log does not exist, running correction script')
	if not subprocess.call([scriptDir + 'correct_csv.py', csvFile]) == 0:
		helpers.pErr('Unable to correct csv file')

setupFile = noSuffix + '.setup'

if not os.path.isfile(setupFile):
	print "Cannot find setup file " + setupFile
	exit(1)

helpers.readSetup(setupFile)

lsa_cores =  helpers.getCores(helpers.params['SERVERCORES'])
ba_cores = []
if 'SPARKCORES' in helpers.params:
	ba_cores = helpers.getCores(helpers.params['SPARKCORES'])

core_start_column = [0] * helpers.NUMCORE
core_start_column[0] = helpers.getColNum("CF")
socket1_read_column = helpers.getColNum('BG')
socket1_write_column = helpers.getColNum('BH')

for i in range(1,helpers.NUMCORE):
	core_start_column[i] = core_start_column[i-1] + helpers.COL_PER_CORE

eTime = [] #elapsed time since moses finished warm up 
aIPCls = [] #average IPC for lsa
sL3MISSls = [] #sum of L3MISS for lsa
hiL3CLKls = [] #highest reading of L3CLK for lsa

if len(ba_cores) > 0:
	sL3MISSb = [] #sum of L3MISS for batch
	sL3ACCb = [] #sum of L3 Access for batch

skt1WRITE = []
skt1READ = []


#get first request generation time from bin file
with open(noSuffix+'.bin', 'r') as f:
	lines = f.readlines()
	firstRequestGenTime = float((lines[0].split())[1])
	lastRequestFinTime = float((lines[-1].split())[1]) + float((lines[-1].split())[4])
# print 'first request generated at' + str(firstRequestGenTime)
# print 'last request finished at ' + str(lastRequestFinTime)

dataRaw = {}
for core in lsa_cores:
	dataRaw[core] = {}
	dataRaw[core]['IPC'] = []
	dataRaw[core]['L3MISS'] = []
	dataRaw[core]['L3CLK'] = []
for core in ba_cores:
	dataRaw[core] = {}
	dataRaw[core]['L3MISS'] = []
	dataRaw[core]['L3ACC'] = []

print 'Reading data from csv file'
lineN = 0
warmupLines = 2
breakOnNextRun=False
with open(csvFile, 'rb') as csvfile:
	dataReader = csv.reader(csvfile, delimiter=';')
	for row in dataReader:
		if breakOnNextRun:
			break
		lineN +=1

		if lineN <= warmupLines: #ignore the first two rows
			continue

		dataTime = helpers.getCsvTime(row[0], row[1])
		# print dataTime
		if dataTime < firstRequestGenTime:
			continue
		if dataTime > lastRequestFinTime:
			breakOnNextRun = True
		elapsedTime = dataTime - firstRequestGenTime
		# print '\t' + str(elapsedTime)
		if len(eTime) > 0:
			try:
				assert elapsedTime > eTime[-1]
			except AssertionError:
				print "Assertion Error: elapsed time is smaller than previous elapsed time"
				print '\t' + str(row)
				print 'is translated to ' + str(elapsedTime) +', where as prvious one is ' + str(eTime[-1])
				exit(1)
		eTime.append(elapsedTime)
		socket1READ = float(row[socket1_read_column])
		socket1WRITE = float(row[socket1_write_column])
		skt1READ.append(socket1READ)
		skt1WRITE.append(socket1WRITE)
		for core in lsa_cores:
			cIPC = float(row[core_start_column[core] + helpers.CDISP['IPC'] ])
			cL3MISS = float(row[core_start_column[core] + helpers.CDISP['L3MISS'] ])
			cL3CLK = float(row[core_start_column[core] + helpers.CDISP['L3CLK'] ])
			dataRaw[core]['IPC'].append(cIPC)
			dataRaw[core]['L3MISS'].append(cL3MISS)
			dataRaw[core]['L3CLK'].append(cL3CLK)
		for core in ba_cores:
			cL3MISS = float(row[core_start_column[core] + helpers.CDISP['L3MISS'] ])
			cL3HIT = float(row[core_start_column[core] + helpers.CDISP['L3HIT'] ])
			cL3ACC = cL3MISS/(1-cL3HIT)
			dataRaw[core]['L3MISS'].append(cL3MISS)
			dataRaw[core]['L3ACC'].append(cL3ACC)

#remove mega thread
lowestCoreIPC = 10
metaThreadCore = -1
for core in lsa_cores:
	average_core_IPC = sum(dataRaw[core]['IPC'])/len(dataRaw[core]['IPC'])
	if average_core_IPC < lowestCoreIPC:
		lowestCoreIPC = average_core_IPC
		metaThreadCore = core
lsa_cores.remove(metaThreadCore)
del dataRaw[metaThreadCore]


#compute aggregate data and also write to a file
print "Processing data and writing to file"
outFile = open(noSuffix + '.agg','w')
for i in range(0,len(eTime)):
	server_IPC_sum = 0
	server_L3MISS_sum = 0
	server_L3CLK_high = 0
	for core in lsa_cores:
		server_IPC_sum += dataRaw[core]['IPC'][i]
		server_L3MISS_sum += dataRaw[core]['L3MISS'][i]
		if dataRaw[core]['L3CLK'][i] > server_L3CLK_high:
			server_L3CLK_high = dataRaw[core]['L3CLK'][i]
	server_IPC_average = server_IPC_sum / len(lsa_cores)
	aIPCls.append(server_IPC_average)
	sL3MISSls.append(server_L3MISS_sum)
	hiL3CLKls.append(server_L3CLK_high)

	if len(ba_cores) > 0:
		batch_L3MISS_sum = 0
		batch_L3ACC_sum = 0
		for core in ba_cores:
			batch_L3MISS_sum += dataRaw[core]['L3MISS'][i]
			batch_L3ACC_sum += dataRaw[core]['L3ACC'][i]
		sL3MISSb.append(batch_L3MISS_sum)
		sL3ACCb.append(batch_L3ACC_sum)

	outFile.write(str(eTime[i]) + ' ' + str(server_IPC_average) + ' ' + str(server_L3MISS_sum) + ' ' + str(server_L3CLK_high))
	if len(ba_cores) > 0:
		outFile.write(' ' + str(batch_L3MISS_sum) + ' ' + str(batch_L3ACC_sum))
	else:
		outFile.write(' ' + str(-1) + ' ' + str(-1) ) #place holder
	outFile.write(' ' + str(skt1READ[i]) + ' ' + str(skt1WRITE[i]))
	outFile.write('\n')
outFile.close()


trialFolder = helpers.getDir(csvFile)

if toPlot:
	print 'Plotting aggregate data vs time'
	plt.suptitle('Server Average IPC vs Time')
	plt.plot(eTime, aIPCls)
	plt.savefig(trialFolder + 'aIPC_vs_time.jpg', dpi=1200 )
	plt.close()

	plt.suptitle('Server L3Miss sum vs Time')
	plt.plot(eTime, sL3MISSls)
	plt.savefig(trialFolder + 'L3Missls_vs_time.jpg', dpi=1200 )
	plt.close()

	plt.suptitle('Server core highest L3CLK vs Time')
	plt.plot(eTime, hiL3CLKls)
	plt.savefig(trialFolder + 'L3CLKls_vs_time.jpg', dpi=1200 )
	plt.close()

	if len(ba_cores) > 0:
		plt.suptitle('Batch L3Miss sum vs Time')
		plt.plot(eTime, sL3MISSb)
		plt.savefig(trialFolder + 'L3Missb_vs_time.jpg',dpi=1200 )
		plt.close()

		plt.suptitle('Batch L3Access sum vs Time')
		plt.plot(eTime, sL3ACCb)
		plt.savefig(trialFolder + 'L3Accessb_vs_time.jpg',dpi=1200 )
		plt.close()

	plt.suptitle('SOCKET1 READ vs Time')
	plt.plot(eTime, skt1READ)
	plt.savefig(trialFolder + 'SKT1READ_vs_time.jpg', dpi=1200 )
	plt.close()

	plt.suptitle('SOCKET1 WRITE vs Time')
	plt.plot(eTime, skt1WRITE)
	plt.savefig(trialFolder + 'SKT1WRITE_vs_time.jpg', dpi=1200 )
	plt.close()
