#!/bin/bash
#
#  GitLab CI/CD operations
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


source /hri/sit/latest/DevelopmentTools/ToolBOSCore/4.1/BashSrc
source "${SIT}/External/anaconda3/envs/common/3.9/BashSrc"
source useFromHere.sh

set -euxo pipefail

BST.py --quality


# EOF
