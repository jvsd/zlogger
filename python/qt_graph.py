#!/usr/bin/python
#export PYTHONPATH=/media/disk/users/jamesd/Dropbox/Developer/virtualenv/imu/python/pyqtgraph/pyqtgraph:/media/disk/users/jamesd/Dropbox/Developer/virtualenv/imu/python/pyqtgraph/examples

import initExample

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
from scipy import fft
import struct
import zmq
import pandas as pd

from imu import *
from pressure import *
from common_plots import *



def update():
	global curve, data, ptr, p, lastTime, fps, lr
	p.clear()
	p_imu2.clear()
	socks = dict(poller.poll(0))
	if m_sockets[0] in socks and socks[m_sockets[0]]==zmq.POLLIN:
		data['imu1'] = data['imu1'].append(get_data_imu(m_sockets[0]))
	if m_sockets[1] in socks and socks[m_sockets[1]]==zmq.POLLIN:
		data['imu2'] = data['imu2'].append(get_data_imu(m_sockets[1]))
	if m_sockets[2] in socks and socks[m_sockets[2]]==zmq.POLLIN:
		data['pressure'] = data['pressure'].append(get_data_pressure(m_sockets[2]))

	curve = pg.PlotCurveItem(data['imu1']['az'].as_matrix(),pen="r")
	curve_imu2 = pg.PlotCurveItem(data['imu2']['az'].as_matrix(),pen="r")
	p.addItem(curve)
	p_imu2.addItem(curve_imu2)
	p.addItem(lr)
	p_imu2.addItem(lr2)
	ptr += 1
	now = time()
	dt = now - lastTime
	lastTime = now
	if fps is None:
		fps = 1.0/dt
	else:
		s = np.clip(dt*3., 0, 1)
		fps = fps * (1-s) + (1.0/dt) * s
		p.setTitle('%0.2f fps' % fps)

def updatePlot():
	global d_frq,p_frq,m_frq
	p2.clear()
	r = lr.getRegion()
	frq,amp = plotspectrum(data['imu1']['az'][int(r[0]):int(r[1])],641.425+p_frq,'k')
	curve = pg.PlotCurveItem(frq,amp,pen="r")
	p2.addItem(curve)
	m_frq = frq[amp.argmax()]
	print m_frq, p_frq
def updatePlot2():
	global d_frq,p_frq,m_frq
	p3.clear()
	r = lr2.getRegion()
	frq,amp = plotspectrum(data['imu2']['az'][int(r[0]):int(r[1])],641.425+p_frq,'k')
	curve = pg.PlotCurveItem(frq,amp,pen="r")
	p3.addItem(curve)
	m_frq = frq[amp.argmax()]
	print m_frq, p_frq
        #if m_frq < d_frq:
        #    p_frq += .001
        #elif m_frq > d_frq:
        #    p_frq -= .001


app = QtGui.QApplication([])

zmq_cont = zmq.Context()
imu1_sock = zmq_cont.socket(zmq.SUB)
imu2_sock = zmq_cont.socket(zmq.SUB)
pressure_sock = zmq_cont.socket(zmq.SUB)
m_sockets = [imu1_sock,imu2_sock,pressure_sock]
m_ports = [5000,5002,5010]
poller = zmq.Poller()
for x,sock in enumerate(m_sockets):
	sock.setsockopt(zmq.SUBSCRIBE,'')
	sock.connect('tcp://192.168.0.114:'+str(m_ports[x]))
	poller.register(sock,zmq.POLLIN)


win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
pg.setConfigOptions(antialias=True)

p = win.addPlot(title="z axis")
p.setRange(xRange=[-500, 500], yRange=[-500, 500])
p_imu2 = win.addPlot(title='imu2')

imu1_data = np.zeros((1,7))
imu2_data = np.zeros((1,7))
pressure_data = np.zeros((1,25))
data = {'imu1':pd.DataFrame(np.zeros((1,7))
,columns=['ax','ay','az','gx','gy','gz','seq']),'imu2':pd.DataFrame(np.zeros((1,7))
,columns=['ax','ay','az','gx','gy','gz','seq']),'pressure':pd.DataFrame(np.zeros((1,26)),columns = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,'alpha','beta','seq','time'])}

ptr = 0
lastTime = time()
fps = None
lr = pg.LinearRegionItem([0,500])
lr.setZValue(-10)

lr2 = pg.LinearRegionItem([0,500])
lr2.setZValue(-10)


    #app.processEvents()  ## force complete redraw for every plot
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(20)
    



win.nextRow()

p2 = win.addPlot(title="fft")
#frq,amp = plotspectrum(data,100.,'k')
#p2.plot(frq,amp)
d_frq = 159.20
p_frq = 9.42
m_frq = 0.0

p3 = win.addPlot(title="Imu2 fft")

lr.sigRegionChanged.connect(updatePlot)
lr2.sigRegionChanged.connect(updatePlot2)


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
