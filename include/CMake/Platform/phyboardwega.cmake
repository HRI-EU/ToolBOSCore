#
#  CMake Platform support for the phyBOARD-WEGA
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

set(CMAKE_SYSTEM_NAME phyboardwega)

set(BUILD_SHARED_LIBS OFF)

# Compilers like that don't pass CMake's compiler check, so fill in the
# results manually and mark the test as passed:
set(CMAKE_C_COMPILER_ID GNU)
set(CMAKE_CXX_COMPILER_ID GNU)
set(CMAKE_COMPILER_IS_GNUCC 1)
set(CMAKE_C_COMPILER_ID_RUN TRUE)
set(CMAKE_C_COMPILER_FORCED TRUE)
set(CMAKE_CXX_COMPILER_ID_RUN TRUE)
set(CMAKE_CXX_COMPILER_FORCED TRUE)


# EOF
