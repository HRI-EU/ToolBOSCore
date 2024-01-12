#!/bin/bash
#
#  Switch to a different ToolBOS SDK installation
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
#  Note:  This file needs to be sourced, not executed! For example:
#         $ source ./switchSDK.rc
#


# define env.variable if not set, yet

if [[ -z ${LD_LIBRARY_PATH+x} ]]
then
    export LD_LIBRARY_PATH=""
fi

if [[ -z ${MAKEFILE_PLATFORM+x} ]]
then
    export MAKEFILE_PLATFORM=focal64
fi

if [[ -z ${PYTHONPATH+x} ]]
then
    export PYTHONPATH=""
fi

if [[ -z ${SIT+x} ]]
then
    export SIT="/hri/sit/latest"
fi

if [[ -z ${TOOLBOSCORE_ROOT+x} ]]
then
    export TOOLBOSCORE_ROOT=""
fi

if [[ -z ${VERBOSE+x} ]]
then
    export VERBOSE=""
fi


SCRIPT_PATH=$(dirname "$(readlink -f "${BASH_SOURCE:-$0}")")
NEW_TOOLBOSCORE_ROOT=$(builtin cd "${SCRIPT_PATH}" ; pwd) || exit 1
echo "new ToolBOSCore location: ${NEW_TOOLBOSCORE_ROOT}"

export TOOLBOSCORE_ROOT="${NEW_TOOLBOSCORE_ROOT}"

if [[ "$#" -eq 0 ]] # no argument supplied, using default
then
    TOOLBOSCORE_VERSION="4.3"
else
    TOOLBOSCORE_VERSION="$1"
fi

export TOOLBOSCORE_SOURCED="DevelopmentTools/ToolBOSCore/${TOOLBOSCORE_VERSION}"
export PATH="${TOOLBOSCORE_ROOT}/bin:${TOOLBOSCORE_ROOT}/bin/${MAKEFILE_PLATFORM}:${PATH}"
export LD_LIBRARY_PATH="${TOOLBOSCORE_ROOT}/lib/${MAKEFILE_PLATFORM}:${LD_LIBRARY_PATH}"
export PYTHONPATH="${TOOLBOSCORE_ROOT}/include:${TOOLBOSCORE_ROOT}/external:${TOOLBOSCORE_ROOT}/lib/${MAKEFILE_PLATFORM}:${PYTHONPATH}"


function bst {
   BST.py "$@"
}
export -f bst


# EOF
