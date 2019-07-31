#
#  CMake build settings
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


#----------------------------------------------------------------------------
# Standard header + common routines
#----------------------------------------------------------------------------


cmake_minimum_required(VERSION 2.8.8)

find_package(BuildSystemTools)

set(BST_INSTALL_CATEGORY Applications)


#----------------------------------------------------------------------------
# Dependencies
#----------------------------------------------------------------------------

# please include here the packageVar.cmake files of the packages this one
# depends on, e.g:
# bst_find_package(DevelopmentTools/ToolBOSCore/2.0)

bst_find_package(DevelopmentTools/ToolBOSCore/2.0)


#----------------------------------------------------------------------------
# Build specification
#----------------------------------------------------------------------------


include_directories(${CMAKE_HOME_DIRECTORY}/examples)


file(GLOB EXE_FILES bin/*.c)
bst_build_executables("${EXE_FILES}" "${BST_LIBRARIES_SHARED}")

file(GLOB HELLOWORLD_FILES examples/*.c)
bst_build_executable(HelloWorld ${HELLOWORLD_FILES} "${BST_LIBRARIES_SHARED}")


# EOF
