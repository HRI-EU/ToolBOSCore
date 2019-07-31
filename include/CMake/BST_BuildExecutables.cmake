#
#  CMake routine: Building executables
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
# Building executables
#----------------------------------------------------------------------------


# compiles all listed files into one executable with the given name
macro(bst_build_executable TARGET_NAME FILELIST LINK_LIBRARIES)

    link_directories(${BST_TOP_LEVEL_DIR}/lib/$ENV{MAKEFILE_PLATFORM})


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

        # Define the source file basename
        get_filename_component(_BASENAME ${_FILE_PATH} NAME)
        set_property(SOURCE ${_FILE_PATH} PROPERTY COMPILE_FLAGS -D__BASENAME_FILE__=\\"${_BASENAME}\\")

        get_filename_component(_FILENAME_NOEXT ${_FILE_PATH} NAME_WE)
        get_filename_component(FILENAME       ${_FILE_PATH} NAME   )

        # find relative directory to source file
        file(RELATIVE_PATH _TMP ${CMAKE_HOME_DIRECTORY} ${_FILE_PATH})
        get_filename_component(DIR "${_TMP}" DIRECTORY)

    endforeach()


    add_executable(${TARGET_NAME} ${_FILELIST})

    set_target_properties(${TARGET_NAME} PROPERTIES
                          RUNTIME_OUTPUT_DIRECTORY         ${BST_TOP_LEVEL_DIR}/${DIR}/$ENV{MAKEFILE_PLATFORM}
                          RUNTIME_OUTPUT_DIRECTORY_DEBUG   ${BST_TOP_LEVEL_DIR}/${DIR}/$ENV{MAKEFILE_PLATFORM}
                          RUNTIME_OUTPUT_DIRECTORY_RELEASE ${BST_TOP_LEVEL_DIR}/${DIR}/$ENV{MAKEFILE_PLATFORM})

    if("${BST_LINK_MODE}" STREQUAL "STATIC")

        # link against own package library, if existing

        if(TARGET ${PROJECT_NAME}-static)
            set(_PACKAGE_LIB_PATH ${BST_LIBRARY_OUTPUT_PATH}/lib${PROJECT_NAME}${CMAKE_STATIC_LIBRARY_SUFFIX})
            add_dependencies(${TARGET_NAME} ${PROJECT_NAME}-static)
        else()
            set(_PACKAGE_LIB_PATH "")
        endif()

        set_target_properties(${TARGET_NAME} PROPERTIES LINK_SEARCH_START_STATIC 1)
        set_target_properties(${TARGET_NAME} PROPERTIES LINK_SEARCH_END_STATIC 1)

        if(NOT WINDOWS)
            set(CMAKE_EXE_LINKER_FLAGS "-static-libgcc -static-libstdc++")
        endif()


        # for static compilation we need to list the high-level packages first,
        # and the low-level (f.i. ToolBOSCore or so) as last, given that we use
        # list(APPEND BST_LIBRARIES_STATIC /path/to/libFoo.a starting from the
        # low-level packages we thus need to revert this list
        #
        set(LINK_LIBRARIES_REVERSE ${LINK_LIBRARIES} ${_PACKAGE_LIB_PATH})
        list(REVERSE LINK_LIBRARIES_REVERSE)

        target_link_libraries(${TARGET_NAME} ${LINK_LIBRARIES_REVERSE})

    else()

        # link against own package library, if existing
        if(TARGET ${PROJECT_NAME}-shared)
            add_dependencies(${TARGET_NAME} ${PROJECT_NAME}-shared)
            link_directories(${LINK_DIRECTORIES} ${BST_LIBRARY_OUTPUT_PATH})
            target_link_libraries(${TARGET_NAME} ${PROJECT_NAME})
        endif()

        target_link_libraries(${TARGET_NAME} ${LINK_LIBRARIES})

    endif()

endmacro()


# compiles all listed files into one executable each
macro(bst_build_executables FILELIST LINK_LIBRARIES)

    link_directories(${BST_TOP_LEVEL_DIR}/lib/$ENV{MAKEFILE_PLATFORM})

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

    endforeach()

endmacro()


# EOF
