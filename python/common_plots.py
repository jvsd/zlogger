import numpy as np
from scipy import fft
import pandas as pd
from scipy.signal import butter,lfilter
from math import sqrt,pi,log
from numpy import zeros,argmax,linspace,cos,mean
from scipy.fftpack import fft
from scipy import integrate
import matplotlib.pyplot as plt
from sys import stdin


WIFI_TUNED = 641.425
TUNED = 650.655

def plotspectrum(y,Fs,color,x=0):
    """
    Plots a Single-Sided Amplitude Spectrum of y(t)
    """
    
    #subtract mean
    #fig,ax = plt.subplots(2)
    #ax[1].plot(y,color)
    y_temp=y-y.mean()
    y = np.copy(y_temp)
    n = len(y) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(n/2)] # one side frequency range

    Y = fft(y)/n # fft computing and normalization
    Y = Y[range(n/2)]
    return frq,2*abs(Y)

