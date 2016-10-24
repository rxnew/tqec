cmake_minimum_required(VERSION 2.8)

project(tqec CXX)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin)

set(LIB conn)
set(MAIN connection)
set(SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)
set(MAIN_SOURCE_DIR ${SOURCE_DIR}/main)
set(LIB_SOURCE_DIR ${SOURCE_DIR}/lib)

include_directories(${LIB_SOURCE_DIR})

file(GLOB_RECURSE LIB_SOURCES ${LIB_SOURCE_DIR}/*.cpp)

add_library(${LIB} STATIC ${LIB_SOURCES})

set_target_properties(${LIB} PROPERTIES
                      PUBLIC_HEADER ${LIB_SOURCE_DIR}/${LIB}.hpp)

install(TARGETS ${LIB}
        EXPORT ${LIB}-export
        ARCHIVE        DESTINATION lib
        INCLUDES       DESTINATION include
        PUBLIC_HEADER  DESTINATION include/${LIB})

install(EXPORT ${LIB}-export
        FILE ${LIB}-config.cmake
        DESTINATION share/cmake/${LIB})

foreach(TARGET ${MAIN})
  add_executable(${TARGET} ${MAIN_SOURCE_DIR}/${TARGET}.cpp)
  target_link_libraries(${TARGET} ${LIB})
endforeach(TARGET)

set(CMAKE_CXX_FLAGS "")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS_RELEASE "-DNDEBUG -O2")

add_definitions(${CMAKE_CXX_FLAGS} "-std=c++11 -Wall")
