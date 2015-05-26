import serial
import zmq
import time
import numpy as np
import struct
import signal
import sys
import argparse

class logger():
    def __init__(self,s_type,zmq_context,port,file_name):
        self.handle = open(file_name,'a')
        self.server=zmq_context.socket(zmq.REP)
        self.data_server = zmq_context.socket(zmq.PUB)
        self.data_server.bind('tcp://*:'+port)
        self.server.bind('tcp://*:'+str(int(port)+1))
        self.poller = zmq.Poller()
        self.poller.register(self.server,zmq.POLLIN)

        self.marker=zmq_context.socket(zmq.SUB)
        self.marker.setsockopt(zmq.SUBSCRIBE,'')
        self.marker.connect('tcp://localhost:5001')
        self.mark_poller = zmq.Poller()
        self.mark_poller.register(self.marker,zmq.POLLIN)
        self.mark = 0.0
	self.buffer = ''
        self.s_type=3
        self.time = 0
        self.zmq_context = zmq_context

    def setup_serial(self):
        self.ser = serial.Serial(
                        port = '/dev/ttyO1',
                        baudrate=115200,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=0,
                        xonxoff=False,
                        rtscts=False,
			interCharTimeout=None
                    )

        self.buffer = ''
	self.ser.close()
	self.ser.open()
        #time.sleep(.5)
        self.ser.read(self.ser.inWaiting())
        self.buffer = ''


    def convert_buffer_bin_to_np(self,buffer):
        #'\xff\xfb'
	DATA_VARIABLES = 24 # 24 variables + time
        lines = buffer.split('\xff\xfb')
        data = np.zeros((1,DATA_VARIABLES+1))
        flag = 0
        for x,i in enumerate(lines):
            temp = []
            if len(i) >= DATA_VARIABLES*2:
                for j in range(DATA_VARIABLES):
                    k = j*2
                    temp.append(struct.unpack('h',i[k]+i[k+1])[0])
                try:    
                    #temp.append(float(i[DATA_VARIABLES*2:len(i)]))#27*2 variables
                    temp.append(struct.unpack('H',i[DATA_VARIABLES*2:len(i)])[0])
                    temp = np.asarray(temp)
                except:
                    print 'exception\n'
                    print i[DATA_VARIABLES*2:len(i)]
                    temp = []
                if len(temp) >10:
                    if flag==0:
                        data[0]=temp
                        flag = 1
                    else:
                        data = np.vstack((data,temp))
        return data
    
    def signal_handler(self, signal, frame):
        print 'closing...'
        sys.exit(0)

    def run(self,buffer='',time_stamp=''):
        if self.s_type == 0:
	    if self.ser.inWaiting() > 128:
                self.buffer=self.buffer + self.ser.read(128)
        elif self.s_type == 3:
            self.buffer = self.buffer + buffer
            self.time = time_stamp


        if '\xff\xfb' in self.buffer:
            data = self.convert_buffer_bin_to_np(self.buffer)
            if data[0][0] != 0.0 and data[0][1] != 0.0:
                #np.savetxt(self.handle,data,fmt='%d',delimiter='\t')
                self.log_data(data)
            self.buffer=self.buffer.split('\xff\xfb')[-1]
        else:
            print 'nothing ' + str(len(self.buffer))

    def log_data(self,data):
        s = dict(self.mark_poller.poll(0))
        if s:
            if s.get(self.marker) == zmq.POLLIN:
                self.mark = float(self.marker.recv())
        for i in range(data.shape[0]):
            plist = data[i].tolist()
            for item in plist:
                self.handle.write("%f\t" % item)
            self.handle.write(self.time + '\n')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name", help = "File name to dump data")
    args = parser.parse_args()
    print args.file_name

    log = logger(args.file_name)
    while(True):
        log.run()
