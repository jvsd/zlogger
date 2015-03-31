#include <sys/ioctl.h>
#include <sys/types.h>
#include <time.h>
#include <zhelpers.hpp>
#include <inttypes.h>
#include <iostream>
#include <stdlib.h>
#include <fcntl.h>


int main(int argc, char* argv[])
{
    if(argc <3)
    {
        std::cout << "Not enough argumnets: Port, Serial Port" << std::endl;
        return 1;
    }
    std::string port = argv[1];
    std::string serial_port = argv[2];
    std::string bind_cmd = "tcp://*:";

    zmq::context_t context(1);
    zmq::socket_t socket(context,ZMQ_PUB);
    socket.bind((bind_cmd+port).c_str());

    int ser;
    ser = open(serial_port.c_str(),O_RDWR| O_NOCTTY);
    char recv_buffer[64];
    char send_buffer[128];
    memset(recv_buffer,'\0',sizeof(recv_buffer));


    int bytes_recv = 0;
    int n = 0;
    while(1){
        //std::cout << "Received: " << rx << std::endl;
        bytes_recv = 0;
        while(bytes_recv < 64)
        {
            n = read(ser,&recv_buffer,64);
            if(n < 0)
            {
                std::cout << "Failed to recv data." << std::endl;
                break;
            }
            memcpy(&send_buffer[bytes_recv],recv_buffer,n);
            bytes_recv += n;
        }
        zmq::message_t message(bytes_recv);
        memcpy((char*)message.data(),send_buffer,bytes_recv);
        socket.send(message);
    }

}


