#
#  CMake routine: Auto-detect package name and version from directory
#                 (based on directory layout convention)
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
# Package meta-information
#----------------------------------------------------------------------------


# detect the canonical path of the package

execute_process(COMMAND python $ENV{TOOLBOSCORE_ROOT}/include/ToolBOSCore/BuildSystem/CanonicalPath.py
                OUTPUT_VARIABLE CANONICAL_PATH
                OUTPUT_STRIP_TRAILING_WHITESPACE
                WORKING_DIRECTORY ${CMAKE_HOME_DIRECTORY})

if("${CANONICAL_PATH}" STREQUAL "")
    message(FATAL_ERROR "Unable to determine canonical path!")
endif()

string(REGEX MATCH "(.*)/(.+)/(.+)" DUMMYVAR ${CANONICAL_PATH})
message( "\nTop-level directory:    ${CMAKE_HOME_DIRECTORY}" )
message( "Package category:       ${CMAKE_MATCH_1}" )
message( "Package name:           ${CMAKE_MATCH_2}" )
message( "Package full version:   ${CMAKE_MATCH_3}" )

set(PACKAGE_NAME    ${CMAKE_MATCH_2} CACHE STRING "Name of the package, e.g. ToolBOSCore")
set(PACKAGE_VERSION ${CMAKE_MATCH_3} CACHE STRING "<Major.Minor> version, e.g. 2.0")
mark_as_advanced(PACKAGE_NAME)
mark_as_advanced(PACKAGE_VERSION)


# split the version into major / minor part

string(REGEX MATCH "(.+)[.](.+)" DUMMYVAR ${PACKAGE_VERSION})
message( "Major version:          ${CMAKE_MATCH_1}" )
message( "Minor version:          ${CMAKE_MATCH_2}" )


# pass the string-length of the source directory as compiler define,
# used to compute correct filename in ANY_LOG_CPP macro (TBCORE-2135)

string(LENGTH "${CMAKE_SOURCE_DIR}/" BST_BASE_PATH_LENGTH)
add_definitions("-DBST_BASE_PATH_LENGTH=${BST_BASE_PATH_LENGTH}")


# set the corresponding CMake-internal variables

project(${PACKAGE_NAME})
set(TARGET_VERSION_MAJOR ${CMAKE_MATCH_1} CACHE STRING "Major version number, e.g. '2' if version is 2.0")
set(TARGET_VERSION_MINOR ${CMAKE_MATCH_2} CACHE STRING "Minor version number, e.g. '0' if version is 2.0")
mark_as_advanced(TARGET_VERSION_MAJOR)
mark_as_advanced(TARGET_VERSION_MINOR)


# EOF
