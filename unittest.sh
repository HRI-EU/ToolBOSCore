#!/bin/bash
#
#  launches the unittest suite
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

source useFromHere.sh
# shellcheck source=/dev/null
source "${TOOLBOSCORE_ROOT}/include/Unittest.bash"

CWD=$(pwd)


cd "${CWD}/test/BuildSystemTools" && runTest ./TestBuildSystemTools.sh
cd "${CWD}/test/MakeShellfiles"   && runTest ./TestMakeShellfiles.py
cd "${CWD}/test/Misc"             && runTest ./TestMisc.sh
cd "${CWD}/test/SoftwareQuality"  && runTest ./TestSoftwareQuality.sh
cd "${CWD}/test/SIT"              && runTest ./TestSIT.sh
cd "${CWD}/test/Tools"            && runTest ./TestTools.sh
cd "${CWD}/test/UserSetup"        && runTest ./TestUserSetup.sh


# we managed to get here --> success
exit 0


# EOF
