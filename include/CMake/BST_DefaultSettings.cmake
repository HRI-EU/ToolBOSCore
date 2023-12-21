#
#  CMake routine: standard compiler settings
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


message( "CMake generator:        ${CMAKE_GENERATOR}" )


#----------------------------------------------------------------------------
# Build type (release / debug)
#----------------------------------------------------------------------------


if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release")
endif()

set(TOOLBOSCORE_BUILDS RELEASE DEBUG)
string(TOUPPER ${CMAKE_BUILD_TYPE} BUILD_TYPE)
list(FIND TOOLBOSCORE_BUILDS ${BUILD_TYPE} BUILD_TYPE_PRESENT)


set(BST_BUILD_STATIC_LIBRARIES TRUE)
set(BST_BUILD_SHARED_LIBRARIES TRUE)


#----------------------------------------------------------------------------
# Compiler frontend
#----------------------------------------------------------------------------


if(UNIX AND "${CMAKE_CROSSCOMPILING}" STREQUAL "FALSE")

    set(ICECC_ROOT /usr/lib/icecc/bin)


    if("$ENV{BST_USE_CLANG}" STREQUAL "TRUE")

        set(CMAKE_C_COMPILER              clang)
        set(CMAKE_CXX_COMPILER            clang++)
        set(BST_USE_CLANG                 TRUE)
        set(BST_USE_ICECC                 FALSE)
        set(BST_USE_GCC                   FALSE)

        message( "Clang/LLVM enabled:     yes" )
        message( "IceCC enabled:          no" )

    elseif(NOT "$ENV{BST_USE_ICECC}" STREQUAL "FALSE")

        if(EXISTS "${ICECC_ROOT}")

            set(CMAKE_C_COMPILER              ${ICECC_ROOT}/gcc)
            set(CMAKE_CXX_COMPILER            ${ICECC_ROOT}/g++)
            set(BST_USE_CLANG                 FALSE)
            set(BST_USE_ICECC                 TRUE)
            set(BST_USE_GCC                   TRUE)

            message( "Clang/LLVM enabled:     no" )
            message( "IceCC enabled:          yes" )

        else()

            set(BST_USE_CLANG                 FALSE)
            set(BST_USE_ICECC                 FALSE)
            set(BST_USE_GCC                   TRUE)

            message( "Clang/LLVM enabled:     no" )
            message( "IceCC enabled:          no (not installed)" )

        endif()

    else()
        set(CMAKE_C_COMPILER              gcc)
        set(CMAKE_CXX_COMPILER            g++)
        set(BST_USE_CLANG                 FALSE)
        set(BST_USE_ICECC                 FALSE)
        set(BST_USE_GCC                   TRUE)

        message( "Clang/LLVM enabled:     no" )
        message( "IceCC enabled:          no" )

    endif()

endif()


# Generate a file 'compile_commands.json' with all build commands.
# This file is used by some SQ checkers which do C/C++ file inspection.

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)


#----------------------------------------------------------------------------
# Compiler flags
#----------------------------------------------------------------------------


if(BST_USE_CLANG)
    set(BST_DEFAULT_FLAGS_LINUX "-ggdb -Wall -Wextra -pedantic -fPIC -Wno-long-long -Wno-variadic-macros -Wfloat-equal")
else()
    set(BST_DEFAULT_FLAGS_LINUX "-ggdb -Wall -Wextra -pedantic -fPIC -rdynamic -Wno-long-long -Wno-variadic-macros -Wfloat-equal")
endif()


set(BST_DEFAULT_FLAGS_WINDOWS "/GF /MD /GS- /Gd /Gy /Oi")


if("$ENV{MAKEFILE_PLATFORM}" STREQUAL "")

    message(FATAL_ERROR "Please set the MAKEFILE_PLATFORM environment variable.")

elseif("$ENV{MAKEFILE_PLATFORM}" STREQUAL "bionic64" OR
       "$ENV{MAKEFILE_PLATFORM}" STREQUAL "focal64"  OR
       "$ENV{MAKEFILE_PLATFORM}" STREQUAL "jammy64")

    set(CMAKE_C_FLAGS           "${CMAKE_C_FLAGS} ${BST_DEFAULT_FLAGS_LINUX} -m64 -std=c99")
    set(CMAKE_CXX_FLAGS         "${CMAKE_CXX_FLAGS} ${BST_DEFAULT_FLAGS_LINUX} -m64")
    set(BST_DEFAULT_DEFINES     "-D__64BIT__ -D__linux__")
    add_definitions(${BST_DEFAULT_DEFINES})

elseif("$ENV{MAKEFILE_PLATFORM}" STREQUAL "bionic32armv7" OR
       "$ENV{MAKEFILE_PLATFORM}" STREQUAL "focal32armv7")

    set(CMAKE_C_FLAGS           "${CMAKE_C_FLAGS} ${BST_DEFAULT_FLAGS_LINUX} -march=armv7-a -std=c99")
    set(CMAKE_CXX_FLAGS         "${CMAKE_CXX_FLAGS} ${BST_DEFAULT_FLAGS_LINUX} -march=armv7-a")
    set(BST_DEFAULT_DEFINES     "-D__32BIT__ -D__linux__ -D__arm__ -D__armv7__")
    add_definitions(${BST_DEFAULT_DEFINES})

elseif("$ENV{MAKEFILE_PLATFORM}" STREQUAL "peakcan")

    set(PEAKCAN_RUN_MODE "ROM_RUN")
    set(PEAKCAN_MCU "arm7tdmi-s")
    set(PEAKCAN_SUBMDL "Flash")
    set(PEAKCAN_FORMAT "ihex")

    set(PEAKCAN_DEFAULT_CFLAGS "-O2 -Wall -Wcast-align -Wcast-qual -Wimplicit -Wpointer-arith -Wswitch -Wredundant-decls -Wreturn-type -Wshadow -Wunused -Wno-long-long -Wno-variadic-macros -Wfloat-equal -Wstrict-prototypes -Wmissing-declarations -Wmissing-prototypes -Wnested-externs -gdwarf-2 -mcpu=${PEAKCAN_MCU}")
    set(CMAKE_C_FLAGS           "${CMAKE_C_FLAGS} ${PEAKCAN_DEFAULT_CFLAGS} -std=c99")
    set(CMAKE_CXX_FLAGS         "${CMAKE_CXX_FLAGS} ${PEAKCAN_DEFAULT_CFLAGS}")
    set(BST_DEFAULT_DEFINES     "-D__32BIT__ -D__peakcan__ -D__arm__ -D__armv7tdmi__")
    set(CMAKE_EXE_LINKER_FLAGS  "-nostartfiles -lc -lgcc -T$ENV{TOOLBOSCORE_ROOT}/include/CMake/Platform/Peakcan_${PEAKCAN_SUBMDL}.ld")
    add_definitions(${BST_DEFAULT_DEFINES} "-D${PEAKCAN_RUN_MODE}")

elseif("$ENV{MAKEFILE_PLATFORM}" STREQUAL "phyboardwega")

    set(CMAKE_C_FLAGS           "${CMAKE_C_FLAGS} ${BST_DEFAULT_FLAGS_LINUX} -std=c99 -mfpu=neon -mfloat-abi=hard")
    set(CMAKE_CXX_FLAGS         "${CMAKE_CXX_FLAGS} ${BST_DEFAULT_FLAGS_LINUX}")
    set(BST_DEFAULT_DEFINES     "-D__32BIT__ -D__linux__ -D__arm__")
    add_definitions(${BST_DEFAULT_DEFINES})

elseif(WIN32) # AND CMAKE_CL_64 EQUAL 0)

    set(CMAKE_EXE_LINKER_FLAGS_DEBUG     "/DEBUG /NODEFAULTLIB:MSVCRT")
    set(CMAKE_MODULE_LINKER_FLAGS_DEBUG "/DEBUG")
    set(CMAKE_SHARED_LINKER_FLAGS_DEBUG "/DEBUG")
    set(CMAKE_STATIC_LINKER_FLAGS_DEBUG "/DEBUG")
    set(CMAKE_C_FLAGS           "${BST_DEFAULT_FLAGS_WINDOWS} /GF /MD /GS- /Gd /Gy /fp:precise /arch:SSE2")
    set(CMAKE_C_FLAGS_RELEASE   "-DNDEBUG")
    set(CMAKE_C_FLAGS_DEBUG     "-D_DEBUG /Od /Zi /MDd")
    set(CMAKE_CXX_FLAGS         "${BST_DEFAULT_FLAGS_WINDOWS} /GR- /EHsc /GF /MD /GS- /Gd /Gy /fp:precise /arch:SSE2")
    set(CMAKE_CXX_FLAGS_RELEASE "-DNDEBUG")
    set(CMAKE_CXX_FLAGS_DEBUG   "-D_DEBUG /Od /Zi /MDd")
    set(BST_DEFAULT_DEFINES     "-D__32BIT__ -D__win32__ -D__windows__ -D__MSVC__ -D__msvc__ -D_CRT_SECURE_NO_DEPRECATE -D_CRT_NONSTDC_NO_DEPRECATE")
    add_definitions(${BST_DEFAULT_DEFINES})

elseif(WIN64) # AND CMAKE_CL_64)

    set(CMAKE_EXE_LINKER_FLAGS_DEBUG     "/DEBUG /NODEFAULTLIB:MSVCRT")
    set(CMAKE_MODULE_LINKER_FLAGS_DEBUG "/DEBUG")
    set(CMAKE_SHARED_LINKER_FLAGS_DEBUG "/DEBUG")
    set(CMAKE_STATIC_LINKER_FLAGS_DEBUG "/DEBUG")
    set(CMAKE_C_FLAGS           "${BST_DEFAULT_FLAGS_WINDOWS} /GF /MD /GS- /Gd /Gy /fp:precise")
    set(CMAKE_C_FLAGS_RELEASE   "-DNDEBUG")
    set(CMAKE_C_FLAGS_DEBUG     "-D_DEBUG /Od /Zi /MDd")
    set(CMAKE_CXX_FLAGS         "${BST_DEFAULT_FLAGS_WINDOWS} /GR- /EHsc /GF /MD /GS- /Gd /Gy /fp:precise")
    set(CMAKE_CXX_FLAGS_RELEASE "-DNDEBUG")
    set(CMAKE_CXX_FLAGS_DEBUG   "-D_DEBUG /Od /Zi /MDd")
    set(BST_DEFAULT_DEFINES     "-D__64BIT__ -D__win64__ -D_WIN64 -D__windows__ -D__MSVC__ -D__msvc__ -D_CRT_SECURE_NO_DEPRECATE -D_CRT_NONSTDC_NO_DEPRECATE")
    add_definitions(${BST_DEFAULT_DEFINES})

else()

    message("Unsupported platform, please check your MAKEFILE_PLATFORM or contact ToolBOS support")

endif()

if("${CMD_HEX2BIN}" STREQUAL "")
    set(CMD_HEX2BIN   "hex2bin")
endif()


if(UNIX)
    if("${CMD_OBJCOPY}" STREQUAL "")
        set(CMD_OBJCOPY "objcopy")
    endif()

    if("${CMD_STRIP}" STREQUAL "")
        set(CMD_STRIP   "strip")
    endif()

    set(CMAKE_C_FLAGS_RELEASE   "-O2 -fstack-protector")
    set(CMAKE_C_FLAGS_DEBUG     "-O0 -fstack-protector-all")

    set(CMAKE_CXX_FLAGS_RELEASE "-O2 -fstack-protector")
    set(CMAKE_CXX_FLAGS_DEBUG   "-O0 -fstack-protector-all")
endif()


# "skip rpath" option when compiling:
#
# TRUE:  do skip rpath = always rely on LD_LIBRARY_PATH
#
# FALSE: do not skip = encode library paths into binaries, this speeds-up
#        the application launch time and does not require LD_LIBRARY_PATH
#        but will make binaries contain references into the developer's
#        working copy, thus other people who launch from SIT don't benefit
#        from it
#
set(CMAKE_SKIP_RPATH TRUE)


#----------------------------------------------------------------------------
# Default paths
#----------------------------------------------------------------------------


# locations where to search for headerfiles:

if(EXISTS ${CMAKE_HOME_DIRECTORY}/src)
    include_directories(${CMAKE_HOME_DIRECTORY}/src)
endif()


# EOF
