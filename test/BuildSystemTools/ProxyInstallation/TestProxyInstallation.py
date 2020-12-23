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
import unittest

from ToolBOSCore.BuildSystem.BuildSystemTools     import BuildSystemTools
from ToolBOSCore.Platforms                        import Platforms
from ToolBOSCore.Storage                          import ProxyDir
from ToolBOSCore.Storage                          import SIT
from ToolBOSCore.Util                             import Any
from ToolBOSCore.Util                             import FastScript



class TestProxyInstallation( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_proxyInstallation( self ):
        oldcwd         = os.getcwd()
        packageName    = 'ExamplePackage'
        packageVersion = '1.0'
        category       = 'Applications'
        projectRoot    = os.path.join( '.', packageName, packageVersion )
        output         = io.StringIO() if Any.getDebugLevel() <= 3 else None
        platform       = Platforms.getHostPlatform()
        sitPath        = SIT.getPath()


        # build + install package
        FastScript.changeDirectory( projectRoot )

        bst = BuildSystemTools()
        bst.setStdOut( output )
        bst.setStdErr( output )
        bst.compile()

        Any.requireIsDirNonEmpty( 'build' )
        Any.requireIsDirNonEmpty( os.path.join( 'build', platform ) )
        Any.requireIsDirNonEmpty( 'examples' )
        Any.requireIsDirNonEmpty( os.path.join( 'examples', platform ) )

        for fileName in ( 'ThreadingExampleAtomicOperation',
                          'ThreadingExampleJoin',
                          'ThreadingExampleTraps' ):
            Any.requireIsFileNonEmpty( os.path.join( 'bin', platform, fileName ) )


        if not ProxyDir.isProxyDir( sitPath ):
            self.skip( "%s: Is not a proxy directory" % sitPath )

        bst.makeDocumentation()
        bst.proxyInstall()
        installRoot = os.path.join( sitPath, category, packageName, packageVersion )


        # check result
        Any.requireIsDir( installRoot )
        Any.requireIsDirNonEmpty(  os.path.join( installRoot, 'bin', platform ) )
        Any.requireIsDirNonEmpty(  os.path.join( installRoot, 'doc/html' ) )
        Any.requireIsFileNonEmpty( os.path.join( installRoot, 'doc/html/index.html' ) )
        Any.requireIsFileNonEmpty( os.path.join( installRoot, 'pkgInfo.py' ) )
        Any.requireIsFileNonEmpty( os.path.join( installRoot, 'packageVar.cmake' ) )

        for fileName in ( 'ThreadingExampleAtomicOperation',
                          'ThreadingExampleJoin',
                          'ThreadingExampleTraps' ):
            Any.requireIsFileNonEmpty( os.path.join( installRoot, 'bin',
                                                     platform, fileName ) )


        # clean-up
        bst.uninstall( cleanGlobalInstallation=False )
        bst.distclean()

        self.assertFalse( os.path.exists( installRoot ) )

        FastScript.changeDirectory( oldcwd )


if __name__ == '__main__':
    unittest.main()


# EOF
