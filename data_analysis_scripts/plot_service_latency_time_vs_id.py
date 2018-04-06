#!/usr/bin/python
import BinAnalysis
import matplotlib.pyplot as plt
import sys
import helpers


bin_analysis = BinAnalysis.BinAnalysis()
# bin_files = helpers.parseWildCards(sys.argv[1])
# print bin_files

# for bin_file in bin_files:
for bin_file in sys.argv[1:]:
	bin_analysis.readBinFile(bin_file)
	fig,ax = plt.subplots()
	bin_analysis.plotData(ax, 'id', 'latency', 'r-', 'latency')
	bin_analysis.plotData(ax, 'id', 'service_time', 'g-', 'service time')
	ax.set_xlabel('request id')
	ax.set_ylabel('time (ns)')
	plt.legend()
	# file_path_without_extension = helpers.getRidOfLastFewCharacters(bin_file, 4)
	# save_pic_path =  file_path_without_extension + '_time_vs_id.jpg'
	# fig.savefig(save_pic_path, dpi=1200)
	# plt.close(fig)
	plt.show()
	plt.close(fig)
	bin_analysis.clearData()

