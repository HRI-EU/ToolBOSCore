#
#  CMake toolchain file for cross-compiling from Linux to Windows using MinGW
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


SET(CMAKE_SYSTEM_NAME Windows)

if( "$ENV{MINGW_PLATFORM}" STREQUAL "mingw32" )
  set( COMPILER_PREFIX "i686-w64-mingw32" )
elseif( "$ENV{MINGW_PLATFORM}" STREQUAL "mingw64" )
  set( COMPILER_PREFIX "x86_64-w64-mingw32" )
else()
  message( FATAL_ERROR "Unsupported platform $ENV{MINGW_PLATFORM}" )
endif()

find_program( CMAKE_RC_COMPILER  NAMES ${COMPILER_PREFIX}-windres )
find_program( CMAKE_C_COMPILER   NAMES ${COMPILER_PREFIX}-gcc )
find_program( CMAKE_AR           NAMES ar )
find_program( CMAKE_CXX_COMPILER NAMES ${COMPILER_PREFIX}-g++ )


SET( CMAKE_FIND_ROOT_PATH  /usr/${COMPILER_PREFIX} )

set( CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER )
set( CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY )
set( CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY )

# EOF
