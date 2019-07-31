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

from six import StringIO

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
        output         = StringIO() if Any.getDebugLevel() <= 3 else None
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
