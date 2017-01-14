cmake_minimum_required(VERSION 3.2)

project(sample CXX)

set(SUB_DIR ${CMAKE_CURRENT_SOURCE_DIR}/sub)

set(BIN_DIR ${CMAKE_CURRENT_SOURCE_DIR}/bin)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/external_projects.cmake)

unset(EXTERNAL_PROJECTS_INCLUDE_PATHS)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${BIN_DIR}/optimization)
add_subdirectory(${SUB_DIR}/optimization)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${BIN_DIR}/placement)
add_subdirectory(${SUB_DIR}/placement)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${BIN_DIR}/parallelization)
add_subdirectory(${SUB_DIR}/parallelization)
