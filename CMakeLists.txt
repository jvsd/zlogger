cmake_minimum_required(VERSION 2.8.9)
project(zlogger)
include_directories(
    .
    ../
    /usr/include
    )

add_executable(main main.cpp)
target_link_libraries(main zmq)

