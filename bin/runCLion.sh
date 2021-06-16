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


DESCRIPTION="CLion IDE"
TOOLBOS_CONF_KEY=package_clion

IDE_PACKAGE=$(ToolBOS-Config.py -p ${TOOLBOS_CONF_KEY})

if [[ "${BASH_ARGV}" != "" ]]
then
    SCRIPTNAME=$(basename $0)

    echo -e "\nLaunches the ${DESCRIPTION} pre-configured for this package.\n"

    echo -e "Usage: ${SCRIPTNAME} [--help]\n"

    echo -e "options:"
    echo -e "  -h|--help       show this help and exit\n"

    echo -e "Examples: ${SCRIPTNAME}\n"

    exit 0
fi


if [[ ! -e "${SIT}/External/OracleJava/1.0/BashSrc" ]]
then
    echo -e "\nOracle Java is required. Please run 'UpdateProxyDir.py' to get it.\n "
    exit -1
fi


# If we are within a source package, attempt to pre-configure the IDE
# accordingly. Otherwise just start the tool.

if [[ -e CMakeLists.txt || -e pkgInfo.py ]]
then

    # generate the BashSrc file for the current package and source it, in order
    # to get PYTHONPATH and dependencies right, also add local "include" and "src"
    # directories (to be sure they are found)

    BST.py --shellfiles &> /dev/null
    source ./install/BashSrc

    CWD=$(pwd)
    export LD_LIBRARY_PATH=${CWD}/lib/${MAKEFILE_PLATFORM}:${LD_LIBRARY_PATH}

    echo -e "\nLD_LIBRARY_PATH:"
    echo ${LD_LIBRARY_PATH} | tr ":" "\n"
    echo -e "\n"

fi


CMD="clion.sh $(pwd)"

# launch the application
echo "Launching ${DESCRIPTION}..."
source ${SIT}/${IDE_PACKAGE}/BashSrc
${CMD}


# EOF
