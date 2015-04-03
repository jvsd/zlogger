import zmq
import serial
import time
import numpy as np
import sys
import struct
import socket
import datetime as datetime
class imu(object):
        time=0
        Fs=0
        ax=0
        ay=0
        az=0
        gx=0
        gy=0
        gz=0


def format(value):
    return "%.3f" % value

class serial_publisher(object):
    def __init__(self,s_type,zmq_context,port,serial_port,serial_baud):
        self.s_type=s_type
        self.zmq_context = zmq_context
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
        self.error_lines = 0
        self.sent_lines = 0
        self.time = 0
        self.ctime = 0
        self.m_time = datetime.datetime.now()
        self.dt = np.zeros(100).tolist()

        if s_type == 0: # Serial port
            self.ser = serial.Serial(
                    port = serial_port,
                    baudrate = serial_baud,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=0,
                    xonxoff=False,
                    rtscts=False,
                    interCharTimeout=None
                )
        elif s_type == 1:
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sock.connect(("192.168.0.113",2000))
        elif s_type == 2:
            self.subscriber = self.zmq_context.socket(zmq.SUB)
            self.subscriber.setsockopt(zmq.SUBSCRIBE,'')
            self.subscriber.connect('ipc:///tmp/4000')
        elif s_type == 3:
            print 'no source'

        self.buffer = ''
        self.log_file = open('imu.log','a')


    def run(self,buffer='',time_stamp = ''):
        self.time = datetime.datetime.now().isoformat()
        self.dt.insert(0,(self.m_time-datetime.datetime.now()).total_seconds())
        self.dt.pop()

        if self.s_type==0:
            if self.ser.inWaiting() > 128:
                self.buffer=self.buffer + self.ser.read(128)
        elif self.s_type==1:
            print 'waiting to recv...'
            self.buffer=self.buffer + self.sock.recv(1024)
        elif self.s_type==2:
            self.buffer = self.buffer + self.subscriber.recv()
            print len(self.buffer)
        elif self.s_type==3:
            self.buffer = self.buffer + buffer
            self.time = time_stamp 


        if '\x0c\x81' in self.buffer:
            lines = self.buffer.split('\x0c\x81')
            for i in range(len(lines)-1):
                socks = dict(self.poller.poll(0))
                if socks:
                    if socks.get(self.server) == zmq.POLLIN:
                        self.server.recv()
                        self.server.send(lines[i])

                self.log_data(lines[i])
                self.data_server.send(lines[i])
                if len(lines[i]) != 14:
                    self.error_lines += 1
                if len(lines[i]) == 14:
                    self.sent_lines += 1
                print 'line: ' + str(len(lines[i])) + "Errors:" + str(self.error_lines)

            self.buffer=lines[-1]
            print 'buffer: ' + str(len(self.buffer))
        self.m_time = datetime.datetime.now()
        print 'Mean time: ' + str(np.asarray(self.dt).mean()*100000.)	

    def log_data(self,raw_data):
        s = dict(self.mark_poller.poll(0))
        if s:
            if s.get(self.marker) == zmq.POLLIN:
                self.mark = float(self.marker.recv())

        t_imu = self.convert_imu(raw_data)
        plist = [t_imu.ax,t_imu.ay,t_imu.az,t_imu.gx,t_imu.gy,t_imu.gz,t_imu.time,self.mark]
        for item in plist:
            self.log_file.write("%f\t" % item)
        self.log_file.write(self.time + '\n')
        
        
    def convert_imu(self,binary_line):
        VARIABLES = 6
        temp = [0,0,0,0,0,0,0]
        if len(binary_line) == 14:
	    for j in range(VARIABLES):
	        k = j*2
	        temp[j] = struct.unpack('h',binary_line[k]+binary_line[k+1])[0]

	    temp[-1] = struct.unpack('H',binary_line[(VARIABLES*2):len(binary_line)])[0]
        temp_imu = imu
        temp_imu.time = temp[-1]
        temp_imu.ax = temp[0]
        temp_imu.ay = temp[1]
        temp_imu.az = temp[2]
        temp_imu.gx = temp[3]
        temp_imu.gy = temp[4]
        temp_imu.gz = temp[5]
        return temp_imu
