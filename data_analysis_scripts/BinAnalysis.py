#!/usr/bin/python
import matplotlib.pyplot as plt
from scipy import stats

class BinAnalysis:

	def __init__(self):
# deprecated because now will try to match column number with data automatically
	# 	self.BIN_TYPE_TO_COLUMN_NUMBER = {
	# 	'id' : 0,
	# 	'generation_time' : 1,
	# 	'queue_time' : 2,
	# 	'service_time' : 3,
	# 	'latency' : 4,
	# 	'service_start_time' : 5,
	# 	'instr_retired' : 6,
	# 	'socket_read' : 7,
	# 	'socket_write' : 8,
	# 	'L3_miss_number' : 9,
	# 	'L3_hit_rate' : 10,
	# 	'time_on_server' : 11,
	# 	'time_request_arrived_on_server' : 12,
	# 	'worker_thread_core_id' : 13,
	# 	'L3_occupancy' : 14
	# }
		self.BIN_COLUMN_HEADERS = ['id', 'generation_time', 'queue_time', 
		'service_time', 'latency', 'service_start_time', 'queue_length' ]
		self.BIN_COLUMN_NUMBER_TO_DATA = {}
		self.BIN_DATA_TO_COLUMN_NUMBER = {}

		self.bin_data = {}

		# for type in self.BIN_TYPE_TO_COLUMN_NUMBER.keys():
		# 	colmun_number = self.BIN_TYPE_TO_COLUMN_NUMBER[type]
		# 	self.BIN_COLUMN_NUMBER_TO_DATA[colmun_number] = type	

	def createNewKeyListPairInTableIfNotExist(self, key, table):
		if key not in table:
			table[key] = []

	def matchHeaderWithColumnNumber(self, headers):
		for header in headers:
				for column in range(len(self.BIN_COLUMN_HEADERS)):
					if self.BIN_COLUMN_HEADERS[column] == header:
						self.BIN_DATA_TO_COLUMN_NUMBER[header] = column
						self.BIN_COLUMN_NUMBER_TO_DATA[column] = header
						break

	def readBinFile(self, filePath):
		seperator = ' '
		with open(filePath, 'r') as f:
			headerLine = f.readline()
			headers = headerLine.strip().split(seperator)

			self.matchHeaderWithColumnNumber(headers)

			while True:
				line = f.readline() 
				if line == "": #EOF
					break;
				datas = line.strip().split(seperator)
				colmun_number = 0
				for data in datas:
					data_float_type = float(data)
					data_name = self.BIN_COLUMN_NUMBER_TO_DATA[colmun_number]
					self.createNewKeyListPairInTableIfNotExist(data_name, self.bin_data)
					self.bin_data[data_name].append(data_float_type)
					colmun_number += 1


	def plotData(self, axis, xvar_name, yvar_name, line_style = 'k-', _label = '', 
		do_linear_regression = False, convertToMBytes = False, convertToMs = False):
		xvar_data = self.bin_data[xvar_name]
		yvar_data = self.bin_data[yvar_name]
		if convertToMBytes:
			#TODO: only accounted for xvar_name being L3_occupancy
			if xvar_name == "L3_occupancy":
				xvar_data = [data/1024 for data in xvar_data]
		if convertToMs:
			if yvar_name == "service_time":
				yvar_data = [data/1e6 for data in yvar_data]
		if _label == '':
			axis.plot(xvar_data, yvar_data, line_style)
		else:
			axis.plot(xvar_data, yvar_data, line_style, label = _label)
		if do_linear_regression:
			self.runLinearRegression(axis, xvar_data, yvar_data)

	def plotDataVsMemoryBandWidth(self, axis, yvar_name, line_style = 'k-', _label = '',
		do_linear_regression = False, convertToGBytes = False, convertToMs = False):
		xvar_data = \
			[(read + write)/(servTime/1e9) for read, write, servTime in zip(
				self.bin_data["socket_read"], self.bin_data["socket_write"], 
				self.bin_data["service_time"])]
		if convertToGBytes:
			xvar_data = [data/1024/1024/1024 for data in xvar_data]

		# xvar_data = []
		# socket_read_list = self.bin_data["socket_read"]
		# print socket_read_list
		# print str(len(socket_read_list))
		# for index, socket_read in enumerate( socket_read_list):
		# 	socket_write = self.bin_data["socket_write"][index]
  #   		memory_bandwidth = socket_read + socket_write
  #   		xvar_data.append(memory_bandwidth)
		yvar_data = self.bin_data[yvar_name]
		# print "memory_bandwidth length is " + str(len(xvar_data))
		# print "y_var length is " + str(len(yvar_data))
		if convertToMs:
			if yvar_name == "service_time":
				yvar_data = [data/1e6 for data in yvar_data]
		if _label == '':
			axis.plot(xvar_data, yvar_data, line_style)
			
		else:
			axis.plot(xvar_data, yvar_data, line_style, label = _label)
		if do_linear_regression:
			self.runLinearRegression(axis, xvar_data, yvar_data)

	def clearData(self):
		self.bin_data.clear()

	def getList(self,list_name):
		return self.bin_data[list_name]

	def runLinearRegression(self, axis, x_values, y_values):
		slope, intercept, r_value, p_value, std_err = stats.linregress(x_values,y_values)
		leftEndx = min(x_values)
		rightEndx = max(x_values)
		leftEndy = leftEndx * slope + intercept
		rightEndy = rightEndx * slope + intercept
		axis.plot([leftEndx, rightEndx], [leftEndy, rightEndy], 'k-', label = 'line of best fit', linewidth=3)
		equation = 'y = ' + str(slope) + ' * x + ' + str(intercept) + '\nr = ' + str(r_value)
		# axis.text(0.1, 0.9, equation, ha='left', va='top', transform=axis.transAxes)
		with open('regression.coefficient', 'w') as f:
			f.write(str(slope) + ' ' + str(intercept) + ' ' + str(r_value) + ' ' + str(p_value) + ' ' + str(std_err)) 
			


