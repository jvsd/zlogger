#include <sys/ioctl.h>
#include <sys/types.h>
#include <time.h>
#include <zhelpers.hpp>
#include <inttypes.h>
#include <iostream>
#include <stdlib.h>
#include <fcntl.h>
#include <vector>

std::string fill_buffer(int& file,int& bytes_recv){
        int n = 0;
        char recv_buffer[64];
        std::string send_buffer;
        send_buffer.reserve(128);

        while(bytes_recv < 64)
        {
            n = read(file,&recv_buffer,64);
            if(n < 0)
            {
                std::cout << "Failed to recv data." << n << std::endl;
                break;
            }
            send_buffer.insert(bytes_recv,recv_buffer);
            bytes_recv += n;
            std::cout << "String length: " << send_buffer.length() << " Bytes: " << bytes_recv << std::endl;
        }
        return send_buffer;
}


int main(int argc, char* argv[])
{

    zmq::context_t context(1);

    zmq::socket_t socket_imu1(context,ZMQ_PUB);
    zmq::socket_t socket_pressure(context,ZMQ_PUB);
    socket_imu1.bind("tcp://*:4000");
    //socket_pressure.bind("tcp://*:4001");

    int imu1;
    imu1 = open("/dev/ttyO5",O_RDWR| O_NOCTTY);

    //int pressure;
    //pressure = open("/dev/ttyO1",O_RDWR| O_NOCTTY);


    std::string imu1_buffer;
    //std::string pressure_buffer;
    imu1_buffer.reserve(128);
    //pressure_buffer.reserve(128);


    int bytes_recv_imu1 = 0;
    //int bytes_recv_pressure = 0;
    while(1){

        bytes_recv_imu1 = 0;
      //  bytes_recv_pressure = 0;

        imu1_buffer = fill_buffer(imu1,bytes_recv_imu1);
        //pressure_buffer = fill_buffer(pressure,bytes_recv_pressure);

        s_send(socket_imu1,imu1_buffer);
        //s_send(socket_pressure,pressure_buffer);



    }

}


