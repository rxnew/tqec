cmake_minimum_required(VERSION 3.2)

set(SPP_INCLUDE_PATHS ${SPP_INCLUDE_PATHS}
    /lib/include
    /lib/local/include)

if(INSTALL_EXTERNAL_PROJECTS_PREFIX)
  set(SPP_INCLUDE_PATHS ${SPP_INCLUDE_PATHS}
      ${INSTALL_EXTERNAL_PROJECTS_PREFIX}/include)
endif()

if(EXTERNAL_PROJECTS_PATHS)
  set(SPP_INCLUDE_PATHS ${SPP_INCLUDE_PATHS}
      ${EXTERNAL_PROJECTS_PATHS}/include)
endif()

find_path(SPP_INCLUDE_PATH
          NAMES spp
          PATHS ${SPP_INCLUDE_PATHS})

if(NOT SPP_INCLUDE_PATH)
  include(${CMAKE_CURRENT_LIST_DIR}/spp.cmake)
endif()
