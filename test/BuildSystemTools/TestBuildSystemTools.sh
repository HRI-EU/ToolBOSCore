#!/bin/bash
#
#  launches the unit testing
#
#  Copyright (C)
#  Honda Research Institute Europe GmbH
#  Carl-Legien-Str. 30
#  63073 Offenbach/Main
#  Germany
#
#  UNPUBLISHED PROPRIETARY MATERIAL.
#  ALL RIGHTS RESERVED.
#
#


source ${TOOLBOSCORE_ROOT}/include/Unittest.bash

CWD=$(pwd)

cd ${CWD}/CMakeLists            && runTest ./TestCMakeLists.py
cd ${CWD}/DocumentationCreator  && runTest ./TestDocumentationCreator.py
cd ${CWD}/GlobalInstallLogEntry && runTest ./TestGlobalInstallLogEntry.py
cd ${CWD}/NativeCompilation     && runTest ./TestNativeCompilation.py


if [[ "${CIA}" != "TRUE" ]]
then
    # 1. cross-compilation is not supported from trusty64, yet
    #
    # 2. during unittest TOOLBOSCORE_ROOT points to the working copy
    #    under test, which does not contain the ToolBOSCore.lib
    #    Windows libraries
    #
    cd ${CWD}/WineMSVC          && runTest ./TestWineMSVC.py
fi


# EOF
