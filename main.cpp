#include <sys/ioctl.h>
#include <sys/types.h>
#include <time.h>
#include <zhelpers.hpp>
#include <inttypes.h>
#include <iostream>
#include <stdlib.h>
#include <fcntl.h>
#include <vector>

std::vector<char> fill_buffer(int& file,int& bytes_recv){
        int n = 0;
        char recv_buffer[64];
        std::vector<char> send_buffer(128);

        while(bytes_recv < 64)
        {
            n = read(file,&recv_buffer,64);
            if(n < 0)
            {
                std::cout << "Failed to recv data." << n << std::endl;
                break;
            }
            memcpy(&send_buffer[bytes_recv],recv_buffer,n);
            bytes_recv += n;
            std::cout << "loop" << std::endl;
        }
        std::cout << "Send_Buffer: "<< &send_buffer[0] << std::endl;
        return send_buffer;
}

void send_buffer(zmq::socket_t* socket, std::vector<char> buffer, int bytes_recv){
        std::cout << "sending" << std::endl;
        zmq::message_t message(bytes_recv);
        memcpy((char*)message.data(),&buffer[0],bytes_recv);
        socket->send(mes);
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


    std::vector<char> imu1_buffer(128);
    std::vector<char> pressure_buffer(128);


    int bytes_recv_imu1 = 0;
    int bytes_recv_pressure = 0;
    while(1){

        std::cout << "here" << std::endl;
        imu1_buffer = fill_buffer(imu1,bytes_recv_imu1);
        pressure_buffer = fill_buffer(pressure,bytes_recv_pressure);
        send_buffer(&socket_imu1,imu1_buffer,bytes_recv_imu1);
        send_buffer(&socket_pressure,pressure_buffer,bytes_recv_pressure);

    }

}


