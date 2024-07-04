#!/bin/bash
#
#  Setup Python environment
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


set -euxo pipefail

export PIP_INDEX_URL="https://package-cache.honda-ri.de/repository/pypi-proxy/simple"
export REQUESTS_CA_BUNDLE="/usr/local/share/ca-certificates/HRI-CA_cert_2020.crt"

PKG_NAME=$(basename "${PWD}")


if [[ -d "/hri/localdisk" ]]
then
    ENV_ROOT="/hri/localdisk/${USER}/venvs/${PKG_NAME}"
else
    ENV_ROOT="./venv"
fi


rm -rf "${ENV_ROOT}"

python3 -m venv "${ENV_ROOT}"
source "${ENV_ROOT}/bin/activate"

pip install --trusted-host package-cache.honda-ri.de --upgrade pip
pip install --trusted-host package-cache.honda-ri.de -r requirements.txt


# EOF
