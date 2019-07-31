#!/bin/sh
#
#  use this shellscript to provide the ground-truth files for the
#  'makeShellfiles' testcase
#
#  Copyright (c)
#  Honda Research Institute Europe GmbH
#  Carl-Legien-Str. 30
#  63073 Offenbach/Main
#  Germany
#
#  UNPUBLISHED PROPRIETARY MATERIAL.
#  ALL RIGHTS RESERVED.
#
#


OUTPUT_DIR=$(pwd)

cd ../../..
BST.py --shellfiles

grep -v commitID install/pkgInfo.py > ${OUTPUT_DIR}/ToolBOSCore-2.0-pkgInfo.py
grep -v commitID install/BashSrc    > ${OUTPUT_DIR}/ToolBOSCore-2.0-BashSrc
grep -v commitID install/CmdSrc.bat > ${OUTPUT_DIR}/ToolBOSCore-2.0-CmdSrc.bat


# EOF
