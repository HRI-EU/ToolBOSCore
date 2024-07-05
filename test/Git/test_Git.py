#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Unittests for Git.py module
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


import pytest
import sys

from ToolBOSCore.Tools import Git


def test_git2https():
    testIn1 = 'git+ssh://git@dmz-gitlab.honda-ri.de/EnvironmentRepresentation/RLDM.git'
    testIn2 =           'git@dmz-gitlab.honda-ri.de/EnvironmentRepresentation/RLDM.git'
    testIn3 =           'git@dmz-gitlab.honda-ri.de/EnvironmentRepresentation/RLDM'

    expected = 'https://dmz-gitlab.honda-ri.de/EnvironmentRepresentation/RLDM.git'

    assert Git.git2https( testIn1 ) == expected
    assert Git.git2https( testIn2 ) == expected
    assert Git.git2https( testIn3 ) == expected


if __name__ == "__main__":
    sys.exit( pytest.main( [ '-vv' ] ) )


# EOF
