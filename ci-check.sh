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


source useFromHere.sh
source "${SIT}/External/anaconda3/envs/common/3.9/BashSrc"

set -euxo pipefail

BST.py --quality


# EOF
