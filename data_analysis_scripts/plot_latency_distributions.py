#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import sys
import helpers
import BinAnalysis

bin_analysis = BinAnalysis.BinAnalysis()

fig,ax = plt.subplots()
data_file_number = 0

#configurable 
percentile = 1
x_limit = -1
exclude_percentage = 0
save = False
figureFilePath = ''
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

for input_file in sys.argv[1:]:
	bin_analysis.readBinFile(input_file)

	sorted_latency_array = np.sort(bin_analysis.getList('latency'))

	sorted_latency_list = list(sorted_latency_array)

	caring_data_from_id = int(len(sorted_latency_list) * exclude_percentage)
	sorted_latency_list = sorted_latency_list[caring_data_from_id:]


	yvals_array = np.arange(len(sorted_latency_list))/float(len(sorted_latency_list))
	yvals_list = list(yvals_array)
	file_name = input_file[len(helpers.getDir(input_file)):]

	ax.plot(sorted_latency_list,yvals_list,helpers.getBuiltInColor(data_file_number),label=file_name)
	bin_analysis.clearData()
	data_file_number += 1


fig.suptitle('Percentile vs. Latency')
ax.set_xlabel('latency (ns)')
ax.set_ylabel('percentile')
if x_limit > 0:
	ax.set_xlim([0, x_limit])
ax.set_ylim([0 , percentile])
plt.legend()

if save:

	fig.savefig(figureFilePath, dpi=1200)
else:
	plt.show()
	plt.close(fig)
