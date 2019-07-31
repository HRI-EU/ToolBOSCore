#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  launches the unit testing
#
#  Copyright (C)
#  Honda Research Institute Europe GmbH
#  Carl-Legien-Str. 30
#  63073 Offenbach/Main
#  Germany
#
#  UNPUBLISHED PROPRIETARY MATERIAL.
#  ALL RIGHTS RESERVED.
#
#


import os
import tempfile
import unittest

from ToolBOSCore.Settings import ToolBOSSettings
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
        canonicalPath = ToolBOSSettings.canonicalPath

        Any.requireIsDir( sitRootPath )

        # proxy directory must not exist, yet (function would refuse otherwise)
        FastScript.remove( sitProxyPath )
        ProxyDir.createProxyDir( sitRootPath, sitProxyPath )

        Any.requireIsDir( os.path.join( sitProxyPath, 'Libraries' ) )
        Any.requireIsDir( os.path.join( sitProxyPath, 'Modules/BBCM' ) )
        Any.requireIsDir( os.path.join( sitProxyPath, 'Libraries' ) )

        self.assertTrue( os.path.islink( os.path.join( sitProxyPath, canonicalPath ) ) )
        self.assertTrue( os.path.islink( os.path.join( sitProxyPath, 'External/java/1.7' ) ) )

        FastScript.remove( sitProxyPath )


    def test_findProxyInstallations( self ):
        # check if user has a valid proxy:
        sitRootPath  = SIT.getParentPath()
        sitProxyPath = SIT.getPath()

        Any.requireIsDir( sitRootPath )
        Any.requireIsDir( sitProxyPath )
        ProxyDir.requireIsProxyDir( sitProxyPath )

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
