import struct
import numpy as np
import pandas as pd

def convert_imu(binary_line):
    VARIABLES = 6
    temp = [0,0,0,0,0,0,0]
    if len(binary_line) == 14:
        for j in range(VARIABLES):
            k = j*2
            temp[j] = struct.unpack('h',binary_line[k]+binary_line[k+1])[0]

        temp[-1] = struct.unpack('h',binary_line[(VARIABLES*2):len(binary_line)])[0]
    temp_imu = imu
    temp_imu.time = temp[-1]
    temp_imu.ax = temp[0]
    temp_imu.ay = temp[1]
    temp_imu.az = temp[2]
    temp_imu.gx = temp[3]
    temp_imu.gy = temp[4]
    temp_imu.gz = temp[5]
    return temp_imu

class imu(object):
        time=0
        Fs=0
        ax=0
        ay=0
        az=0
        gx=0
        gy=0
        gz=0

def get_data_imu(sock):
	imu1_data = np.zeros((1,7))
	out_data = pd.DataFrame(imu1_data,columns=['ax','ay','az','gx','gy','gz','seq'])
	count = 0
	l_imu = []
	while(count < 100):
		x_imu = convert_imu(sock.recv())
		print x_imu.time
		imu1_data = np.zeros((1,7))
		imu1_data[0,0] = x_imu.ax
		imu1_data[0,1] = x_imu.ay
		imu1_data[0,2] = x_imu.az
		imu1_data[0,3] = x_imu.gx
		imu1_data[0,4] = x_imu.gy
		imu1_data[0,5] = x_imu.gz
		imu1_data[0,6] = x_imu.time
		out_data = out_data.append(pd.DataFrame(imu1_data,columns=['ax','ay','az','gx','gy','gz','seq']))
		print count
		count+=1
	print out_data[1:out_data.shape[0]]
	return out_data[1:out_data.shape[0]]


	
