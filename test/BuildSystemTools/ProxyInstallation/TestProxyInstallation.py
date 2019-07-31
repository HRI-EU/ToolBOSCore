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
import unittest

from six import StringIO

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
        output         = StringIO() if Any.getDebugLevel() <= 3 else None
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
