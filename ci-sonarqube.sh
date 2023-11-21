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


if [[ "$#" -eq 0 ]] # no argument supplied, using default
then
    TOOLBOSCORE_VERSION="4.2"
else
    TOOLBOSCORE_VERSION="$1"
fi

# shellcheck source=/hri/sit/latest/DevelopmentTools/ToolBOSCore/4.2/BashSrc
source "/hri/sit/latest/DevelopmentTools/ToolBOSCore/${TOOLBOSCORE_VERSION}/BashSrc"
source "${SIT}/External/anaconda3/envs/common/3.9/BashSrc"

set -euxo pipefail

runSonarQube.py


# EOF
