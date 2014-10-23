cmake_minimum_required(VERSION 2.8.9)
project(zlogger)
include_directories(
    .
    ../
    /opt/local/include/
    /usr/include
    )

link_directories(/opt/local/lib)


add_executable(main main.cpp)
target_link_libraries(main zmq)

