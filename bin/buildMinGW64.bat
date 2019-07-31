::
::  Compile using MinGW
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
::  S:\DevelopmentTools\ToolBOSCore\3.0\bin\buildMinGW64.bat
::
::  If you need to use a different location for the SIT than S:
::  just set the variable SIT_LOCATION before calling this batch script, e.g.
::  set SIT_LOCATION=C:\Users\Me\MyLocalSIT
::  C:\Users\Me\MyLocalSIT\DevelopmentTools\ToolBOSCore\3.0\bin\buildMinGW64.bat
::


@echo off

if defined SIT_LOCATION (
    set SIT_LOCATION=%SIT_LOCATION%
) else (
    set SIT_LOCATION=C:\SIT
)


set BST_CMAKE_OPTIONS=-G "MinGW Makefiles"

call %SIT_LOCATION%\DevelopmentTools\ToolBOSCore\3.0\CmdSrcMinGW.bat



BST.py --all --platform=mingw64


:: EOF
