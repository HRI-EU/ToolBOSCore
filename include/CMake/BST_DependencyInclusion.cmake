#
#  CMake routine: dependency inclusion
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


if(NOT DEFINED BST_INCLUDED_PACKAGES)
  set(BST_INCLUDED_PACKAGES "")
endif()


macro(bst_find_package PACKAGE)

    # if package name contains a slash, we assume it is a canonical path
    # ("SIT package"), if not found we redirect to the native find_package()

    string(FIND "${PACKAGE}" "/" SLASH_FOUND)

    if("${SLASH_FOUND}" STREQUAL "-1")

        find_package(${PACKAGE})

    else("${SLASH_FOUND}" STREQUAL "-1")

        list(FIND BST_INCLUDED_PACKAGES "${PACKAGE}" PACKAGE_FOUND)

        if(${PACKAGE_FOUND} EQUAL -1)

            set(INCLUDED_FILENAME $ENV{SIT}/${PACKAGE}/packageVar.cmake)

            if(NOT EXISTS "$ENV{SIT}/${PACKAGE}")
               message(FATAL_ERROR
                       "\n$ENV{SIT}/${PACKAGE}: No such file or directory\n"
                       "--> ${PACKAGE}: No such package in this SIT\n--> Maybe UpdateProxyDir.py needed?\n")
            elseif(EXISTS "${INCLUDED_FILENAME}")
                message("including package:      sit://${PACKAGE}")
                include("${INCLUDED_FILENAME}")
                list(APPEND BST_INCLUDED_PACKAGES "${PACKAGE}")
            else()
                message(FATAL_ERROR
                        "\n${INCLUDED_FILENAME} does not exist. "
                        "Most likely the package ${PACKAGE} was not properly "
                        "installed into SIT.\n\n")
            endif()

        #else()
            #message("already included:       sit://${PACKAGE}")
        endif()

    endif()

endmacro()


# EOF
