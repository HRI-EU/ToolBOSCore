::
::  ToolBOS environment setup
::
::  Copyright (c) Honda Research Institute Europe GmbH
::
::  Redistribution and use in source and binary forms, with or without
::  modification, are permitted provided that the following conditions are
::  met:
::
::  1. Redistributions of source code must retain the above copyright notice,
::     this list of conditions and the following disclaimer.
::
::  2. Redistributions in binary form must reproduce the above copyright
::     notice, this list of conditions and the following disclaimer in the
::     documentation and/or other materials provided with the distribution.
::
::  3. Neither the name of the copyright holder nor the names of its
::     contributors may be used to endorse or promote products derived from
::     this software without specific prior written permission.
::
::  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
::  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
::  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
::  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
::  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
::  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
::  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
::  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
::  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
::  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
::  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
::
::
::  Example usage in Windows cmd.exe:
::  C:\>S:\DevelopmentTools\ToolBOSCore\4.3\CmdSrc.bat
::
::  If you need to use a different location for the SIT than S:
::  just set the variable SIT_LOCATION before calling this batch script, e.g.
::  set SIT_LOCATION=C:\Users\Me\MyLocalSIT
::  C:\Users\Me\MyLocalSIT\DevelopmentTools\ToolBOSCore\4.3\CmdSrc.bat



:: ------------------------------------------------------------------------
:: Master Environment Setup
:: ------------------------------------------------------------------------


@echo off


:: avoid multiple inclusion
echo %PATH% | find "DevelopmentTools/ToolBOSCore/4.3" > null
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

set TOOLBOSCORE_ROOT=%SIT%/DevelopmentTools/ToolBOSCore/4.3

:: Run-time libraries paths
set PATH=%TOOLBOSCORE_ROOT%\bin;%PATH%
set PATH=%TOOLBOSCORE_ROOT%\bin\%MAKEFILE_PLATFORM%;%PATH%
set PATH=%TOOLBOSCORE_ROOT%\lib\%MAKEFILE_PLATFORM%;%PATH%

:: Python path
set PYTHONPATH=%TOOLBOSCORE_ROOT%\include;%PYTHONPATH%
set PYTHONPATH=%TOOLBOSCORE_ROOT%\external;%PYTHONPATH%
set PYTHONPATH=%TOOLBOSCORE_ROOT%\lib\%MAKEFILE_PLATFORM%;%PYTHONPATH%

:: EOF
