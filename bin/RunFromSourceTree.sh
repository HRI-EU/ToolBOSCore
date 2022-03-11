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
  echo "Usage: $PROGNAME <executable>"
  echo ""
  echo "Parameters:"
  echo "        executable      the file to be executed"
  echo ""
  echo "Options:"
  echo "        -h, --help      display this help and exit"
  echo ""
  echo "Examples:"
  echo "        $PROGNAME ./examples/${MAKEFILE_PLATFORM}/myExample"
  echo ""
  echo "Please report bugs on JIRA (${TOOLBOS_CONF_BUGTRACK_URL})."

  exit
}


# Find <target> in current or parent-directories. Print directory to
# stdout when found. Stop at root (/) if <target> not found.
function rfind()
{
    local target=${1}
    local retStatus=1

    local currentDir=${PWD}
    while [ "${PWD}" != "/" ]; do
        if [ -e "${target}" ]; then
            echo "${PWD}"
            retStatus=0
	    break
        fi
        cd ..
    done

    cd "${currentDir}" || exit
    return ${retStatus}
}


#----------------------------------------------------------------------------
# init the variables

CWD=$(pwd)
INSTALL_DIR=install
FILENAME=BashSrc


while :
do

    case $1 in

    -h|--help)
        print_help "${0}"
        shift
        ;;

    *)
        break;

    esac
done


if [[ $1 == "" ]]
then
    print_help "${0}"
fi

EXECUTABLE_BIN=$1


if [[ "${VERBOSE}" == "TRUE" ]]
then
    set -euxo pipefail
else
    set -euo pipefail
fi


#----------------------------------------------------------------------------
# the executable passed as argument must be a file, readable and an executable

if [[ ! -s "${EXECUTABLE_BIN}" ||
      ! -r "${EXECUTABLE_BIN}" ||
      ! -x "${EXECUTABLE_BIN}" ||
      ! -f "${EXECUTABLE_BIN}" ]]
then

    if [[ $(which "${EXECUTABLE_BIN}") == "" ]]
        then
        echo ""
        echo "${EXECUTABLE_BIN}: No such file (or permission denied)"
        echo ""
        exit 1;
    else
        # the EXECUTABLE_PATH is created assuming the script is executed inside the version subdir
        EXECUTABLE_PATH=${CWD}
        EXECUTABLE_DIR=${CWD}
    fi
else
    # the EXECUTABLE_PATH is created assuming the script is executed inside the version subdir
    EXECUTABLE_PATH=${CWD}/${EXECUTABLE_BIN}
    EXECUTABLE_DIR=${CWD}/$(dirname "${EXECUTABLE_BIN}")
fi


if [[ "${VERBOSE}" == "TRUE" ]]
then
    echo "EXECUTABLE_PATH:   ${EXECUTABLE_PATH}"
    echo "EXECUTABLE_DIR:    ${EXECUTABLE_DIR}"
    echo "MAKEFILE_PLATFORM: ${MAKEFILE_PLATFORM}"
fi


function runCommand
{
    COMMAND=$1

    if [[ -z "${COMMAND}" ]]
    then
        echo "Internal script error :-/"
        exit 1
    fi


    if [[ $VERBOSE == "TRUE" ]]
    then
        echo -e "\n\n\033[1;31m$ ${COMMAND}\033[0m"
    fi


    eval "${COMMAND}"


    if [[ "${?}" != 0 ]]
    then
        exit 1
    fi
}


#----------------------------------------------------------------------------
# source the regular BashSrc from the source tree if existing

if [[ $VERBOSE == "TRUE" ]]
then
    echo -e "\n\n\033[1;31m$ BST.py --shellfiles\033[0m"
    BST.py --shellfiles
else
    BST.py --shellfiles 2> /dev/null
fi


cd "${CWD}" || exit

if [[ $VERBOSE == "TRUE" && ! -r ./${INSTALL_DIR}/${FILENAME} ]]
then
    echo -e "\n./${INSTALL_DIR}/${FILENAME}: No such file\n"
fi


#----------------------------------------------------------------------------
# start with a freshly set up LD_LIBRARY_PATH

# disabled unsetting LD_LIBRARY_PATH as it will cause packages not be
# re-sourced again (checking for double-sourcing is now done via separate
# env.variable TOOLBOSCORE_SOURCED, instead of LD_LIBRARY_PATH itself

# unset LD_LIBRARY_PATH

if [[ -r "./${INSTALL_DIR}/${FILENAME}" ]]
then
    # shellcheck source=./install/BashSrc
    source "./${INSTALL_DIR}/${FILENAME}"
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
    echo -e "\n\n\033[1;31m$ ldd ${EXECUTABLE_BIN}\033[0m"
    ldd "${EXECUTABLE_BIN}"
fi

"$@"
STATUS=$?


exit ${STATUS}


echo "Internal script error (how did you get here??)"
exit 42


# EOF
