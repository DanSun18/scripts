#!/usr/bin/python
import matplotlib.pyplot as plt
import numpy as np
import sys
import helpers
import re #for splitting with multiple delimiters
import BinAnalysis


##################################data structure
datas = {} 
##################################helpers
def getNameOfFileStoringTimeOfFrequencyChange(binFileName):
	#remove ".bin" at the end
	commonPrefix = binFileName[:-4]
	print "Common prefix is ", commonPrefix
	#append "_frequencyChangeTime.txt" at the resulting string
	nameOfFileStoringTimeOfFrequencyChange = commonPrefix + "_frequencyChangeTime.txt"
	print "Name of file storing frequency change is ", nameOfFileStoringTimeOfFrequencyChange
	return nameOfFileStoringTimeOfFrequencyChange

def getTimeOfFrequencyChangeFromFile(nameOfFileStoringTimeOfFrequencyChange):
	timeString = "";
	timeInt = -1;
	with open(nameOfFileStoringTimeOfFrequencyChange, 'r') as timeFile:
		timeString = timeFile.readline();
		print "frequency changed at (string)", timeString
	timeInt = int(timeString);
	print "frequency changed at (int)", timeInt
	return timeInt

def getTimeOfFrequencyChange(binFileName):
	nameOfFileStoringTimeOfFrequencyChange = getNameOfFileStoringTimeOfFrequencyChange(binFileName)
	timeOfFrequencyChange = getTimeOfFrequencyChangeFromFile(nameOfFileStoringTimeOfFrequencyChange)
	timeOfFrequencyChange = timeOfFrequencyChange * 1e9 #convert from s to ns
	print "frequency changed at (ns)", timeOfFrequencyChange
	return timeOfFrequencyChange

def addTimeOfFrequencyChangeAsVerticalLineOnAxis(ax, timeOfFrequencyChange):
	ax.axvline(x=timeOfFrequencyChange, color='k', linestyle='--')

def plotLatencyVsId(latencyList, idList, inputFile):
	#plotting
	fig,ax = plt.subplots()
	linesNumber = 0

	ax.plot(idList,latencyList,helpers.getBuiltInColor(linesNumber))
	fig.suptitle('Latency vs Id')
	ax.set_xlabel('Id')
	ax.set_ylabel('Latency')
	# addTimeOfFrequencyChangeAsVerticalLineOnAxis(ax, timeOfFrequencyChange)
	# if x_limit > 0:
		# ax.set_xlim([0, x_limit])

	# ax.set_ylim([0 , percentile])
	# plt.legend()

	if save:
		figureFilePath = helpers.getDir(inputFile)+'latencyVsId.jpg'
		print 'Saving plot to ' + figureFilePath
		fig.savefig(figureFilePath, dpi=1200)
	else:
		plt.show()
		plt.close(fig)

def plotServiceTimeVsStartTime(ServiceList, startList, inputFile, timeOfFrequencyChange):
	#plotting
	fig,ax = plt.subplots()
	linesNumber = 0

	ax.plot(startList,ServiceList,helpers.getBuiltInColor(linesNumber))
	fig.suptitle('Service Time vs Service Start Time')
	ax.set_xlabel('Service Start Time')
	ax.set_ylabel('Service Time')
	addTimeOfFrequencyChangeAsVerticalLineOnAxis(ax, timeOfFrequencyChange)
	# if x_limit > 0:
		# ax.set_xlim([0, x_limit])

	# ax.set_ylim([0 , percentile])
	# plt.legend()

	if save:
		figureFilePath = helpers.getDir(inputFile)+'serviceVsStart.jpg'
		print 'Saving plot to ' + figureFilePath
		fig.savefig(figureFilePath, dpi=1200)
	else:
		plt.show()
		plt.close(fig)
###################################### main function
bin_analysis = BinAnalysis.BinAnalysis()

#configurable 
percentile = 1
x_limit = -1
exclude_percentage = 0
save = False
figureFilePath = ''
# respond to command line arguments
if '-h' in sys.argv:
	print '--percentile=percentile'
	print '--x_limit=xlimit'
	print '--exclude=front_portion_of_data'
	exit()
suppliedArguments = list(sys.argv)
for argument in suppliedArguments:
	if '--percentile=' in argument:
		percentile = float((argument.strip().split('='))[1])
		print 'Plotting up to ' + str(percentile) + " percentile"

	if '--x_limit=' in argument:
		x_limit = float((argument.strip().split('='))[1])
		print 'Plotting with x_limit set to ' + str(x_limit)

	if '--exclude=' in argument:
		exclude_percentage = float((argument.strip().split('='))[1])
		print 'excluding the first ' + str(exclude_percentage*100)+"% data"

	if '--save' in argument:
		save = True
		sys.argv.remove('--save')
		# figureFilePath = helpers.getDir(input_file)+'latency_distribution.jpg'
		# print 'Saving plot to ' + figureFilePath

# actual parsing

for input_file in sys.argv[1:]:
	binFile = input_file
	# thread, qps = findThreadsAndQPS(input_file)
	# addThreadIntoDataIfNotAlreadyExist(thread)
	bin_analysis.readBinFile(binFile)
	#get time of frequency change from another file
	timeOfFrequencyChange = getTimeOfFrequencyChange(binFile);
	# Get necessary data
	latencyList = bin_analysis.getList('latency')
	idList = bin_analysis.getList('id')
	serviceStartList = bin_analysis.getList('service_start_time')
	serviceTimeList = bin_analysis.getList('service_time')
	#plot
	plotLatencyVsId(latencyList, idList, binFile)
	plotServiceTimeVsStartTime(serviceTimeList, serviceStartList, binFile, timeOfFrequencyChange)

	#clear, get ready for next parse
	bin_analysis.clearData()




###############################################################