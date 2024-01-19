#!/bin/bash
#
#  detects basic project information to be used in custom build scripts
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


#----------------------------------------------------------------------------
# Includes
#----------------------------------------------------------------------------


source "${TOOLBOSCORE_ROOT}/include/SIT.bash"


#----------------------------------------------------------------------------
# The package maintainer may want to preset values before auto-detecting
#----------------------------------------------------------------------------


if [[ -r definitions.sh ]]
then
    echo "sourcing definitions.sh"
    # shellcheck source=/dev/null
    source ./definitions.sh
fi


#----------------------------------------------------------------------------
# Useful constants
#----------------------------------------------------------------------------


# The user may specify BST_INSTALL_PREFIX so that the SIT will be placed
# inside, useful for testing (see TBCORE-1104).
#
# Do not alter $SIT otherwise.

if [[ -z ${BST_INSTALL_PREFIX+x} ]]
then
    export BST_INSTALL_PREFIX=""
fi

if [[ -z "${BST_INSTALL_PREFIX}" ]]
then
    # do nothing, otherwise mostly everybody (who does not use BST_INSTALL_PREFIX)
    # sourcing this file will get their $SIT altered, which we really don't want
    # shellcheck disable=SC2269
    SIT=${SIT}
else
    SIT=${BST_INSTALL_PREFIX}
fi

if [[ -z ${PROJECT_NAME+x} ]]
then
    export PROJECT_NAME=""
fi

if [[ -z "${PROJECT_NAME}" ]]
then
    PROJECT_NAME=$(basename "$(dirname "${PWD}")")
fi

if [[ -z ${PROJECT_VERSION+x} ]]
then
    export PROJECT_VERSION=""
fi

if [[ -z "${PROJECT_VERSION}" ]]
then
    PROJECT_VERSION=$(basename "${PWD}")                # 2 digits
fi

echo "Major version: ${PROJECT_VERSION}" | awk -F. '{ print $1 }'
echo "Minor version: ${PROJECT_VERSION}" | awk -F. '{ print $2 }'

if [[ -z ${PROJECT_CATEGORY+x} ]]
then
    PROJECT_CATEGORY=""
fi

if [[ -z "${PROJECT_CATEGORY}" && -r "CMakeLists.txt" ]]
then
  PROJECT_CATEGORY=$(awk '/BST_INSTALL_CATEGORY/ { gsub( "[:'\)']","" ); print $2 }' < CMakeLists.txt)
else
  PROJECT_CATEGORY="UnableToDetectCategory"
fi

CANONICAL_PATH=${PROJECT_CATEGORY}/${PROJECT_NAME}/${PROJECT_VERSION}
PROJECT_ROOT=${SIT}/${CANONICAL_PATH}
INSTALL_ROOT=${PROJECT_ROOT}
SRC_TARBALL_NAME=sources.tar.bz2
BIN_TARBALL_NAME=package.tar.bz2
SOURCES_DIR=sources
PACKAGE_DIR=package
BUILD_DIR=src/build/${MAKEFILE_PLATFORM}

EXIT_FAILURE=1


if [ -z "${BST_BUILD_JOBS}" ]
then
  export BST_BUILD_JOBS=1
fi


#----------------------------------------------------------------------------
# The package maintainer may want to override or provide something more
#----------------------------------------------------------------------------


if [[ -r definitions.sh ]]
then
    # shellcheck source=/dev/null
    source ./definitions.sh
fi


#----------------------------------------------------------------------------
# Utility commands
#----------------------------------------------------------------------------



function MakefileSystem_printvar()
{
    echo ""
    echo "please verify auto-detected information:"
    echo ""
    echo "SIT=${SIT}"
    echo "PROJECT_NAME=${PROJECT_NAME}"
    echo "PROJECT_VERSION=${PROJECT_VERSION}"
    echo "PROJECT_REVISION=${PROJECT_REVISION}"
    echo "PROJECT_PATCHLEVEL_VERSION=${PROJECT_PATCHLEVEL_VERSION}"
    echo "PROJECT_CATEGORY=${PROJECT_CATEGORY}"
    echo "PROJECT_ROOT=${PROJECT_ROOT}"
    echo ""
}


function MakefileSystem_unpackSources()
{
    DIR=src

    if [[ -d ${DIR} ]]
    then
        OLDCWD=$(pwd)
        cd "${DIR}" || exit

        if [[ -r ${SRC_TARBALL_NAME} ]]
        then
            rm -rf "${SOURCES_DIR}"
            mkdir "${SOURCES_DIR}"
            echo "unpacking tarball... (this may take some time)"
            tar xvjf "${SRC_TARBALL_NAME}" -C "${SOURCES_DIR}"
        else
            echo "${SRC_TARBALL_NAME}: No such file"
            exit "${EXIT_FAILURE}"
        fi

        cd "${OLDCWD}" || exit
    fi
}


function MakefileSystem_unpackBinaries()
{
    DIR=precompiled

    if [[ -d ${DIR} ]]
    then
        OLDCWD=$(pwd)
        cd "${DIR}" || exit

        if [[ -r ${BIN_TARBALL_NAME} ]]
        then
            rm -rf "${PACKAGE_DIR}"
            mkdir "${PACKAGE_DIR}"
            echo "unpacking tarball... (this may take some time)"
            tar xjf "${BIN_TARBALL_NAME}" -C "${PACKAGE_DIR}"
        fi

        cd "${OLDCWD}" || exit
    fi
}


function MakefileSystem_makeBuildDir()
{
    OLDCWD=$(pwd)

    if [[ -n "${BUILD_DIR}" && -d "${BUILD_DIR}" ]]
    then
        echo "removing build directory left over from a previous build"
        rm -rf "${BUILD_DIR}"
    fi

    mkdir -pv "${BUILD_DIR}"

    cd "${OLDCWD}" || exit
}


function MakefileSystem_removeVersionSymlinkInSIT()
{
    # remove the two-digit-version symlink (will be re-created later)
    VERSION_SYMLINK=${PROJECT_ROOT}

    if [[ -e ${VERSION_SYMLINK} ]]
    then
        if [[ -L ${VERSION_SYMLINK} ]]
        then
            rm -v "${PROJECT_ROOT}"


        # if it is not a link (most likely it is a directory from a previous
        # platform build) we should ignore this, leading to the current
        # platform being installed into the same directory

        # else
        #     echo "${PROJECT_ROOT} should be a symlink. Please fix manually."
        #     exit ${EXIT_FAILURE}
        fi
    fi
}


function MakefileSystem_renameVersionsInSIT()
{
    TWO_DIGIT_PATH=${PROJECT_ROOT}
    THREE_DIGIT_PATH=${INSTALL_ROOT}

    mv -v "${TWO_DIGIT_PATH}" "${THREE_DIGIT_PATH}"
    ln -sfv "${PROJECT_PATCHLEVEL_VERSION}" "${PROJECT_ROOT}"
}


function MakefileSystem_updateVersionSymlink()
{
    MakefileSystem_removeVersionSymlinkInSIT
    ln -sfv "${PROJECT_PATCHLEVEL_VERSION}" "${PROJECT_ROOT}"
}


function MakefileSystem_installShellfiles()
{
    echo "generating shellfiles"
    BST.py --shellfiles

    mkdir -p "${INSTALL_ROOT}"

    if [[ -d "${INSTALL_ROOT}" ]]
    then
        cp -v install/BashSrc "${INSTALL_ROOT}"
        cp -v install/CmdSrc.bat "${INSTALL_ROOT}"
        cp -v install/pkgInfo.py "${INSTALL_ROOT}"
    else
        echo "${INSTALL_ROOT}: No such directory"
        exit "${EXIT_FAILURE}"
    fi

    if [[ -e packageVar.cmake ]]
    then
        cp -v packageVar.cmake "${INSTALL_ROOT}/packageVar.cmake"

    elif [[ -e install/packageVar.cmake ]]
    then
        cp -v install/packageVar.cmake "${INSTALL_ROOT}/packageVar.cmake"
    fi

    if [[ -e doc/README.txt ]]
    then
        mkdir -p "${INSTALL_ROOT}/doc"
        cp -v doc/README.txt "${INSTALL_ROOT}/doc/README.txt"
    fi

    if [[ -e doc/SVN-Log.txt ]]
    then
        mkdir -p "${INSTALL_ROOT}/doc"
        cp -v doc/SVN-Log.txt "${INSTALL_ROOT}/doc/SVN-Log.txt"
    fi
}


function MakefileSystem_addGlobalInstallLogEntry()
{
    # $1 = path to installed project (incl. version)
    PROJECT_ROOT=$1

    if [[ -z ${TOOLBOSCORE_ROOT} ]]
    then
        echo "TOOLBOSCORE_ROOT is not set, did you source the ToolBOSCore package?"
        exit 1
    fi

    if [[ -z "${PROJECT_ROOT}" ]]
    then
        echo "${FUNCNAME[*]}: Parameter 1 (PROJECT_ROOT) is missing"
        exit 1
    fi

    echo -e "please provide a reason for this global installation:\n"

    if [[ -z ${MAKEFILE_GLOBALINSTALLREASON} ]]
    then
        echo -e "\tReason syntax   = <TYPE>: <short description>\n"
        echo -e "\t                  for example:"
        echo -e "\t                  DOC: PDF manual updated"
        echo -e "\t                  FIX: buffer overflow in _doCompute() fixed"
        echo -e "\t                  NEW: now supports shared memory\n"

        if [[ ${DRY_RUN} == "TRUE" ]]
        then
            echo -e "\n ----------------------------------------------------------------------------"
            echo  "|  This is fake. Will not actually publish this message in dry run mode ;-)  |"
            echo -e " ----------------------------------------------------------------------------\n"
        fi

        echo -en "\tReason          = "

        read -re MAKEFILE_GLOBALINSTALLREASON
    fi

    if [[ ${DRY_RUN} == "TRUE" ]]
    then
        "${TOOLBOSCORE_ROOT}"/bin/AddGlobalInstallLogEntry.py -d "$1" \
                                "${MAKEFILE_GLOBALINSTALLREASON}"
    else
        "${TOOLBOSCORE_ROOT}"/bin/AddGlobalInstallLogEntry.py "$1" \
                                "${MAKEFILE_GLOBALINSTALLREASON}"
    fi
}


function MakefileSystem_generateDefaultReadme()
{
    if [[ ! -e doc/README.txt && -n "${SETUP_SCRIPT}" && -r "${SETUP_SCRIPT}" ]]
    then
        if [[ ! -d doc ]]
        then
            mkdir doc
        fi

        PKG_DESCRIPTION=$(python "${SETUP_SCRIPT}" --description)
        PKG_VERSION=$(python "${SETUP_SCRIPT}" --version)
        PKG_URL=$(python "${SETUP_SCRIPT}" --url)

        { echo -e "\nPACKAGE INFORMATION:";
          echo -e "====================\n";
          echo -e "Description: ${PKG_DESCRIPTION}\n";
          echo -e "Version:     ${PKG_VERSION}\n";
          echo -e "Homepage:    ${PKG_URL}\n"; } >> doc/README.txt
    fi
}


function MakefileSystem_installProcedure()
{
    # $1 = path to installed project (incl. version)

    MakefileSystem_generateDefaultReadme
    MakefileSystem_addGlobalInstallLogEntry "$1"
    MakefileSystem_installShellfiles
}


function MakefileSystem_install()
{
    # $1 = path to installed project (3-digit version)

    MakefileSystem_generateDefaultReadme
    MakefileSystem_installShellfiles
}


function MakefileSystem_globalinstall()
{
    # $1 = path to installed project (3-digit version)

    MakefileSystem_addGlobalInstallLogEntry "$1"
}



# EOF
