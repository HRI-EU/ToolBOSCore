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

if [[ "${CIA}" != "TRUE" ]]
then
    # All these tests require BBDMs,... not present during Nightly Build
    #
    source ${SIT}/Libraries/BPLBase/7.1/BashSrc
    source ${SIT}/Modules/BBDM/BBDMArrayBlockF32/1.7/BashSrc
    source ${SIT}/Modules/BBDM/BBDMBaseI32/1.7/BashSrc
    source ${SIT}/Modules/BBDM/BBDMBlockF32/1.7/BashSrc
    source ${SIT}/Modules/BBDM/BBDMBaseF32/1.7/BashSrc
    source ${SIT}/Modules/BBDM/BBDMMemI8/1.7/BashSrc

    cd ${CWD}/General        && runTest ${MAKEFILE_PLATFORM}/TestCoreLibrary
fi


cd ${CWD}/IOChannel      && runTest ${MAKEFILE_PLATFORM}/TestIOChannel
cd ${CWD}/ListsAndQueues && runTest ${MAKEFILE_PLATFORM}/TestListsAndQueues
cd ${CWD}/Multithreading && runTest ${MAKEFILE_PLATFORM}/TestMultithreading


# EOF
