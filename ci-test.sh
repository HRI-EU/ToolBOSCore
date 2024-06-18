#!/bin/bash
#
#  GitLab CI/CD operations
#
#  Copyright (c) Honda Research Institute Europe GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#


CONDA_CANONICAL_PATH=""
CONDA_VERSION="3.9" # backward compatability


SourceAnaconda() {
    VERSION="$1"

    # hack for now to parse the canonical path of anaconda correctly!
    if [[ "${VERSION}" == "${CONDA_VERSION}" ]]
    then
        CONDA_CANONICAL_PATH="${SIT}/External/anaconda3/envs/common/${VERSION}/BashSrc"
    else
        CONDA_CANONICAL_PATH="${SIT}/External/anaconda/envs/common/${VERSION}/BashSrc"
    fi

    echo "sourcing Anaconda from ${CONDA_CANONICAL_PATH}"
    # shellcheck source=/hri/sit/latest/External/anaconda/envs/common/3.11/BashSrc
    source "${CONDA_CANONICAL_PATH}"
}


if [[ "$#" -eq 0 ]] # no arguments supplied
then
    echo "No arguments supplied, please provide the necessary arguments!"
    echo "Usage: $0 TOOLBOSCORE_VERSION PYTHON_VERSION"
    exit 1
fi


if [[ -n "$1" ]]
then
    TOOLBOSCORE_VERSION="$1"
fi


# shellcheck source=/dev/null
source useFromHere.sh "${TOOLBOSCORE_VERSION}"


if [[ -z "$2" ]] # no argument supplied, using default
then
    echo "Using the default Python version from Ubuntu!"
else
    SourceAnaconda "$2"
fi


set -euxo pipefail

BST.py --test


# EOF
