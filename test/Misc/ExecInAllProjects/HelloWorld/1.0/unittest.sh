#!/bin/bash
#
#  launches the unittest suite
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
#  Start by hand using "./unittest.sh", or programmatically via "BST.py -t"
#  (or BuildSystemTools.unittest() in Python).
#
#


#----------------------------------------------------------------------------
# Includes
#----------------------------------------------------------------------------


source ${TOOLBOSCORE_ROOT}/include/Unittest.bash


#----------------------------------------------------------------------------
# Launcher
#----------------------------------------------------------------------------


# list here each testprogram (one "runTest"-statement per line)
runTest ./test/${MAKEFILE_PLATFORM}/unittest


# we managed to get here --> success
exit 0


# EOF
