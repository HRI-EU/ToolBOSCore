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

set(BST_INSTALL_CATEGORY Libraries)


#----------------------------------------------------------------------------
# Dependencies
#----------------------------------------------------------------------------


# please include here the packages this one depends on
# (one bst_find_package() per dependency), e.g:
# bst_find_package(DevelopmentTools/ToolBOSCore/3.0)

bst_find_package(DevelopmentTools/ToolBOSCore/3.0)


#----------------------------------------------------------------------------
# Build specification
#----------------------------------------------------------------------------


file(GLOB SRC_FILES src/*.c src/*.cpp)

bst_build_libraries("${SRC_FILES}" "${PROJECT_NAME}" "${BST_LIBRARIES_SHARED}")


file(GLOB EXE_FILES bin/*.c bin/*.cpp examples/*.c examples/*.cpp
                    test/*.c test/*.cpp)

bst_build_executables("${EXE_FILES}" "${BST_LIBRARIES_SHARED}")


# EOF
