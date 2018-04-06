#!/usr/bin/python
import BinAnalysis
import matplotlib.pyplot as plt
import sys
import helpers

# plot service time vs. memory bandwidth for
# all files passed in as arguments

bin_analysis = BinAnalysis.BinAnalysis()

fig,ax = plt.subplots()
data_file_number = 0

bin_file = sys.argv[1]
bin_analysis.readBinFile(bin_file)
line_color = helpers.getBuiltInColor(data_file_number)
bin_analysis.plotDataVsMemoryBandWidth(axis=ax, yvar_name='service_time', line_style=('b' + '.'), 
		do_linear_regression=False, convertToGBytes=True, convertToMs=True)
ax.set_xlabel('Memory Bandwidth (GB/s)')
ax.set_ylabel('Service Time (ms)')
bin_analysis.clearData()
data_file_number += 1

#stored in the folder of the last processeed file
dir_path = helpers.getDir(bin_file)
file_name = helpers.getFileName(bin_file)
save_pic_path =  dir_path + file_name + 'service_time_vs_MBW.jpg'
fig.savefig(save_pic_path, dpi=1200)
plt.close(fig)