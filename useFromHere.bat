::
::  Switch to a different ToolBOS SDK installation
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


:: ------------------------------------------------------------------------
:: Master Environment Setup
:: ------------------------------------------------------------------------


@echo off


set OLD_TOOLBOSCORE_ROOT=%TOOLBOSCORE_ROOT%
set NEW_TOOLBOSCORE_ROOT=H:\ToolBOSCore\3.3

echo new ToolBOS SDK location: %NEW_TOOLBOSCORE_ROOT%


set TOOLBOSCORE_ROOT=%NEW_TOOLBOSCORE_ROOT%
set PATH=%TOOLBOSCORE_ROOT%\bin;%TOOLBOSCORE_ROOT%\bin\%MAKEFILE_PLATFORM%;%TOOLBOSCORE_ROOT%\lib;%TOOLBOSCORE_ROOT%\lib\%MAKEFILE_PLATFORM%;%PATH%
set PYTHONPATH=%TOOLBOSCORE_ROOT%\include;%TOOLBOSCORE_ROOT%\external;%TOOLBOSCORE_ROOT%\lib\%MAKEFILE_PLATFORM%;%PYTHONPATH%


:: EOF
