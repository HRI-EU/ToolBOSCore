#
#  CMake toolchain file for cross-compiling from Linux to Windows using WINE
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


# prefer our modified CMake modules (such as UseJava.cmake or
# Windows-MSVC.cmake) over those from CMake distribution
cmake_policy(SET CMP0011 OLD)    # no policy scope
cmake_policy(SET CMP0017 OLD)    # prefer our tweaked CMake modules

if("$ENV{COMPILER}" STREQUAL "vs2010" OR "$ENV{COMPILER}" STREQUAL "vs2012")
    set(CMAKE_SYSTEM_NAME Windows)
    set(CMAKE_C_COMPILER   $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/1.4/bin/cl)
    set(CMAKE_CXX_COMPILER $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/1.4/bin/cl)
    set(CMAKE_RC_COMPILER  $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/1.4/bin/rc)
    set(CMAKE_C_COMPILER_VERSION   9.0)
    set(CMAKE_CXX_COMPILER_VERSION 9.0)
    set(CMAKE_FIND_ROOT_PATH $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/1.4/bin)
    set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
    set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
    set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
elseif("$ENV{COMPILER}" STREQUAL "vs2017")
    set(CMAKE_SYSTEM_NAME Windows)
    set(CMAKE_C_COMPILER   $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/5.0/bin/cl)
    set(CMAKE_CXX_COMPILER $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/5.0/bin/cl)
    set(CMAKE_RC_COMPILER  $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/5.0/bin/rc)
    set(CMAKE_C_COMPILER_VERSION   9.0)
    set(CMAKE_CXX_COMPILER_VERSION 9.0)
    set(CMAKE_FIND_ROOT_PATH $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/5.0/bin)
    set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
    set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
    set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
else()
  message(FATAL_ERROR "Unsupported compiler $ENV{COMPILER}")
endif()


# EOF
