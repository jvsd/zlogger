#include <sys/ioctl.h>
#include <sys/types.h>
#include <time.h>
#include <zhelpers.hpp>
#include <inttypes.h>
#include <iostream>
#include <sstream>
#include <stdlib.h>
#include <vector>
#include <unistd.h>
#include <fcntl.h>
#include <ctime>

int SEND_BUF_SIZE = 512;
int RECV_BUF_SIZE = 128;

// ./main ran as default and python script ran with -5 works well. Must setup ports with python prior. also set cpu_Freq to performance.

std::string fill_buffer(int& file,int& bytes_recv){
        int n = 0;
        char recv_buffer[RECV_BUF_SIZE];
        std::string send_buffer;
        send_buffer.reserve(SEND_BUF_SIZE);

        while(bytes_recv < RECV_BUF_SIZE)
        {
            n = read(file,recv_buffer,RECV_BUF_SIZE);
            if(n < 0)
            {
                std::cout << "Failed to recv data." << n << std::endl;
                break;
            }
            send_buffer.insert(bytes_recv,&recv_buffer[0],n);
            bytes_recv += n;
            std::cout << "String length: " << send_buffer.size() << " Bytes: " << bytes_recv << std::endl;
        }
        return send_buffer;
}


int main(int argc, char* argv[])
{

    zmq::context_t context(1);

    zmq::socket_t socket_imu1(context,ZMQ_PUB);
    //zmq::socket_t socket_pressure(context,ZMQ_PUB);
    socket_imu1.bind("ipc:///tmp/4000");
    //socket_pressure.bind("ipc:///tmp/4001");

    struct tm *localTime;
    timeval curTime;

    int imu1;
    imu1 = open("/dev/ttyO5",O_RDWR| O_NOCTTY); //| O_NDELAY);

    int pressure;
    pressure = open("/dev/ttyO1",O_RDWR| O_NOCTTY); // | O_NDELAY);


    std::string imu1_buffer;
    std::string pressure_buffer;



    int bytes_recv_imu1 = 0;
    int bytes_recv_pressure = 0;
    while(1){
        imu1_buffer.reserve(SEND_BUF_SIZE);
        pressure_buffer.reserve(SEND_BUF_SIZE);
        std::stringstream outTime;

        bytes_recv_imu1 = 0;
        bytes_recv_pressure = 0;

        gettimeofday(&curTime,NULL);
        localTime=localtime(&curTime.tv_sec);


        int day = localTime->tm_mday;
        int hour = localTime->tm_hour;
        int min = localTime->tm_min;
        int sec = localTime->tm_sec;
        int millis = curTime.tv_usec / 1000;

        imu1_buffer = fill_buffer(imu1,bytes_recv_imu1);
        pressure_buffer = fill_buffer(pressure,bytes_recv_pressure);
        //imu1_buffer.shrink_to_fit();
        //pressure_buffer.shrink_to_fit();

        outTime << day << ":" << hour << ":" << min << ":" << sec << ":" << millis;
        s_sendmore(socket_imu1,outTime.str());
        s_sendmore(socket_imu1,imu1_buffer);
        s_send(socket_imu1,pressure_buffer);

    }

}


