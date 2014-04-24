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
bool DEBUG = false;

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
            if(DEBUG)
            {
                std::cout << "String length: " << send_buffer.size() << " Bytes: " << bytes_recv << std::endl;
            }
        }
        return send_buffer;
}


int main(int argc, char* argv[])
{

    zmq::context_t context(1);

    zmq::socket_t socket_imu1(context,ZMQ_PUB);
    zmq::socket_t requested(context,ZMQ_REP);
    requested.bind("tcp://*:4001");
    //socket_imu1.bind("ipc:///tmp/4000");
    socket_imu1.bind("tcp://*:4000");


    struct tm *localTime;
    timeval curTime;

    int imu1;
    int imu2;
    int pressure;


    std::string imu1_buffer;
    std::string pressure_buffer;
    std::string imu2_buffer;
    std::string request;



    int bytes_recv_imu1 = 0;
    int bytes_recv_pressure = 0;
    int bytes_recv_imu2 = 0;
    int counter;
    int loops = 0;
    while(1){

        request = s_recv(requested);
        counter = 0;
        imu1 = open("/dev/ttyO5",O_RDWR| O_NOCTTY | O_SYNC); //| O_NDELAY);
        imu2 = open("/dev/ttyO2",O_RDWR| O_NOCTTY | O_SYNC);
        pressure = open("/dev/ttyO1",O_RDWR| O_NOCTTY | O_SYNC); // | O_NDELAY);

	//Get time when we start for syncing.
        std::stringstream outTime;
        gettimeofday(&curTime,NULL);
        localTime=localtime(&curTime.tv_sec);
        int day = localTime->tm_mday;
        int hour = localTime->tm_hour;
        int min = localTime->tm_min;
        int sec = localTime->tm_sec;
        int millis = curTime.tv_usec / 1000;
        outTime << day << ":" << hour << ":" << min << ":" << sec << ":" << millis;
	s_send(requested,outTime.str());

        while(counter < 500)
        {
            imu1_buffer.reserve(SEND_BUF_SIZE);
            imu2_buffer.reserve(SEND_BUF_SIZE);
            pressure_buffer.reserve(SEND_BUF_SIZE);

            bytes_recv_imu1 = 0;
            bytes_recv_imu2 = 0;
            bytes_recv_pressure = 0;


            imu1_buffer = fill_buffer(imu1,bytes_recv_imu1);
            imu2_buffer = fill_buffer(imu2,bytes_recv_imu2);
            pressure_buffer = fill_buffer(pressure,bytes_recv_pressure);

            //s_sendmore(socket_imu1,outTime.str());
            s_sendmore(socket_imu1,imu1_buffer);
	    s_sendmore(socket_imu1,imu2_buffer);
            s_send(socket_imu1,pressure_buffer);
            counter += 1;
        }

	loops+=1;
        close(imu1);
        close(imu2);
        close(pressure);
	std::cout << "Request: " << request << " ,Loops " << loops << std::endl;
        //zmq::message_t reply(sizeof(int));
        //memcpy ((void *) reply.data (), &counter,sizeof(int));
        //requested.send(reply);
    }

}


