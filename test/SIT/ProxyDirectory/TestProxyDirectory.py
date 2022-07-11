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


import os
import tempfile
import unittest

from ToolBOSCore.Settings import ToolBOSConf
from ToolBOSCore.Storage  import ProxyDir
from ToolBOSCore.Storage  import SIT
from ToolBOSCore.Util     import FastScript
from ToolBOSCore.Util     import Any


class TestProxyDirectory( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_createProxyDir( self ):
        sitProxyPath  = tempfile.mkdtemp( prefix='test-' )
        sitRootPath   = SIT.getRootPath()
        # canonicalPath = ToolBOSConf.canonicalPath

        Any.requireIsDir( sitRootPath )

        # proxy directory must not exist, yet (function would refuse otherwise)
        FastScript.remove( sitProxyPath )
        ProxyDir.createProxyDir( sitRootPath, sitProxyPath )

        Any.requireIsDir( os.path.join( sitProxyPath, 'Libraries' ) )
        Any.requireIsDir( os.path.join( sitProxyPath, 'Modules/BBCM' ) )
        Any.requireIsDir( os.path.join( sitProxyPath, 'Libraries' ) )

        # ignore ToolBOSCore itself which might not be released in this version, yet
        # (see TBCORE-2330)
        # self.assertTrue( os.path.islink( os.path.join( sitProxyPath, canonicalPath ) ) )

        self.assertTrue( os.path.islink( os.path.join( sitProxyPath, 'External/java/1.8' ) ) )

        FastScript.remove( sitProxyPath )


    def test_findProxyInstallations( self ):
        # check if user has a valid proxy:
        sitRootPath  = SIT.getParentPath()
        sitProxyPath = SIT.getPath()

        Any.requireIsDir( sitRootPath )
        Any.requireIsDir( sitProxyPath )

        # skip test if no Proxy-SIT was configured
        if not ProxyDir.isProxyDir( sitProxyPath ):
            self.skipTest( 'No Proxy-SIT configured' )

        # create a fake package directory within the proxy...
        packageName    = 'UnittestABCDEF123'
        goodNameDir    = os.path.join( sitProxyPath, 'Libraries', packageName )
        goodVersionDir = os.path.join( goodNameDir, '42.0' )
        badVersionDir  = os.path.join( goodNameDir, '21.0' )
        FastScript.mkdir( goodVersionDir )

        resultList     = ProxyDir.findProxyInstallations()
        self.assertTrue( len(resultList) >= 1 )   # may be greater if developer has real software installed in proxy

        self.assertTrue( goodVersionDir in resultList )
        self.assertFalse( badVersionDir in resultList )

        # clean-up
        FastScript.remove( goodNameDir )


if __name__ == '__main__':
    unittest.main()


# EOF
