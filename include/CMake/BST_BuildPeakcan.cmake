#
#  CMake macros for PCAN-Router image creation
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


# compiles all listed files into one executable each
macro(bst_build_peakcan FILELIST LINK_LIBRARIES)

    link_directories(${CMAKE_HOME_DIRECTORY}/lib/$ENV{MAKEFILE_PLATFORM})

    set(_FILELIST "")

    # ignore filenames starting with "." (likely editor tempfile or so)
    foreach(_FILE_PATH ${FILELIST})
        get_filename_component(_BASENAME ${_FILE_PATH} NAME)
        string(SUBSTRING ${_BASENAME} 0 1 _FIRSTCHAR)

        if(${_FIRSTCHAR} STREQUAL ".")
            message("-- Ignoring ${_FILE_PATH} (!)")
        else()
            if("$ENV{VERBOSE}" STREQUAL "TRUE")
                message("-- Found ${_FILE_PATH}")
            endif()

            list(APPEND _FILELIST ${_FILE_PATH})
        endif()
    endforeach()


    foreach(_FILE_PATH ${_FILELIST})

        # target name = basename of file
        get_filename_component(_FILENAME_NOEXT ${_FILE_PATH} NAME_WE)
        bst_build_executable(${_FILENAME_NOEXT} ${_FILE_PATH} "${LINK_LIBRARIES}")
        get_target_property(BINARY_DIR ${_FILENAME_NOEXT} RUNTIME_OUTPUT_DIRECTORY)

        add_custom_command(TARGET ${_FILENAME_NOEXT}
                           POST_BUILD
                           WORKING_DIRECTORY ${BINARY_DIR}
                           COMMENT "Generating Peakcan flash image for ${_FILENAME_NOEXT} ..."

                           COMMAND ${CMD_OBJCOPY}
                           ARGS -Oihex ${_FILENAME_NOEXT} ${_FILENAME_NOEXT}.hex

                           COMMAND ${CMD_HEX2BIN}
                           ARGS -s 0000 ${_FILENAME_NOEXT}.hex)

    endforeach()

endmacro()


# EOF
