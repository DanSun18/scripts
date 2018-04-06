#!/usr/bin/python


# A very rough script that takes an input bin file
# and plot service time against sockeet level 
# read and write

import numpy as np
import matplotlib.pyplot as plt
import sys
import OFFSET




# input_file = str(sys.argv[1])

for input_file in sys.argv[1:]:

	file = open(input_file)



	svcTimes = []
	instrs = []
	sktReads = []
	sktWrites = []
	coreL3Misses = []
	coreL3HitRates = []

	print "Reading data from " + input_file

	with file:
		lines = file.readlines()
		for line in lines:
			times = line.split(' ')
			svcTime = int(times[OFFSET.BIN['service']])
			instr = int(times[OFFSET.BIN['instrRetired']])
			sktRead = int(times[OFFSET.BIN['sktRead']])
			sktWrite = int(times[OFFSET.BIN['sktWrite']])
			coreL3Miss = int(times[OFFSET.BIN['L3Miss']])
			coreL3HitRate = float(times[OFFSET.BIN['L3HitRate']])


			svcTimes.append(svcTime)
			instrs.append(instr)
			sktReads.append(sktRead)
			sktWrites.append(sktWrite)
			coreL3Misses.append(coreL3Miss)
			coreL3HitRates.append(coreL3HitRate * 100)

	file.close()

	print "Creating plots..."

	print "Creating service time vs instruction plot"
	fig,ax = plt.subplots()
	fig.suptitle('Service Time vs. instruction')
	ax.plot(instrs, svcTimes,'b.')
	ax.set_xlabel('number of instructions')
	ax.set_ylabel('service time (ms)')
	fig.savefig(input_file+'_service_vs_instrs.jpg', dpi=1200)
	plt.close(fig)


	print "Creating service time vs socket read plot"
	fig,ax = plt.subplots()
	fig.suptitle('Service Time vs. Socket Read')
	ax.plot(sktReads, svcTimes,'b.')
	ax.set_xlabel('socket read (bytes)')
	ax.set_ylabel('service time (ms)')
	fig.savefig(input_file+'_service_vs_sktRead.jpg', dpi=1200)
	plt.close(fig)

	print "Creating service time vs socket write plot"
	fig,ax = plt.subplots()
	fig.suptitle('Service Time vs. Socket Write')
	ax.plot(sktWrites, svcTimes,'b.')
	ax.set_xlabel('socket write (bytes)')
	ax.set_ylabel('service time (ms)')
	fig.savefig(input_file+'_service_vs_sktWrite.jpg', dpi=1200)
	plt.close(fig)

	print "Creating service time vs L3Miss plot"
	fig,ax = plt.subplots()
	fig.suptitle('Service Time vs. L3 Miss')
	ax.plot(coreL3Misses, svcTimes,'b.')
	ax.set_xlabel('L3Miss (bytes)')
	ax.set_ylabel('service time (ms)')
	fig.savefig(input_file+'_service_vs_L3Miss.jpg', dpi=1200)
	plt.close(fig)

	print "Creating service time vs L3Hit Rate plot"
	fig,ax = plt.subplots()
	fig.suptitle('Service Time vs. L3 Hit Rate')
	ax.plot(coreL3HitRates, svcTimes,'b.')
	ax.set_xlabel('L3 Hit Rate %')
	ax.set_ylabel('service time (ms)')
	fig.savefig(input_file+'_service_vs_L3HitRate.jpg', dpi=1200)
	plt.close(fig)
