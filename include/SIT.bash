#
#  functions to query SIT path names
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
#


export SIT_PROXY_LINK_NAME=parentTree


function SIT_getPath()
{
    if [[ -z "${SIT}" ]];
    then

        echo "\$SIT: variable undefined"
        exit 1

    elif [[ ! -d "${SIT}" ]];
    then

        echo "${SIT}: No such directory"
        exit 1

    fi

    echo "${SIT}"
}


function SIT_getRootPath()
{
    LOOPGUARD=10;    # allow max. 10 nesting levels of proxy directories
    SITPATH=$(SIT_getPath)

    while [ -e "${SITPATH}/${SIT_PROXY_LINK_NAME}" ] && [ "${LOOPGUARD}" -gt 0 ]
    do

        SITPATH="${SITPATH}/${SIT_PROXY_LINK_NAME}"
        LOOPGUARD=$(( LOOPGUARD - 1 ))

    done

    readlink -f "${SITPATH}"
}


function SIT_isProxyDir()
{
    if [[ -L "${1}/${SIT_PROXY_LINK_NAME}" ]];
    then

        echo 1

    else

        echo 0

    fi
}


# EOF
