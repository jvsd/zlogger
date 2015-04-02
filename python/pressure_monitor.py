import serial
import time
import numpy as np
import struct
import signal
import sys
import argparse

class logger():
    def __init__(self,file_name):
        self.handle = file(file_name,'a')
	self.buffer = ''

    def setup_serial(self)
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
                    temp.append(float(i[DATA_VARIABLES*2:len(i)]))#27*2 variables
                    temp = np.asarray(temp)
                except:
                    print 'exception\n'
                    print i[DATA_VARIABLES:len(i)]
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

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        #while(True):
	if self.ser.inWaiting() > 128:
            self.buffer=self.buffer + self.ser.read(128)

        #self.buffer = self.buffer + self.ser.read(self.ser.inWaiting())
        #if '\xff\xfb' in self.buffer:
            #data = self.convert_buffer_bin_to_np(self.buffer)
            #if data[0][0] != 0.0 and data[0][1] != 0.0:
            #    np.savetxt(self.handle,data,fmt='%d',delimiter='\t')
            #self.buffer=self.buffer.split('\xff\xfb')[-1]
        #else:
        #    print 'nothing ' + str(len(self.buffer))
	#time.sleep(.05)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name", help = "File name to dump data")
    args = parser.parse_args()
    print args.file_name

    log = logger(args.file_name)
    while(True):
        log.run()
