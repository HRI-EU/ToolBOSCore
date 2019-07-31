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


import logging
import os
import unittest

from ToolBOSCore.Packages.PackageCreator import makeShellfiles
from ToolBOSCore.Settings                import ToolBOSSettings
from ToolBOSCore.Util                    import FastScript
from ToolBOSCore.Util                    import Any


class TestMakeShellfiles( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )

    def test_makeShellfiles( self ):
        projectRoot    = FastScript.getEnv( 'TOOLBOSCORE_ROOT' )
        installDir     = os.path.join( projectRoot, 'install' )
        fileNamePrefix = '%s-%s-' % ( ToolBOSSettings.packageName,
                                      ToolBOSSettings.packageVersion )

        # create shellfiles
        makeShellfiles( projectRoot )

        # check result
        for fileName in ( 'pkgInfo.py', 'BashSrc', 'CmdSrc.bat' ):
            expectedFile = fileNamePrefix + fileName
            resultFile   = os.path.join( installDir, fileName )

            logging.info( 'expecting content as in: %s' % expectedFile )
            logging.info( 'comparing with:          %s' % resultFile )

            expectedContent = FastScript.getFileContent( expectedFile )
            resultContent   = FastScript.getFileContent( resultFile )

            # check if each line occurs in 'resultContent', except the line
            # of the SVN revision as this frequently changes
            for line in expectedContent.splitlines():
                if not line.startswith( 'revision' ):
                    try:
                        self.assertTrue( resultContent.find( line ) != -1 )
                    except AssertionError:
                        logging.error( 'line not found: %s' % line )
                        raise


if __name__ == '__main__':
    unittest.main()


# EOF
