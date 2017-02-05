cmake_minimum_required(VERSION 3.2)

project(sample CXX)

set(TARGETS connection)
set(SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)
set(LIB_SOURCE_DIR ${SOURCE_DIR}/lib)

if(NOT CMAKE_RUNTIME_OUTPUT_DIRECTORY)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin)
endif()

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/external_projects.cmake)

include_directories(${EXTERNAL_PROJECTS_INCLUDE_PATHS})
include_directories(${LIB_SOURCE_DIR})

file(GLOB_RECURSE SOURCES ${LIB_SOURCE_DIR}/*.cpp)

foreach(TARGET ${TARGETS})
  add_executable(${TARGET} ${SOURCE_DIR}/${TARGET}.cpp ${SOURCES})
  target_link_libraries(${TARGET} ${EXTERNAL_PROJECTS_LIBRARIES})
  if(BUILD_EXTERNAL_PROJECT_NAMES)
    add_dependencies(${TARGET} ${BUILD_EXTERNAL_PROJECT_NAMES})
  endif()
endforeach(TARGET)

#add_custom_target(reload ALL
#                  COMMAND cmake ${CMAKE_CURRENT_SOURCE_DIR}
#                  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
#                  DEPENDS ${TARGETS})

set(CMAKE_CXX_FLAGS "")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS_RELEASE "-DNDEBUG -O2")

add_definitions(${CMAKE_CXX_FLAGS} "-std=c++14 -Wall")
