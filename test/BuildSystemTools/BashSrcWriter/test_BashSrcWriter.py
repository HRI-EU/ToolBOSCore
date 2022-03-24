#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Unittests for Rules.py module
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
import tempfile

from ToolBOSCore.Packages import PackageDetector
from ToolBOSCore.Storage  import BashSrc, PkgInfo
from ToolBOSCore.Util     import Any, FastScript


def test_bashSrcWriter():
    pkgInfoFile    = 'Middleware-pkgInfo.py'
    refBashSrc     = 'Middleware-BashSrc'

    pkgInfoContent = PkgInfo.getPkgInfoContent( filename=pkgInfoFile )
    Any.requireIsDictNonEmpty( pkgInfoContent )

    refFileContent = FastScript.getFileContent( refBashSrc )
    Any.requireIsTextNonEmpty( refFileContent )

    outBashSrc     = tempfile.mktemp( prefix='test-' )

    details        = PackageDetector.PackageDetector( pkgInfoContent=pkgInfoContent )
    details.retrieveMakefileInfo()

    dependencies   = [ 'DevelopmentTools/ToolBOSCore/4.0',
                       'External/anaconda3/envs/common/3.9',
                       'ExternalAdapted/nanomsg/1.1',
                       'Libraries/ToolBOSLib/4.0',
                       'Libraries/IniConfigFile/1.1' ]

    # override auto-detected values for unittesting purposes
    details.inheritedProjects = dependencies
    overrides      = { 'hasLibDir': True }

    writer         = BashSrc.BashSrcWriter( details, overrides )
    writer.write( outBashSrc )

    outFileContent = FastScript.getFileContent( outBashSrc )
    Any.requireIsTextNonEmpty( outFileContent )

    assert outFileContent == refFileContent


if __name__ == "__main__":
    sys.exit( pytest.main( [ '-vv' ] ) )


# EOF
