::
::  ToolBOS environment setup
::
::  Copyright (C)
::  Honda Research Institute Europe GmbH
::  Carl-Legien-Str. 30
::  63073 Offenbach/Main
::  Germany
::
::  UNPUBLISHED PROPRIETARY MATERIAL.
::  ALL RIGHTS RESERVED.
::
::
::  Example usage in Windows cmd.exe:
::  C:\>S:\DevelopmentTools\ToolBOSCore\2.0\CmdSrc.bat
::
::  If you need to use a different location for the SIT than S:
::  just set the variable SIT_LOCATION before calling this batch script, e.g.
::  set SIT_LOCATION=C:\Users\Me\MyLocalSIT
::  C:\Users\Me\MyLocalSIT\DevelopmentTools\ToolBOSCore\2.0\CmdSrc.bat



:: ------------------------------------------------------------------------
:: Master Environment Setup
:: ------------------------------------------------------------------------


@echo off


:: avoid multiple inclusion
echo %PATH% | find "DevelopmentTools/ToolBOSCore/3.0" > null
if %errorlevel% equ 0 ( goto :EOF )


:: ------------------------------------------------------------------------
:: Platform identifier / Build system
:: ------------------------------------------------------------------------


set MAKEFILE_OS=windows


if "%PROCESSOR_ARCHITECTURE%" == "x86" (
    set MAKEFILE_CPU=i386
) else (
    set MAKEFILE_CPU=amd64
)


if defined MAKEFILE_CC (
    set COMPILER=%MAKEFILE_CC%
) else (
    set MAKEFILE_CC=vs2012
    set COMPILER=%MAKEFILE_CC%
)


if defined MAKEFILE_PLATFORM (
    set HOST_PLATFORM=%MAKEFILE_PLATFORM%
    set TARGET_PLATFORM=%MAKEFILE_PLATFORM%
) else (
    set MAKEFILE_PLATFORM=windows-%MAKEFILE_CPU%-%MAKEFILE_CC%
    set HOST_PLATFORM=%MAKEFILE_PLATFORM%
    set TARGET_PLATFORM=%MAKEFILE_PLATFORM%
)


:: ------------------------------------------------------------------------
:: Location of ToolBOS SDK + Paths settings
:: ------------------------------------------------------------------------


if defined SIT_LOCATION (
    :: This performs in-variable text replacement (backslash to slash)
    set SIT=%SIT_LOCATION:\=/%
) else (
    set SIT=S:
)

set TOOLBOSCORE_ROOT=%SIT%/DevelopmentTools/ToolBOSCore/3.0

:: Run-time libraries paths
set PATH=%TOOLBOSCORE_ROOT%\bin;%PATH%
set PATH=%TOOLBOSCORE_ROOT%\bin\%MAKEFILE_PLATFORM%;%PATH%
set PATH=%TOOLBOSCORE_ROOT%\lib\%MAKEFILE_PLATFORM%;%PATH%


:: Load dependencies
call "%SIT%\External\CMake\3.2\CmdSrc.bat"

:: Python path
set PYTHONPATH=%TOOLBOSCORE_ROOT%\include;%PYTHONPATH%
set PYTHONPATH=%TOOLBOSCORE_ROOT%\external;%PYTHONPATH%
set PYTHONPATH=%TOOLBOSCORE_ROOT%\lib\%MAKEFILE_PLATFORM%;%PYTHONPATH%

:: EOF
