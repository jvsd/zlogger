import numpy as np
import struct
import pandas as pd

class pressure(object):
	seq = 0
	time = 0
	pressure = np.zeros(21)
	dynamic_p = 0
	alpha = 0
	beta = 0

def convert_pressure(buffer):
#the buffer has already been split
	DATA_VARIABLES = 24 # 24 variables + time
	if len(buffer) >= DATA_VARIABLES*2:
		temp = []	
		for j in range(DATA_VARIABLES):
			k = j*2
			temp.append(struct.unpack('h',buffer[k]+buffer[k+1])[0])
		try:    
			temp.append(struct.unpack('H',buffer[DATA_VARIABLES*2:len(buffer)])[0])
			temp = np.asarray(temp)
		except:
			print 'exception\n'
			print buffer[DATA_VARIABLES*2:len(buffer)]
			temp = []
		if len(temp) >10:
			out_pressure = pressure
			for i in range(21):
				out_pressure.pressure[i] = temp[i]
			out_pressure.alpha = temp[22]
			out_pressure.beta = temp[23]
			out_pressure.seq = temp[24]
			out_pressure.dynamic_p = temp[21]
	return out_pressure

def get_data_pressure(sock):
	global imu2_data
	pressure_data = np.zeros((1,25))
	x_pressure = convert_pressure(sock.recv())
	for i in range(21):
		pressure_data[0,i] = x_pressure.pressure[i]
	pressure_data[0,22]=x_pressure.alpha
	pressure_data[0,23]=x_pressure.beta
	pressure_data[0,24]=x_pressure.seq
	pressure_data[0,21]=x_pressure.dynamic_p
	out_data = pd.DataFrame(pressure_data,columns = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,'alpha','beta','seq'])
	print out_data
	return out_data
