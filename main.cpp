#include <sys/ioctl.h>
#include <sys/types.h>
#include <time.h>
#include <zhelpers.hpp>
#include <inttypes.h>


int main(void)
{
    zmq::context_t context(1);
    zmq::socket_t socket(context,ZMQ_SUB);
    uint64_t hwm = 1;
    socket.setsockopt(ZMQ_SUBSCRIBE,"",0);
    socket.connect("tcp://10.0.2.14:5000");

    int rx = 0;
    while(1){

        std::cout << "Received: " << rx << std::endl;
        std::string s = s_recv(socket);
        std::cout << s;
        rx++;
    }

}


