#!/bin/bash
#
#  Archive partial SIT with everything needed by specified package
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


E_NODIR=70
E_UNKNOWN=80


if [[ "$BASH_ARGC" != 1 || "$1" == '-h' || "$1" == '--help' ]]
then
    echo ""
    echo "Usage: $(basename $0) PROJECTDIR"
    echo ""
    echo "PROJECTDIR: Directory to the application stored as HRI project in the global SIT (*)"
    echo ""
    echo "Example:"
    echo "$(basename $0) /hri/sit/latest/Applications/Hdot/HCollect/1.3"
    echo "The libraries are copied to /hri/sit/frozen"
    echo ""
    echo "(*) Please note that your application needs to be globally installed before you can make a copy of the tree"
    echo ""

    if [[ "$1" == '-h' || "$1" == '--help' ]]
    then
        exit 0
    else
        exit $E_BADARGS
    fi
fi

exit


PROJECT=$1
TARGETDIR=/hri/sit/frozen


if [ ! -d ${PROJECT} ]
then
    echo ""
    echo "Specified project was not found! Please check that the directory exists!"
    echo "Dir was: ${PROJECT}"
    echo ""
    exit $E_NODIR
fi


if [ ! -d ${TARGETDIR} ]
then
    echo ""
    echo "Target directory was not found!"
    echo "Dir was: ${PROJECT}"
    echo ""
    exit $E_NODIR
fi


USER=$(whoami)
LATEST=$(readlink /hri/sit/builds/latest)
COMPLETEDIR="${TARGETDIR}/${USER}_${LATEST}"


echo "User: ${USER}"
echo "Date of SIT build: ${LATEST}"
echo "Target directory: ${COMPLETEDIR}"
echo "======================================"


ExportWizard.py Distribute OutputDir "package=${PROJECT} outputDir=${COMPLETEDIR}"


if [ "$?" -ne "0" ]
then
    echo ""
    echo "The tree was NOT copied successfull!"
    echo "Some unknown error occured."
    exit $E_UNKNOWN
fi



if [ ! -d ${COMPLETEDIR} ]
then
    echo ""
    echo "The tree was NOT copied successfull!"
    echo "${COMPLETEDIR} does not exist!"
    echo ""
    exit $E_NODIR
fi


echo "The tree has been copied successfull!"
echo
echo "PLEASE add the following lines to your start script in order to work with the frozen tree:"
echo "==========================================================================================="
echo "export SIT_VERSION=${USER}_${LATEST}"
echo "export SIT=${COMPLETEDIR}"
echo "source ${COMPLETEDIR}/DevelopmentTools/ToolBOSCore/2.0/BashSrc"
echo ""


# EOF
