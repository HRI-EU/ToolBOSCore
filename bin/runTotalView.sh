#!/bin/bash
#
#  JetBrains IDE launcher
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


set -euo pipefail


DESCRIPTION="TotalView"
TOOLBOS_CONF_KEY=package_totalview


if [[ "$1" == '-h' || "$1" == '--help' ]]
then
    SCRIPTNAME=$(basename "${0}")

    echo -e "\nLaunches the latest stable version of ${DESCRIPTION}\n"

    echo -e "Usage: ${SCRIPTNAME} [--help]\n"

    echo -e "options:"
    echo -e "  -h|--help       show this help and exit\n"

    echo -e "Examples: ${SCRIPTNAME}\n"

    exit 0
fi


set -euxo pipefail


# launch the application
echo "Launching ${DESCRIPTION}..."
PACKAGE=$(ToolBOS-Config.py -p "${TOOLBOS_CONF_KEY}")
# shellcheck source=/hri/sit/latest/External/totalview/2020.0/BashSrc
source "${SIT}/${PACKAGE}/BashSrc"

exec totalview -newUI "$@"


# EOF
