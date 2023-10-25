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

if [[ "$#" -eq 0 ]] # no parameter is passed, using default
then
    VERSION="4.2"
else
    VERSION="$1"
fi

source useFromHere.sh "${VERSION}"
source "${SIT}/External/anaconda3/envs/common/3.9/BashSrc"

set -euxo pipefail

BST.py --test


# EOF
