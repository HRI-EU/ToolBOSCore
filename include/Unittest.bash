#!/bin/bash
#
#  unittest helpers
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

# strict shell settings
set -euxo pipefail

function check
{
    "$@"
    local status=$?

    if [[ ${status} != 0 ]]
    then
        echo -e "\nexecution failed: $*\n"
        exit 255
    fi

    return "${status}"
}


function execTest()
{
    FILENAME=$1
    CMDLINE=$*

    if [[ -z ${USE_RUNFROMSOURCETREE+x} ]]
    then
        export USE_RUNFROMSOURCETREE="FALSE"
    fi

    if [[ -f "${FILENAME}" ]]
    then
        echo -e "Start test: ${FILENAME}"

        if [[  ( "${USE_RUNFROMSOURCETREE}" == "FALSE" ) ||
             ( ( ! -e CMakeLists.txt ) && ( ! -e pkgInfo.py ) )  ]]
        then
            "${CMDLINE[*]}"
        else
            RunFromSourceTree.sh "${CMDLINE[*]}"
         fi

        # shellcheck disable=SC2181
        if [[ $? != 0 ]]
        then
            echo -e "Stop test:  ${FILENAME}  [\033[1;31mFAILED\033[00m]"
            return 1
        else
            echo -e "Stop test:  ${FILENAME}  [\033[1;32mOK\033[00m]"
            return 0
        fi
    else
        echo -e "Error: ${FILENAME}  [\033[1;31mNOT FOUND\033[00m]"
        return 1
    fi
}

function runTest()
{
    CMDLINE=$*

    if ! execTest "$@"
    then
        exit 1
    fi
}

function runTests()
{
    for FILENAME in $1
    do
        runTest "${FILENAME}"
    done
}


function runMatlabTest()
{
    FILENAME=$1
    CMDLINE=$*

    if [[ -f "${FILENAME}" ]]
    then
        if [[ ${FILENAME} == *.m ]]
        then
            echo -e "\nStart test: ${FILENAME}"
            if ! matlab -nodisplay -nosplash -nodesktop -r "try,run ${FILENAME}, exit(0),catch e, disp(e.identifier), disp(e.message), clear e, exit(-1),end"
            then
                echo -e "Stop test:  ${FILENAME}  [\033[1;31mFAILED\033[00m]"
                exit 1
            else
                echo -e "Stop test:  ${FILENAME}  [\033[1;32mOK\033[00m]"
            fi
        else
            echo -e "Error: ${FILENAME}  [\033[1;31mNOT A MATLAB FILE\033[00m]"
            exit 1
        fi
    else
        echo -e "Error: ${FILENAME}  [\033[1;31mNOT FOUND\033[00m]"
        exit 1
    fi
}


# EOF
