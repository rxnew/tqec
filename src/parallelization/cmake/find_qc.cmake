cmake_minimum_required(VERSION 3.2)

set(QC_INCLUDE_PATHS ${QC_INCLUDE_PATHS}
    /lib/include
    /lib/local/include)

set(QC_LIBRARY_PATHS ${QC_LIBRARY_PATHS}
    /usr/lib
    /usr/local/lib)

if(INSTALL_EXTERNAL_PROJECTS_PREFIX)
  set(QC_INCLUDE_PATHS ${QC_INCLUDE_PATHS}
      ${INSTALL_EXTERNAL_PROJECTS_PREFIX}/include)

  set(QC_LIBRARY_PATHS ${QC_LIBRARY_PATHS}
      ${INSTALL_EXTERNAL_PROJECTS_PREFIX}/lib)
endif()

if(EXTERNAL_PROJECTS_PATHS)
  set(QC_INCLUDE_PATHS ${QC_INCLUDE_PATHS}
      ${EXTERNAL_PROJECTS_PATHS}/include)

  set(QC_LIBRARY_PATHS ${QC_LIBRARY_PATHS}
      ${EXTERNAL_PROJECTS_PATHS}/lib)
endif()

find_path(QC_INCLUDE_PATH
          NAMES qc
          PATHS ${QC_INCLUDE_PATHS})

find_library(QC_LIBRARY
             NAMES qc
             PATHS ${QC_LIBRARY_PATHS})

if(NOT QC_INCLUDE_PATH OR NOT QC_LIBRARY)
  include(${CMAKE_CURRENT_LIST_DIR}/qc.cmake)
endif()
