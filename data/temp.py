import numpy as np
from scipy import fft
from scipy.interpolate import interp1d
import pandas as pd
from scipy.signal import butter,lfilter
from math import sqrt,pi,log
from numpy import zeros,argmax,linspace,cos,mean
from scipy.fftpack import fft
from scipy import integrate
import matplotlib.pyplot as plt
from sys import stdin

TUNED = 650.655

imu1 = pd.read_csv('imu1.log',sep="\t",header = None)
imu1.columns = ['ax','ay','az','gx','gy','gz','seq','mark','time']
imu2 = pd.read_csv('imu2.log',sep="\t",header = None)
imu2.columns = ['ax','ay','az','gx','gy','gz','seq','mark','time']
pressure = pd.read_csv('pressure.log',sep="\t",header = None)
pressure.columns = pressure_columns = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,'alpha','beta','seq','time']

#Sequence fix
imu2['seq'] = imu2['seq'] - imu2['seq'][0]
imu1['seq'] = imu1['seq'] + (imu2['seq'][1]-imu1['seq'][1])

f1 = interp1d(imu1['seq'][5:-1],imu1['az'][5:-1])
f2 = interp1d(imu2['seq'][5:-1],imu2['az'][5:-1])
#min error of sum(A1 - (A2 * (Ct))
last_error = -1
t = 0
dt = .00001

while(current_error < last_error):

	e = 0
	for i in range(int(len(imu2['az'][5:-1])-np.ceil(t))):
		i+=5
		e += (f2(imu2['seq'][i]+t) - imu1['az'][i])**2    
	if(last_error == -1):
		last_error = current_error + 1
	else:
		last_error = current error
	current_error = e
	t +=dt

