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


import io
import os
import tempfile
import unittest

from ToolBOSCore.BuildSystem.BuildSystemTools import BuildSystemTools
from ToolBOSCore.Packages.PackageCreator    import PackageCreator_C_Library
from ToolBOSCore.Platforms                    import Platforms
from ToolBOSCore.Platforms                    import CrossCompilation
from ToolBOSCore.Util                         import FastScript
from ToolBOSCore.Util                         import Any



class TestWineMSVC( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_wineMSVC( self ):
        oldcwd         = os.getcwd()
        tmpDir         = tempfile.mkdtemp( prefix='test-' )
        packageName    = 'HelloWorld'
        packageVersion = '42.0'
        projectRoot    = os.path.join( tmpDir, packageName, packageVersion )
        output         = io.StringIO() if Any.getDebugLevel() <= 3 else None
        hostPlatform   = Platforms.getHostPlatform()
        targetPlatform = 'windows-amd64-vs2012'

        if targetPlatform not in CrossCompilation.getSwitchEnvironmentList( hostPlatform ):
            self.skipTest( '%s to %s cross-compilation not supported' % \
                           ( hostPlatform, targetPlatform ) )


        # create package on-the-fly
        PackageCreator_C_Library( packageName, packageVersion,
                                  outputDir=tmpDir ).run()


        # build package
        FastScript.changeDirectory( projectRoot )

        bst = BuildSystemTools()
        bst.setStdOut( output )
        bst.setStdErr( output )
        bst.setTargetPlatform( targetPlatform )
        bst.compile()


        # check result
        Any.requireIsDirNonEmpty( os.path.join( projectRoot, 'build' ) )
        Any.requireIsDirNonEmpty( os.path.join( projectRoot, 'build', targetPlatform ) )
        Any.requireIsDirNonEmpty( os.path.join( projectRoot, 'lib' ) )
        Any.requireIsDirNonEmpty( os.path.join( projectRoot, 'lib', targetPlatform ) )
        Any.requireIsDirNonEmpty( os.path.join( projectRoot, 'src' ) )
        Any.requireIsDirNonEmpty( os.path.join( projectRoot, 'test' ) )
        Any.requireIsDirNonEmpty( os.path.join( projectRoot, 'test', targetPlatform ) )


        # clean-up
        bst.distclean()
        self.assertFalse( os.path.exists( os.path.join( projectRoot, 'build' ) ) )
        self.assertFalse( os.path.exists( os.path.join( projectRoot, 'lib' ) ) )
        FastScript.remove( tmpDir )
        FastScript.changeDirectory( oldcwd )


if __name__ == '__main__':
    unittest.main()


# EOF
