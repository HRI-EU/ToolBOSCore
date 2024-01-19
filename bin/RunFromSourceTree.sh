#!/bin/bash
#
#  sources the BashSrc, sets the LD_LIBRARY_PATH to the local ./lib/<platform>
#  directory and executes the program
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


set -eo pipefail


# read TOOLBOS_CONF_BUGTRACK_URL from settings file:
source "${TOOLBOSCORE_ROOT}/etc/ToolBOS.conf.sh"


if [[ -z ${VERBOSE+x} ]]
then
    export VERBOSE="FALSE"
fi



#----------------------------------------------------------------------------
# checking for cmdline parameters


function print_help()
{
    PROGNAME=$(basename "$0")

    echo ""
    echo "This script tests for the ./install/BashSrc, creates it if not "
    echo "present, sets the LD_LIBRARY_PATH to the local ./lib/<platform> "
    echo "directory and executes the specified program."
    echo ""
    echo "Usage: ${PROGNAME} <executable>"
    echo ""
    echo "Parameters:"
    echo "        executable      the file to be executed"
    echo ""
    echo "Options:"
    echo "        -h, --help      display this help and exit"
    echo ""
    echo "Examples:"
    echo "        ${PROGNAME} ./examples/${MAKEFILE_PLATFORM}/myExample"
    echo ""
    echo "Please report bugs on GitLab (${TOOLBOS_CONF_BUGTRACK_URL})."
}


CWD=$(pwd)


while :
do
    case $1 in

    -h|--help)
        print_help "${0}"
        exit
        ;;
    *)
        break;

    esac
done


if [[ $1 == "" ]]
then
    print_help "${0}"
fi


if [[ "${VERBOSE}" == "TRUE" ]]
then
    set -euxo pipefail
else
    set -euo pipefail
fi


#----------------------------------------------------------------------------
# the executable passed as argument must be a file, readable and an executable

PROGRAM=$1

if [[ ! -s "${PROGRAM}" ||
      ! -r "${PROGRAM}" ||
      ! -x "${PROGRAM}" ||
      ! -f "${PROGRAM}" ]]
then
    echo ""
    echo "${PROGRAM}: No such file (or permission denied)"
    echo ""
    exit 1;
fi


#----------------------------------------------------------------------------
# source the regular BashSrc from the source tree if existing

if [[ ${VERBOSE} == "TRUE" ]]
then
    echo -e "\n\n\033[1;31m$ BST.py --shellfiles\033[0m"
    BST.py --shellfiles
else
    BST.py --shellfiles 2> /dev/null
fi


cd "${CWD}" || exit

if [[ ${VERBOSE} == "TRUE" && ! -r ./install/BashSrc ]]
then
    echo -e "\n./install/BashSrc: No such file\n"
fi


#----------------------------------------------------------------------------
# start with a freshly set up LD_LIBRARY_PATH

# disabled unsetting LD_LIBRARY_PATH as it will cause packages not be
# re-sourced again (checking for double-sourcing is now done via separate
# env.variable TOOLBOSCORE_SOURCED, instead of LD_LIBRARY_PATH itself

# unset LD_LIBRARY_PATH

if [[ -r "./install/BashSrc" ]]
then
    # shellcheck source=./install/BashSrc
    source "./install/BashSrc"
fi


#----------------------------------------------------------------------------
# put locally compiled libraries at the beginning of the library search path

export LD_LIBRARY_PATH=./lib/${MAKEFILE_PLATFORM}:${LD_LIBRARY_PATH}


#----------------------------------------------------------------------------
# show effectively used libraries

if [[ "${VERBOSE}" == "TRUE" ]]
then
    echo -e "\n\n\033[1;31m$ echo \$LD_LIBRARY_PATH\033[0m"
    echo "${LD_LIBRARY_PATH}" | tr ":" "\n"
fi


#----------------------------------------------------------------------------
# execute the binary (with parameters given on cmdline)

if [[ "${VERBOSE}" == "TRUE" ]]
then
    echo -e "\n\n\033[1;31m$ ldd ${PROGRAM}\033[0m"
    ldd "${PROGRAM}"
fi

"$@"
STATUS=$?


exit "${STATUS}"


# EOF
