#include <sys/ioctl.h>
#include <sys/types.h>
#include <time.h>
#include <zhelpers.hpp>
#include <inttypes.h>
timespec count1;

void startTime();
double getElapsed();
double diff(timespec start, timespec end);

int main(void)
{
    zmq::context_t context(1);
    zmq::socket_t socket(context,ZMQ_SUB);
    uint64_t hwm = 1;
    socket.setsockopt(ZMQ_SUBSCRIBE,"",0);
    socket.setsockopt(ZMQ_HWM,&hwm,sizeof(hwm));
    socket.connect("tcp://localhost:5555");

    int rx = 0;
    while(1){

        std::cout << "Received: " << rx << std::endl;
        std::string s = s_recv(socket);
        std::cout << s;
        rx++;
    }

}

void startTime()
{
    clock_gettime(CLOCK_REALTIME,&count1);
}

double getElapsed()
{
    timespec current;
    clock_gettime(CLOCK_REALTIME,&current);
    return diff(count1,current);
}

double diff(timespec start, timespec end)
{
    timespec temp;
    if ((end.tv_nsec-start.tv_nsec)<0){
        temp.tv_sec = end.tv_sec-start.tv_sec-1;
        temp.tv_nsec = 1000000000+end.tv_nsec-start.tv_nsec;
    }else{
        temp.tv_sec = end.tv_sec-start.tv_sec;
        temp.tv_nsec = end.tv_nsec - start.tv_nsec;
    }
    return double(temp.tv_sec*1000000000.0+temp.tv_nsec)/1000.0;
}

