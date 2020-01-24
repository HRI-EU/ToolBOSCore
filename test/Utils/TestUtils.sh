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

cd ${CWD}/ArgsManagerV2 && ./TestArgsManagerV2.py
cd ${CWD}/ThreadPool    && ./TestThreadPool.py


# EOF
