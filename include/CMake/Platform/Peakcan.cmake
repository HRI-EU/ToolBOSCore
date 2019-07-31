#
#  CMake Platform support for Peak CAN Router
#
#  Copyright (C)
#  Honda Research Institute Europe GmbH
#  Carl-Legien-Str. 30
#  63073 Offenbach/Main
#  Germany
#
#  UNPUBLISHED PROPRIETARY MATERIAL.
#  ALL RIGHTS RESERVED.
#
#

set(CMAKE_SYSTEM_NAME Generic)
set_property(GLOBAL PROPERTY TARGET_SUPPORTS_SHARED_LIBS OFF)

set(BUILD_SHARED_LIBS OFF)
set(CMAKE_SHARED_LIBRARY_C_FLAGS "")
set(CMAKE_SHARED_LIBRARY_CXX_FLAGS "")
set(CMAKE_SHARED_MODULE_C_FLAGS "")
set(CMAKE_SHARED_MODULE_CXX_FLAGS "")

# Compilers like that targeting bare metal systems don't pass
# CMake's compiler check, so fill in the results manually and mark the test
# as passed:
set(CMAKE_C_COMPILER_ID GNU)
set(CMAKE_CXX_COMPILER_ID GNU)
set(CMAKE_COMPILER_IS_GNUCC 1)
set(CMAKE_C_COMPILER_ID_RUN TRUE)
set(CMAKE_C_COMPILER_FORCED TRUE)
set(CMAKE_CXX_COMPILER_ID_RUN TRUE)
set(CMAKE_CXX_COMPILER_FORCED TRUE)


# EOF
