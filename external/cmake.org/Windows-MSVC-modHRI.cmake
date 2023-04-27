#=============================================================================
# Copyright 2001-2012 Kitware, Inc.
#
# Distributed under the OSI-approved BSD License (the "License");
# see accompanying file Copyright.txt for details.
#
# This software is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the License for more information.
#=============================================================================
# (To distribute this file outside of CMake, substitute the full
#  License text for the above reference.)

#
# CMake toolchain file for cross-compiling from Linux to Windows using MSVC
# under WINE. This file is based upon of Cmake's original Windows-MSVC.cmate
# template file coming from Cmake's v3.2.2
#

include_guard(GLOBAL)

cmake_policy(PUSH)
cmake_policy(SET CMP0054 NEW)

# This is our preferred setting for a MSVC cross-compilation platform under Windows
# using Wine

if("$ENV{COMPILER}" STREQUAL "vs2010" OR "$ENV{COMPILER}" STREQUAL "vs2012")
    set(CMAKE_SYSTEM_NAME Windows)
    set(CMAKE_C_COMPILER   $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/1.4/bin/cl)
    set(CMAKE_CXX_COMPILER $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/1.4/bin/cl)
    set(CMAKE_RC_COMPILER  $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/1.4/bin/rc)
    set(CMAKE_AR  $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/1.4/bin/lib)
    set(CMAKE_C_COMPILER_VERSION   9.0)
    set(CMAKE_CXX_COMPILER_VERSION 9.0)
    set(CMAKE_FIND_ROOT_PATH $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/1.4/bin)
    set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
    set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
    set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
elseif("$ENV{COMPILER}" STREQUAL "vs2017")
    set(CMAKE_SYSTEM_NAME Windows)
    set(CMAKE_C_COMPILER   $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/8.0/bin/cl)
    set(CMAKE_CXX_COMPILER $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/8.0/bin/cl)
    set(CMAKE_RC_COMPILER  $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/8.0/bin/rc)
    set(CMAKE_AR  $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/8.0/bin/lib)
    set(CMAKE_C_COMPILER_VERSION   9.0)
    set(CMAKE_CXX_COMPILER_VERSION 9.0)
    set(CMAKE_FIND_ROOT_PATH $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/8.0/bin)
    set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
    set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
    set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
else()
  message(FATAL_ERROR "Unsupported compiler $ENV{COMPILER}")
endif()


set(CMAKE_C_STANDARD_LIBRARIES_INIT "kernel32.lib user32.lib gdi32.lib winspool.lib shell32.lib ole32.lib oleaut32.lib uuid.lib comdlg32.lib advapi32.lib")
set(CMAKE_CXX_STANDARD_LIBRARIES_INIT "${CMAKE_C_STANDARD_LIBRARIES_INIT}")

set(CMAKE_LIBRARY_PATH_FLAG "-LIBPATH:")
set(CMAKE_LINK_LIBRARY_FLAG "")

set(MSVC 1)
set(WINDOWS 1)

# hack: if a new cmake (which uses CMAKE_LINKER) runs on an old build tree
# (where link was hardcoded) and where CMAKE_LINKER isn't in the cache
# and still cmake didn't fail in CMakeFindBinUtils.cmake (because it isn't rerun)
# hardcode CMAKE_LINKER here to link, so it behaves as it did before, Alex
if(NOT DEFINED CMAKE_LINKER)
   set(CMAKE_LINKER link)
endif()

if(CMAKE_VERBOSE_MAKEFILE)
  set(CMAKE_CL_NOLOGO)
else()
  set(CMAKE_CL_NOLOGO "/nologo")
endif()

set(CMAKE_CREATE_WIN32_EXE "/subsystem:windows")
set(CMAKE_CREATE_CONSOLE_EXE "/subsystem:console")

if(CMAKE_GENERATOR MATCHES "Visual Studio 6")
   set (CMAKE_NO_BUILD_TYPE 1)
endif()
if(NOT CMAKE_NO_BUILD_TYPE AND CMAKE_GENERATOR MATCHES "Visual Studio")
  set(CMAKE_NO_BUILD_TYPE 1)
  set(CMAKE_CONFIGURATION_TYPES "Debug;Release;MinSizeRel;RelWithDebInfo" CACHE STRING
     "Semicolon separated list of supported configuration types, only supports Debug, Release, MinSizeRel, and RelWithDebInfo, anything else will be ignored.")
  mark_as_advanced(CMAKE_CONFIGURATION_TYPES)
endif()

# make sure to enable languages after setting configuration types
enable_language(RC)
set(CMAKE_COMPILE_RESOURCE "rc <FLAGS> /fo<OBJECT> <SOURCE>")

if("${CMAKE_GENERATOR}" MATCHES "Visual Studio")
  set(MSVC_IDE 1)
else()
  set(MSVC_IDE 0)
endif()

if(NOT MSVC_VERSION)
  if(CMAKE_C_COMPILER_VERSION)
    set(_compiler_version ${CMAKE_C_COMPILER_VERSION})
  else()
    set(_compiler_version ${CMAKE_CXX_COMPILER_VERSION})
  endif()
  if("${_compiler_version}" MATCHES "^([0-9]+)\\.([0-9]+)")
    math(EXPR MSVC_VERSION "${CMAKE_MATCH_1}*100 + ${CMAKE_MATCH_2}")
  else()
    message(FATAL_ERROR "MSVC compiler version not detected properly: ${_compiler_version}")
  endif()

  set(MSVC10)
  set(MSVC11)
  set(MSVC60)
  set(MSVC70)
  set(MSVC71)
  set(MSVC80)
  set(MSVC90)
  set(CMAKE_COMPILER_2005)
  set(CMAKE_COMPILER_SUPPORTS_PDBTYPE)
  if(NOT "${_compiler_version}" VERSION_LESS 17)
    set(MSVC11 1)
  elseif(NOT  "${_compiler_version}" VERSION_LESS 16)
    set(MSVC10 1)
  elseif(NOT  "${_compiler_version}" VERSION_LESS 15)
    set(MSVC90 1)
  elseif(NOT  "${_compiler_version}" VERSION_LESS 14)
    set(MSVC80 1)
    set(CMAKE_COMPILER_2005 1)
  elseif(NOT  "${_compiler_version}" VERSION_LESS 13.10)
    set(MSVC71 1)
  elseif(NOT  "${_compiler_version}" VERSION_LESS 13)
    set(MSVC70 1)
  else()
    set(MSVC60 1)
    set(CMAKE_COMPILER_SUPPORTS_PDBTYPE 1)
  endif()
endif()

set(CMAKE_COMPILER_SUPPORTS_PDBTYPE 0)
set(MSVC_C_ARCHITECTURE_ID 64)
set(MSVC_CXX_ARCHITECTURE_ID 64)

if(MSVC_C_ARCHITECTURE_ID MATCHES 64 OR MSVC_CXX_ARCHITECTURE_ID MATCHES 64)
  set(CMAKE_CL_64 1)
  set(_CMAKE_MSVC_DLL_ENTRY "-entry:_DllMainCRTStartup")
  set(WIN32 0)
  set(WIN64 1)
else()
  set(CMAKE_CL_64 0)
  set(_CMAKE_MSVC_DLL_ENTRY "-entry:_DllMainCRTStartup@12")
  set(WIN32 1)
endif()
if(CMAKE_FORCE_WIN64 OR CMAKE_FORCE_IA64)
  set(CMAKE_CL_64 1)
  set(WIN32 0)
  set(WIN64 1)
endif()

#if("${MSVC_VERSION}" GREATER 1599)
#  set(MSVC_INCREMENTAL_DEFAULT ON)
#endif()

# default to Debug builds
set(CMAKE_BUILD_TYPE_INIT Debug)

set(_PLATFORM_DEFINES "/DWIN32")

if(MSVC_VERSION GREATER 1310)
  set(_RTC1 " /RTC1")
  set(_FLAGS_CXX " /GR- /EHsc")
  set(CMAKE_C_STANDARD_LIBRARIES_INIT "kernel32.lib user32.lib gdi32.lib winspool.lib shell32.lib ole32.lib oleaut32.lib comdlg32.lib advapi32.lib")
else()
  set(_RTC1 " /GZ")
  set(_FLAGS_CXX " /GR- /GX")
  set(CMAKE_C_STANDARD_LIBRARIES_INIT "kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib odbc32.lib odbccp32.lib")
endif()

set(CMAKE_CXX_STANDARD_LIBRARIES_INIT "${CMAKE_C_STANDARD_LIBRARIES_INIT}")

# executable linker flags
set(CMAKE_LINK_DEF_FILE_FLAG "/DEF:")
# set the machine type
if(MSVC_C_ARCHITECTURE_ID)
  if(MSVC_C_ARCHITECTURE_ID MATCHES "^ARMV.I")
    set(_MACHINE_ARCH_FLAG "/machine:THUMB")
  elseif(_MSVC_C_ARCHITECTURE_FAMILY STREQUAL "ARM64")
    set(_MACHINE_ARCH_FLAG "/machine:ARM64")
  elseif(_MSVC_C_ARCHITECTURE_FAMILY STREQUAL "ARM64EC")
    set(_MACHINE_ARCH_FLAG "/machine:ARM64EC")
  elseif(_MSVC_C_ARCHITECTURE_FAMILY STREQUAL "ARM")
    set(_MACHINE_ARCH_FLAG "/machine:ARM")
  else()
    set(_MACHINE_ARCH_FLAG "/machine:X${MSVC_C_ARCHITECTURE_ID}")
  endif()
elseif(MSVC_CXX_ARCHITECTURE_ID)
  if(MSVC_CXX_ARCHITECTURE_ID MATCHES "^ARMV.I")
    set(_MACHINE_ARCH_FLAG "/machine:THUMB")
  elseif(_MSVC_CXX_ARCHITECTURE_FAMILY STREQUAL "ARM64")
    set(_MACHINE_ARCH_FLAG "/machine:ARM64")
  elseif(_MSVC_CXX_ARCHITECTURE_FAMILY STREQUAL "ARM64EC")
    set(_MACHINE_ARCH_FLAG "/machine:ARM64EC")
  elseif(_MSVC_CXX_ARCHITECTURE_FAMILY STREQUAL "ARM")
    set(_MACHINE_ARCH_FLAG "/machine:ARM")
  else()
    set(_MACHINE_ARCH_FLAG "/machine:X${MSVC_CXX_ARCHITECTURE_ID}")
  endif()
endif()

set(CMAKE_EXE_LINKER_FLAGS_INIT
    "${CMAKE_EXE_LINKER_FLAGS_INIT} /STACK:20000000 ${_MACHINE_ARCH_FLAG}")

# add /debug and /INCREMENTAL:YES to DEBUG and RELWITHDEBINFO also add pdbtype
# on versions that support it
set(MSVC_INCREMENTAL_YES_FLAG "")
#if(NOT MSVC_INCREMENTAL_DEFAULT)
#  set( MSVC_INCREMENTAL_YES_FLAG "/INCREMENTAL:YES")
#else()
#  set(  MSVC_INCREMENTAL_YES_FLAG "/INCREMENTAL" )
#endif()

#if (CMAKE_COMPILER_SUPPORTS_PDBTYPE)
#  set (CMAKE_EXE_LINKER_FLAGS_DEBUG_INIT "/debug /pdbtype:sept ${MSVC_INCREMENTAL_YES_FLAG}")
#  set (CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO_INIT "/debug /pdbtype:sept ${MSVC_INCREMENTAL_YES_FLAG}")
#else ()
#  set (CMAKE_EXE_LINKER_FLAGS_DEBUG_INIT "/debug ${MSVC_INCREMENTAL_YES_FLAG}")
#  set (CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO_INIT "/debug ${MSVC_INCREMENTAL_YES_FLAG}")
#endif ()
# for release and minsize release default to no incremental linking
set(CMAKE_EXE_LINKER_FLAGS_MINSIZEREL_INIT "/INCREMENTAL:NO")
set(CMAKE_EXE_LINKER_FLAGS_RELEASE_INIT "/INCREMENTAL:NO")

# copy the EXE_LINKER flags to SHARED and MODULE linker flags
# shared linker flags
set(CMAKE_SHARED_LINKER_FLAGS_INIT ${CMAKE_EXE_LINKER_FLAGS_INIT})
set(CMAKE_SHARED_LINKER_FLAGS_DEBUG_INIT ${CMAKE_EXE_LINKER_FLAGS_DEBUG_INIT})
set(CMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO_INIT ${CMAKE_EXE_LINKER_FLAGS_DEBUG_INIT})
set(CMAKE_SHARED_LINKER_FLAGS_RELEASE_INIT ${CMAKE_EXE_LINKER_FLAGS_RELEASE_INIT})
set(CMAKE_SHARED_LINKER_FLAGS_MINSIZEREL_INIT ${CMAKE_EXE_LINKER_FLAGS_MINSIZEREL_INIT})
# module linker flags
set(CMAKE_MODULE_LINKER_FLAGS_INIT ${CMAKE_SHARED_LINKER_FLAGS_INIT})
set(CMAKE_MODULE_LINKER_FLAGS_DEBUG_INIT ${CMAKE_SHARED_LINKER_FLAGS_DEBUG_INIT})
set(CMAKE_MODULE_LINKER_FLAGS_RELWITHDEBINFO_INIT ${CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO_INIT})
set(CMAKE_MODULE_LINKER_FLAGS_RELEASE_INIT ${CMAKE_EXE_LINKER_FLAGS_RELEASE_INIT})
set(CMAKE_MODULE_LINKER_FLAGS_MINSIZEREL_INIT ${CMAKE_EXE_LINKER_FLAGS_MINSIZEREL_INIT})

macro(__windows_compiler_msvc lang)
  if(NOT "${CMAKE_${lang}_COMPILER_VERSION}" VERSION_LESS 14)
    # for 2005 make sure the manifest is put in the dll with mt
    #set(_CMAKE_VS_LINK_DLL "<CMAKE_COMMAND> -E vs_link_dll ")
    #set(_CMAKE_VS_LINK_EXE "<CMAKE_COMMAND> -E vs_link_exe ")
  endif()

  set(CMAKE_${lang}_LINK_LIBRARY_FLAG "")
  set(CMAKE_LIBRARY_PATH_FLAG "-LIBPATH:")
  set(CMAKE_${lang}_COMPILER_AR  $ENV{SIT}/DevelopmentTools/ToolBOSPluginWindows/8.0/bin/lib)

  set(CMAKE_${lang}_CREATE_SHARED_LIBRARY
    "${_CMAKE_VS_LINK_DLL}<CMAKE_LINKER> ${CMAKE_CL_NOLOGO} <OBJECTS> ${CMAKE_START_TEMP_FILE} /out:<TARGET> /manifest /implib:<TARGET_IMPLIB> /DLL ${_CMAKE_MSVC_DLL_ENTRY} /subsystem:console /nodefaultlib:libc /incremental:no /opt:icf /opt:ref /pdb:<TARGET_PDB> /version:<TARGET_VERSION_MAJOR>.<TARGET_VERSION_MINOR> <LINK_FLAGS> <LINK_LIBRARIES> ${CMAKE_END_TEMP_FILE}")

  set(CMAKE_${lang}_CREATE_SHARED_MODULE ${CMAKE_${lang}_CREATE_SHARED_LIBRARY})
  set(CMAKE_${lang}_CREATE_STATIC_LIBRARY  "<CMAKE_LINKER> /lib ${CMAKE_CL_NOLOGO} <LINK_FLAGS> /out:<TARGET> <OBJECTS> ")

  set(CMAKE_${lang}_COMPILE_OBJECT
    "<CMAKE_${lang}_COMPILER> ${CMAKE_START_TEMP_FILE} ${CMAKE_CL_NOLOGO}${_COMPILE_${lang}} <DEFINES> <INCLUDES> <FLAGS> /Fo<OBJECT> /Fd<TARGET_PDB> -c <SOURCE>${CMAKE_END_TEMP_FILE}")
  set(CMAKE_${lang}_CREATE_PREPROCESSED_SOURCE
    "<CMAKE_${lang}_COMPILER> > <PREPROCESSED_SOURCE> ${CMAKE_START_TEMP_FILE} ${CMAKE_CL_NOLOGO}${_COMPILE_${lang}} <DEFINES> <INCLUDES> <FLAGS> -E <SOURCE>${CMAKE_END_TEMP_FILE}")
  set(CMAKE_${lang}_CREATE_ASSEMBLY_SOURCE
    "<CMAKE_${lang}_COMPILER> ${CMAKE_START_TEMP_FILE} ${CMAKE_CL_NOLOGO} ${_COMPILE_${lang}} <DEFINES> <INCLUDES> <FLAGS> /FoNUL /FAs /Fa<ASSEMBLY_SOURCE> /c <SOURCE>${CMAKE_END_TEMP_FILE}")

  set(CMAKE_${lang}_COMPILER_LINKER_OPTION_FLAG_EXECUTABLE "/link")
  set(CMAKE_${lang}_USE_RESPONSE_FILE_FOR_OBJECTS 1)
  set(CMAKE_${lang}_LINK_EXECUTABLE
    "${_CMAKE_VS_LINK_EXE}<CMAKE_LINKER> ${CMAKE_CL_NOLOGO} <OBJECTS> ${CMAKE_START_TEMP_FILE} <LINK_FLAGS> /OUT:<TARGET> /implib:<TARGET_IMPLIB> /pdb:<TARGET_PDB> /version:<TARGET_VERSION_MAJOR>.<TARGET_VERSION_MINOR> <LINK_LIBRARIES>${CMAKE_END_TEMP_FILE}")

  set(CMAKE_${lang}_FLAGS_INIT "${_PLATFORM_DEFINES}${_PLATFORM_DEFINES_${lang}} /D_WINDOWS /W3 /Zm1000${_FLAGS_${lang}}")
  set(CMAKE_${lang}_FLAGS_DEBUG_INIT "/D_DEBUG /Ob0 /Od${_RTC1}")
  set(CMAKE_${lang}_FLAGS_RELEASE_INIT "/O2 /Ob2 /D NDEBUG")
  set(CMAKE_${lang}_FLAGS_RELWITHDEBINFO_INIT "/O2 /Ob1 /D NDEBUG")
  set(CMAKE_${lang}_FLAGS_MINSIZEREL_INIT "/O1 /Ob1 /D NDEBUG")
endmacro()

cmake_policy(POP)

# EOF
