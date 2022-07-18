#
#  CMake build settings
#
#  Copyright (c) Honda Research Institute Europe GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#


#----------------------------------------------------------------------------
# Standard header + common routines
#----------------------------------------------------------------------------


cmake_minimum_required(VERSION 2.8.8)

find_package(BuildSystemTools)


#----------------------------------------------------------------------------
# Dependencies
#----------------------------------------------------------------------------


# please include here the packages this one depends on
# (one bst_find_package() per dependency), e.g:
# bst_find_package(Libraries/ToolBOSLib/3.1)

bst_find_package(Libraries/ToolBOSLib/4.0)
bst_find_package(External/cutest/1.5)


#----------------------------------------------------------------------------
# Build specification
#----------------------------------------------------------------------------


file(GLOB SRC_FILES src/*.c src/*.cpp)

bst_build_libraries("${SRC_FILES}" "${PROJECT_NAME}" "${BST_LIBRARIES_SHARED}")


file(GLOB EXE_FILES bin/*.c bin/*.cpp examples/*.c examples/*.cpp
                    test/*.c test/*.cpp)

bst_build_executables("${EXE_FILES}" "${BST_LIBRARIES_SHARED}")


# EOF
