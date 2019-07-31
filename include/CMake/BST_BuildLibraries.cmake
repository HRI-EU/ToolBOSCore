#
#  CMake routine: Building static and shared libraries
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
# Building libraries
#----------------------------------------------------------------------------


macro(bst_build_libraries FILELIST LIBNAME LINK_LIBRARIES)
    set(_FILELIST "")
    set(_DEFFILE "")

    # ignore filenames starting with "." (likely editor tempfile or so)
    foreach(_FILE_PATH ${FILELIST})
        get_filename_component(BASENAME ${_FILE_PATH} NAME)
        string(SUBSTRING ${BASENAME} 0 1 FIRSTCHAR)

        if(${FIRSTCHAR} STREQUAL ".")
            message("-- Ignoring ${_FILE_PATH} (!)")
        else()
            if("$ENV{VERBOSE}" STREQUAL "TRUE")
                message("-- Found ${_FILE_PATH}")
            endif()

            # check wether or not the caller has provided a def filename
            # and in case we remove it from the target's library list and
            # we set the _DEFFILE variable accordingly
            get_filename_component(FILEEXT ${_FILE_PATH} EXT)
            string(TOLOWER "${FILEEXT}" FILEEXT)
            if(FILEEXT STREQUAL ".def")
                set(_DEFFILE "${_FILE_PATH}")
            else()
                list(APPEND _FILELIST ${_FILE_PATH})
            endif()

            # Detect assembler source and pass it to C compiler
            if(FILEEXT STREQUAL ".S" OR FILEEXT STREQUAL ".s")
                if("$ENV{VERBOSE}" STREQUAL "TRUE")
                    message("-- Found ASM ${_FILE_PATH}, using C compiler")
                endif()
                set_property(SOURCE ${_FILE_PATH} PROPERTY LANGUAGE C)
            endif()
        endif()
    endforeach()


    set(BST_LIBRARY_OUTPUT_PATH ${BST_TOP_LEVEL_DIR}/lib/$ENV{MAKEFILE_PLATFORM})


    if(NOT "${_FILELIST}" STREQUAL "")
        link_directories(${BST_LIBRARY_OUTPUT_PATH})

        # Define the source file basename
        foreach(_FILE_PATH ${_FILELIST})
            get_filename_component(_BASENAME ${_FILE_PATH} NAME)
            set_property(SOURCE ${_FILE_PATH} PROPERTY COMPILE_FLAGS -D__BASENAME_FILE__=\\"${_BASENAME}\\")
        endforeach()


        # The -global target builds only into object all the specified _FILELIST files
        add_library(${LIBNAME}-global OBJECT ${_FILELIST})

        if(BST_BUILD_STATIC_LIBRARIES)
            # Both static and shared libraries are built using the
            # precompiled objects from -global target
            add_library(${LIBNAME}-static STATIC $<TARGET_OBJECTS:${LIBNAME}-global>)
        endif()

        # in case of windows target we must generate the def file from the static .lib
        if(WINDOWS)
            set(WINDOWS_BITS 32)
            if(WIN64)
               set(WINDOWS_BITS 64)
            endif()

            # if def file isn't defined then we default to our name
            if(_DEFFILE STREQUAL "")
                set(_DEFFILE "${BST_LIBRARY_OUTPUT_PATH}/${LIBNAME}.def")
            endif()

            set(TMPFILE "${BST_LIBRARY_OUTPUT_PATH}/${LIBNAME}.tmp")

            # extract raw symbols from library
            add_custom_command(OUTPUT ${TMPFILE}
                               COMMAND dumpbin /SYMBOLS "$<TARGET_FILE:${LIBNAME}-static>" > ${TMPFILE}
                               DEPENDS ${LIBNAME}-global
                               COMMENT "Extracting symbols from ${LIBNAME}"
                               VERBATIM)

            # write public interface to def file
            add_custom_command(OUTPUT ${_DEFFILE}
                               COMMAND python "$ENV{TOOLBOSCORE_ROOT}/include/CMake/DumpWinSymbols.py" -i "${TMPFILE}" -b ${WINDOWS_BITS} -o "${_DEFFILE}"
                               DEPENDS ${TMPFILE}
                               COMMENT "Generating ${_DEFFILE}"
                               VERBATIM)

            # finally make a target from all the -global objects and the generated .def file
            add_library(${LIBNAME}-shared SHARED $<TARGET_OBJECTS:${LIBNAME}-global> ${_DEFFILE})

            # Removed temporary files
            add_custom_command(TARGET ${LIBNAME}-shared POST_BUILD
                               COMMAND ${CMAKE_COMMAND} -E remove -f "${TMPFILE}"
                               COMMENT "Removing temporary files"
                               VERBATIM)

        else()

            if(BST_BUILD_SHARED_LIBRARIES)
                # other system will need only all the -global objects
                add_library(${LIBNAME}-shared SHARED $<TARGET_OBJECTS:${LIBNAME}-global>)
            endif()

        endif()

        if(WINDOWS)
            # MSVC requires an explicit library name with version number
            # to detect that it is a library

            set_target_properties(${LIBNAME}-static PROPERTIES
                                  OUTPUT_NAME lib${LIBNAME}.${TARGET_VERSION_MAJOR}.${TARGET_VERSION_MINOR})

            set_target_properties(${LIBNAME}-shared PROPERTIES
                                    OUTPUT_NAME ${LIBNAME}.${TARGET_VERSION_MAJOR}.${TARGET_VERSION_MINOR})


            # when cross-compiling from Linux we can use symlinks,
            # while on native Windows the files are copied for now :-/

            if(${CMAKE_CROSSCOMPILING} STREQUAL "TRUE")
                set(CMD_SYMLINK ${CMAKE_COMMAND} -E create_symlink)
            else()
                set(CMD_SYMLINK ${CMAKE_COMMAND} -E copy)
            endif()

            add_custom_command(TARGET ${LIBNAME}-shared
                                COMMAND ${CMD_SYMLINK}
                                        ${LIBNAME}.${TARGET_VERSION_MAJOR}.${TARGET_VERSION_MINOR}${CMAKE_LINK_LIBRARY_SUFFIX}
                                        ${LIBNAME}${CMAKE_LINK_LIBRARY_SUFFIX}
                                WORKING_DIRECTORY ${BST_LIBRARY_OUTPUT_PATH})

            add_custom_command(TARGET ${LIBNAME}-static
                                COMMAND ${CMD_SYMLINK}
                                        lib${LIBNAME}.${TARGET_VERSION_MAJOR}.${TARGET_VERSION_MINOR}${CMAKE_LINK_LIBRARY_SUFFIX}
                                        lib${LIBNAME}${CMAKE_LINK_LIBRARY_SUFFIX}
                                WORKING_DIRECTORY ${BST_LIBRARY_OUTPUT_PATH})
        else()
            # do not name output files "libFoo-static" and "libFoo-shared"
            # but "libFoo.a" and "libFoo.so"

            if(BST_BUILD_STATIC_LIBRARIES)
                set_target_properties(${LIBNAME}-static PROPERTIES OUTPUT_NAME ${LIBNAME})
            endif()

            if(BST_BUILD_SHARED_LIBRARIES)
                set_target_properties(${LIBNAME}-shared PROPERTIES OUTPUT_NAME ${LIBNAME})
            endif()


            # on Linux extract debug information to *.syms files
            set(_PACKAGE_LIB_NAME $<TARGET_FILE_NAME:${LIBNAME}-shared>)

            if(BST_BUILD_SHARED_LIBRARIES)
                # check if the shared library build is available
                if(NOT "${BUILD_SHARED_LIBS}" STREQUAL "OFF" AND UNIX)
                    add_custom_command(TARGET ${LIBNAME}-shared
                                    POST_BUILD
                                    WORKING_DIRECTORY ${BST_LIBRARY_OUTPUT_PATH}
                                    COMMENT "Generating debug symbols for shared library ${LIBNAME} ..."

                                    COMMAND ${CMD_OBJCOPY}
                                    ARGS    --only-keep-debug ${_PACKAGE_LIB_NAME} ${_PACKAGE_LIB_NAME}.syms

                                    COMMAND ${CMD_STRIP}
                                    ARGS    -g ${_PACKAGE_LIB_NAME}

                                    COMMAND ${CMD_OBJCOPY}
                                    ARGS    --add-gnu-debuglink=${_PACKAGE_LIB_NAME}.syms ${_PACKAGE_LIB_NAME}

                                    COMMAND chmod
                                    ARGS    a-x ${_PACKAGE_LIB_NAME}.syms)
                endif()
            endif()

        endif()

        set_target_properties(${LIBNAME}-global PROPERTIES

                              ARCHIVE_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                              ARCHIVE_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                              ARCHIVE_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH}

                              LIBRARY_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                              LIBRARY_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                              LIBRARY_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH}

                              RUNTIME_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                              RUNTIME_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                              RUNTIME_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH})

        if(BST_BUILD_STATIC_LIBRARIES)
            set_target_properties(${LIBNAME}-static PROPERTIES

                              ARCHIVE_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                              ARCHIVE_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                              ARCHIVE_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH}

                              LIBRARY_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                              LIBRARY_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                              LIBRARY_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH}

                              RUNTIME_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                              RUNTIME_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                              RUNTIME_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH})

            target_link_libraries(${LIBNAME}-static ${LINK_LIBRARIES})
        endif()

        if(BST_BUILD_SHARED_LIBRARIES)
            set_target_properties(${LIBNAME}-shared PROPERTIES

                              ARCHIVE_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                              ARCHIVE_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                              ARCHIVE_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH}

                              LIBRARY_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                              LIBRARY_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                              LIBRARY_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH}

                              RUNTIME_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                              RUNTIME_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                              RUNTIME_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH}

                              VERSION ${TARGET_VERSION_MAJOR}.${TARGET_VERSION_MINOR})

            target_link_libraries(${LIBNAME}-shared ${LINK_LIBRARIES})
        endif()

    endif()

endmacro()


macro(bst_build_mexfile FILELIST LIBNAME LINK_LIBRARIES)
    if(UNIX)
        add_library(${LIBNAME} SHARED ${FILELIST})
    else()
        add_library(${LIBNAME} SHARED ${FILELIST} $ENV{TOOLBOSCORE_ROOT}/include/CMake/mex.def)
    endif()

    set(BST_LIBRARY_OUTPUT_PATH ${CMAKE_HOME_DIRECTORY}/lib/$ENV{MAKEFILE_PLATFORM})

    set_target_properties(${LIBNAME} PROPERTIES

                          ARCHIVE_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                          ARCHIVE_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                          ARCHIVE_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH}

                          LIBRARY_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                          LIBRARY_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                          LIBRARY_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH}

                          RUNTIME_OUTPUT_DIRECTORY         ${BST_LIBRARY_OUTPUT_PATH}
                          RUNTIME_OUTPUT_DIRECTORY_DEBUG   ${BST_LIBRARY_OUTPUT_PATH}
                          RUNTIME_OUTPUT_DIRECTORY_RELEASE ${BST_LIBRARY_OUTPUT_PATH})

    set_target_properties(${LIBNAME} PROPERTIES PREFIX "")
    set_target_properties(${LIBNAME} PROPERTIES SUFFIX ".${MATLAB_MEX_SUFFIX}")

    target_link_libraries(${LIBNAME} ${LINK_LIBRARIES})

    file(MAKE_DIRECTORY ${BST_LIBRARY_OUTPUT_PATH})

    if(WINDOWS AND DEFINED MATLAB_MEX_EMBED_MANIFEST)
        # On Windows target we want to embed the manifest file in the MEX itself
        # because otherwise Matlab doesn't validate the extension and fails
        add_custom_command(TARGET ${LIBNAME}
                           POST_BUILD
                           COMMAND "mt" -nologo -manifest \"${BST_LIBRARY_OUTPUT_PATH}/${LIBNAME}.${MATLAB_MEX_SUFFIX}.manifest\" -outputresource:\"${BST_LIBRARY_OUTPUT_PATH}/${LIBNAME}.${MATLAB_MEX_SUFFIX}\;\#2\"
                           COMMENT "Embedding manifest into ${LIBNAME}"
                           WORKING_DIRECTORY ${BST_LIBRARY_OUTPUT_PATH})
    endif()

endmacro()


# compiles all listed files into one mexfile each
macro(bst_build_mexfiles FILELIST LINK_LIBRARIES)

    link_directories(${BST_LIBRARY_OUTPUT_PATH})

    foreach(_FILE_PATH ${FILELIST})

        # target name = basename of file
        get_filename_component(FILENAME_NOEXT ${_FILE_PATH} NAME_WE)
        bst_build_mexfile(${_FILE_PATH} ${FILENAME_NOEXT} "${LINK_LIBRARIES}")

    endforeach()

endmacro()


# create Matlab wrappers (MEX files)
macro(bst_build_wrappers)

    if("${BST_LINK_MODE}" STREQUAL "STATIC")
        if(TARGET ${PROJECT_NAME}-static)
            set(BST_MATLAB_LIBRARIES ${BST_LIBRARIES_STATIC}
                                     ${BST_LIBRARY_OUTPUT_PATH}/lib${PROJECT_NAME}${CMAKE_STATIC_LIBRARY_SUFFIX})
        else()
            set(BST_MATLAB_LIBRARIES ${BST_LIBRARIES_STATIC})
        endif()
    else()
        set(BST_MATLAB_LIBRARIES ${BST_LIBRARIES_SHARED})
    endif()

    file(GLOB WRAPPER_FILES wrapper/*.c wrapper/*.cpp)

    foreach(_FILE_PATH ${WRAPPER_FILES})
        get_filename_component(BASENAME ${_FILE_PATH} NAME_WE)
        bst_build_mexfile("wrapper/${BASENAME}" "${BASENAME}" "${BST_MATLAB_LIBRARIES}")

        if("${BST_LINK_MODE}" STREQUAL "STATIC")

            set_target_properties(${BASENAME} PROPERTIES LINK_SEARCH_START_STATIC 1)
            set_target_properties(${BASENAME} PROPERTIES LINK_SEARCH_END_STATIC 1)

            if(NOT WINDOWS)
                set(CMAKE_EXE_LINKER_FLAGS "-static-libgcc -static-libstdc++")
            endif()

            # for static compilation we need to list the high-level packages first,
            # and the low-level (f.i. ToolBOSCore or so) as last, given that we use
            # list(APPEND BST_LIBRARIES_STATIC /path/to/libFoo.a starting from the
            # low-level packages we thus need to revert this list
            #
            set(LINK_LIBRARIES_REVERSE ${BST_LIBRARIES_STATIC})
            list(REVERSE LINK_LIBRARIES_REVERSE)

            add_dependencies(${BASENAME} ${PROJECT_NAME}-static)
            target_link_libraries(${BASENAME} "${LINK_LIBRARIES_REVERSE}")

        else()

            add_dependencies(${BASENAME} ${PROJECT_NAME}-shared)
            target_link_libraries(${BASENAME} ${PROJECT_NAME}-shared)

        endif()

    endforeach()

    # copy Matlab scripts into wrapper output directory to have them all together

    file(GLOB MATLAB_FILES wrapper/*.m)

    foreach(_FILE_PATH ${MATLAB_FILES})
        add_custom_command(TARGET "${PROJECT_NAME}-shared"
                           POST_BUILD
                           COMMAND ${CMAKE_COMMAND}
                           ARGS -E copy ${_FILE_PATH}
                                        ${BST_LIBRARY_OUTPUT_PATH})
    endforeach()

endmacro()


# An RTMaps package actually is a shared library with ".pck" extension and
# a binary blob (signature) near the end. This blob can be added using a
# tool provided by Intempora. However it requires a valid RTMaps license.
macro(bst_build_rtmaps_package FILELIST LIBNAME LINK_LIBRARIES)

    bst_build_libraries("${FILELIST}" "${LIBNAME}" "${LINK_LIBRARIES}")

    add_custom_command(TARGET "${LIBNAME}-shared"
                       POST_BUILD

                       COMMAND ${CMAKE_COMMAND}
                       ARGS    -E copy ${CMAKE_HOME_DIRECTORY}/lib/$ENV{MAKEFILE_PLATFORM}/lib${LIBNAME}.so
                                       ${CMAKE_HOME_DIRECTORY}/lib/$ENV{MAKEFILE_PLATFORM}/${LIBNAME}.pck

                       COMMAND $ENV{TOOLBOSCORE_ROOT}/include/RTMaps/AddDRMSignature.sh
                       ARGS    ${CMAKE_HOME_DIRECTORY}/CMakeLists.txt
                               ${CMAKE_HOME_DIRECTORY}/${PROJECT_NAME}.pckinfo
                               ${CMAKE_HOME_DIRECTORY}/lib/$ENV{MAKEFILE_PLATFORM}/${LIBNAME}.pck

                       COMMENT "Adding RTMaps DRM signature")

endmacro()


# EOF
