#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  launches the unit testing
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


import logging
import os
import unittest

from ToolBOSCore.Packages                import PackageDetector
from ToolBOSCore.Packages.PackageCreator import makeShellfiles
from ToolBOSCore.Settings                import ToolBOSConf
from ToolBOSCore.Util                    import FastScript
from ToolBOSCore.Util                    import Any


class TestMakeShellfiles( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )

    def test_makeShellfiles( self ):
        detector       = PackageDetector.PackageDetector()
        detector.retrieveMakefileInfo()

        projectRoot    = detector.topLevelDir
        installDir     = os.path.join( projectRoot, 'install' )
        fileNamePrefix = ToolBOSConf.packageName + '-'

        # create shellfiles
        makeShellfiles( projectRoot )

        # check result
        for fileName in ( 'pkgInfo.py', 'BashSrc', 'CmdSrc.bat' ):
            expectedFile = fileNamePrefix + fileName
            resultFile   = os.path.join( installDir, fileName )

            logging.info( 'expecting content as in: %s', expectedFile )
            logging.info( 'comparing with:          %s', resultFile )

            expectedContent = FastScript.getFileContent( expectedFile )
            resultContent   = FastScript.getFileContent( resultFile )

            # check if each line occurs in 'resultContent',
            # except volatile data
            for line in expectedContent.splitlines():
                if line.startswith( 'gitOrigin' ) or \
                   line.startswith( 'gitBranch' ) or \
                   line.startswith( 'gitCommitID' ) or \
                   line.startswith( 'patchlevel' ) or \
                   line.startswith( 'maintainer' ):
                    continue

                try:
                    self.assertTrue( resultContent.find( line ) != -1 )
                except AssertionError:
                    logging.error( '%s: line not found: %s', resultFile, line )
                    raise


if __name__ == '__main__':
    unittest.main()


# EOF
