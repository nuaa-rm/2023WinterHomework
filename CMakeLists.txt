cmake_minimum_required(VERSION 3.24)
project(2023WinterHomework)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 14)
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})
message(${OpenCV_INCLUDE_DIRS})


add_executable(2023WinterHomework main.cpp)

target_link_libraries(2023WinterHomework  ${OpenCV_LIBS})

