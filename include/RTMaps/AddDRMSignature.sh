#!/bin/bash
#
#  Retrieves the RTMaps version included in CMakeLists.txt and calls the
#  Intempora DRM script from that installation
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

#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


SCRIPTNAME=$(basename "$0")

function showHelp()
{
  echo -e "\nRetrieves the RTMaps version included in CMakeLists.txt and "
  echo -e "calls the Intempora DRM script from that installation in order to \n"
  echo -e "to add the necessary DRM information to the *.pck file."

  echo -e "Usage:"
  echo -e "    ${SCRIPTNAME} <CMakeLists> <pckInfoFile> <pckFile>\n"

  echo -e "Example:"
  echo -e "${SCRIPTNAME} CMakeLists.txt ./MyPackage.pckinfo ./lib/${MAKEFILE_PLATFORM}/MyPackage.pck\n\n"
}


if [[ $# != 3 ]]
then
    showHelp
    exit
fi


CMAKELISTS=$1
PCK_INFO=$2
PCK_FILE=$3


#----------------------------------------------------------------------------
# Retrieve included RTMaps version from CMakeLists.txt
#----------------------------------------------------------------------------


RTMAPS_VERSION=$(grep -oP '(?<=bst_find_package\(External/RTMaps/).*(?=\))' "${CMAKELISTS}")

if [[ -z "${RTMAPS_VERSION}" ]]
then
    echo "Error: Unable to retrieve RTMaps version from ${CMAKELISTS}."
    exit 1
fi


if [[ "${VERBOSE}" == "TRUE" ]]
then
    echo "RTMaps version: ${RTMAPS_VERSION}"
fi


#----------------------------------------------------------------------------
# Launch DRM tool
#----------------------------------------------------------------------------

# shellcheck source=/hri/sit/latest/External/RTMaps/4.7/BashSrc
source "${SIT}/External/RTMaps/${RTMAPS_VERSION}/BashSrc"

if [[ -z "${RTMAPS_SDKDIR}" ]]
then
    echo "Environment variable RTMAPS_SDKDIR not defined."
    echo "Please check the RTMaps installation."
    exit 1
fi


CMD="${RTMAPS_SDKDIR}/bin/rtmaps_package_sign -info ${PCK_INFO} -package ${PCK_FILE}"

if [[ "${VERBOSE}" == "TRUE" ]]
then
    echo "${CMD}"
fi

${CMD}


# EOF
