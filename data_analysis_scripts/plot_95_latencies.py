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
def findThreadsAndQPS(filename):
	actualFileName = filename.strip().split('/')[-1]
	# print actualFileName
	delimiters = 'q', 't', '.'
	regexPattern = '|'.join(map(re.escape, delimiters))
	# print regexPattern
	splitted = re.split(regexPattern, actualFileName)
	# print splitted
	thread = splitted[1]
	qps = splitted[2]
	# print "Thread: ",thread
	# print "Qps: ",qps
	return (thread,qps)
def addThreadIntoDataIfNotAlreadyExist(thread):
	if thread not in datas:
		datas[thread] = {}
		datas[thread]['qps'] = []
		datas[thread]['95thLatency'] = []
def rearrangeByQps(originalQps, originalLatency, sortedQps, sortedLatency):
	while not len(originalQps) == 0:
		minimumQps = min(originalQps)
		index = originalQps.index(minimumQps)	
		correspondingLatency = originalLatency[index]
		originalQps.remove(minimumQps)
		originalLatency.remove(correspondingLatency)
		sortedQps.append(minimumQps)
		sortedLatency.append(correspondingLatency)	
######################################
saving = False
if '-s' in sys.argv:
	saving = True
	sys.argv.remove('-s')

trial = sys.argv[1]
binPath = trial + '/' + trial + '.bin'
interval = 50e6 #50ms, converting to ns

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
		figureFilePath = helpers.getDir(input_file)+'latency_distribution.jpg'
		print 'Saving plot to ' + figureFilePath

# actual parsing

for input_file in sys.argv[1:]:

	thread, qps = findThreadsAndQPS(input_file)
	addThreadIntoDataIfNotAlreadyExist(thread)
	bin_analysis.readBinFile(input_file)

	sorted_latency_array = np.sort(bin_analysis.getList('latency'))
	sorted_latency_list = list(sorted_latency_array)

	caring_data_from_id = int(len(sorted_latency_list) * exclude_percentage)
	sorted_latency_list = sorted_latency_list[caring_data_from_id:]

	Latency95th = helpers.get95th(sorted_latency_list)
	datas[thread]['qps'].append(int(qps))
	datas[thread]['95thLatency'].append(Latency95th)
	# print datas[thread]

	bin_analysis.clearData()

fig,ax = plt.subplots()
linesNumber = 0

for thread in datas:
	qpsList = datas[thread]['qps']
	Latency95thList = datas[thread]['95thLatency']
	# print qpsList
	# print Latency95thList
	sortedQpsList = []
	sortedLatencyList = []
	rearrangeByQps(qpsList, Latency95thList, sortedQpsList, sortedLatencyList)
	print sortedQpsList
	print sortedLatencyList
	ax.plot(sortedQpsList,sortedLatencyList,helpers.getBuiltInColor(linesNumber),label='Thread='+thread)
	linesNumber += 1

fig.suptitle('95-th Percentile Latency vs. QPS')
ax.set_xlabel('QPS')
ax.set_ylabel('Latency (ms)')

if x_limit > 0:
	ax.set_xlim([0, x_limit])

# ax.set_ylim([0 , percentile])
plt.legend()

if save:
	fig.savefig(figureFilePath, dpi=1200)
else:
	plt.show()
	plt.close(fig)


###############################################################