import zmq
import serial
import time
import numpy as np
import sys
import struct
import socket
import datetime as datetime
import pressure_monitor as pressure_monitor
import imu_monitor as imu_monitor



#Requires (1)scriptname (2)zmq_port (3)serial_port (4)serial_baud
if __name__=='__main__':
    if len(sys.argv) != 5:
        print 'input arguments are s_type zmq_port serial_port serial_baud'
        sys.exit()
    else:
        s_type = int(sys.argv[1])
        zmq_port = sys.argv[2]
        serial_port = sys.argv[3]
        serial_baud = sys.argv[4]
        
    cont = zmq.Context()
    m_imu = imu_monitor.serial_publisher(3,cont,zmq_port,serial_port,serial_baud,'imu1.log')
    m_imu2 = imu_monitor.serial_publisher(3,cont,str(int(zmq_port)+2),serial_port,serial_baud, 'imu2.log')
    m_pressure = pressure_monitor.logger(s_type = 3,zmq_context = cont,port = str(int(zmq_port)+10),file_name = 'pressure.log')

    serial_subscriber = cont.socket(zmq.SUB)
    starter_sock = cont.socket(zmq.REP)
    serial_subscriber.setsockopt(zmq.SUBSCRIBE,'')
    serial_subscriber.connect("tcp://192.168.0.150:4000")
    starter_sock.bind("tcp://*:4998")
    marker = cont.socket(zmq.PUB)
    marker.bind("tcp://*:4999")

    poller = zmq.Poller()
    poller.register(serial_subscriber,zmq.POLLIN)

    while(True):
        ##Wait for starting signal
        r = starter_sock.recv()
        starter_sock.send(r)
        #send marker from starting signal
        marker.send(str(r))

        #start zlogger
        requested = cont.socket(zmq.REQ)
        requested.connect("tcp://192.168.0.150:4001")
        requested.send('none')
        #get start time stamp
        start_stamp = requested.recv()
        
        recv_messages = 0
        while(True):
            try:
                socks = dict(poller.poll(10*1000))
            except:
                print 'exception in poll'
                break
            if serial_subscriber in socks:
                message = serial_subscriber.recv_multipart()
                recv_message += 1

                m_imu.run(buffer = message[0],time_stamp = start_stamp)
                m_imu2.run(buffer = message[1],time_stamp = start_stamp)
                m_pressure.run(buffer = message[2],time_stamp = start_stamp)
            else:
                break
        print "Received " + str(recv_messages) + " messages with time " + str(start_stamp) + ", marked by " + str(r)



