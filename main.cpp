#include <sys/ioctl.h>
#include <sys/types.h>
#include <time.h>
#include <zhelpers.hpp>
#include <inttypes.h>
#include <iostream>
#include <stdlib.h>
#include <fcntl.h>

int fill_buffer(int file,char * recv_buffer, char* send_buffer){
        int bytes_recv = 0;
        int n = 0;
        while(bytes_recv < 64)
        {
            n = read(file,&recv_buffer,64);
            if(n < 0)
            {
                std::cout << "Failed to recv data." << std::endl;
                break;
            }
            memcpy(&send_buffer[bytes_recv],recv_buffer,n);
            bytes_recv += n;
        }
        return bytes_recv;
}

void send_buffer(zmq::socket_t* socket, char* buffer, int bytes_recv){
        zmq::message_t message(bytes_recv);
        memcpy((char*)message.data(),send_buffer,bytes_recv);
        socket->send(message);
}
    

int main(int argc, char* argv[])
{

    zmq::context_t context(1);

    zmq::socket_t socket_imu1(context,ZMQ_PUB);
    zmq::socket_t socket_pressure(context,ZMQ_PUB);
    socket_imu1.bind("tcp://*:4000");
    socket_pressure.bind("tcp://*:4001");

    int imu1;
    imu1 = open("/dev/ttyO5",O_RDWR| O_NOCTTY);

    int pressure;
    pressure = open("/dev/ttyO1",O_RDWR| O_NOCTTY);

    char recv_imu1_buffer[64];
    char recv_pressure_buffer[64];

    char imu1_buffer[128];
    char pressure_buffer[128];


    int bytes_recv_imu1 = 0;
    int bytes_recv_pressure = 0;
    while(1){
        bytes_recv_imu1 = fill_buffer(imu1,recv_imu1_buffer,imu1_buffer);
        bytes_recv_pressure =fill_buffer(pressure,recv_pressure_buffer,pressure_buffer);
        send_buffer(&socket_imu1,imu1_buffer,bytes_recv_imu1);
        send_buffer(&socket_pressure,pressure_buffer,bytes_recv_pressure);

    }

}


