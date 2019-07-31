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

cd ${CWD}/Bootstrap      && runTest ./TestBootstrap.py
cd ${CWD}/DeprecatedFlag && runTest ./TestDeprecatedFlag.py


if [[ "${CIA}" != "TRUE" ]]
then
    # Disabled during CIA because no proxy directory present at that time.
    #
    cd ${CWD}/ProxyDirectory && runTest ./TestProxyDirectory.py
fi


# EOF
