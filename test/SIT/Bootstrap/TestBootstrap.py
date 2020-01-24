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

from ToolBOSCore.Storage import SIT
from ToolBOSCore.Storage import CopyTreeFilter
from ToolBOSCore.Util    import FastScript
from ToolBOSCore.Util    import Any


class TestBootstrap( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_bootstrapSIT( self ):
        basePkgList = SIT.getMinRequirements()
        outputDir   = tempfile.mkdtemp( prefix='test-' )


        # create test SIT
        copyFilter = CopyTreeFilter.CopyTreeFilter( [] )  # skip copying binaries
        copyFilter.filterDocu = True
        SIT.bootstrap( outputDir, True, True, copyFilter.callback, False )


        # check if all essential packages are available
        for package in basePkgList:
            Any.requireIsFile( os.path.join( outputDir, package, 'packageVar.cmake' ) )

        # check for Module-Index directory
        Any.requireIsDir( os.path.join( outputDir, 'Modules', 'Index' ) )


        # clean-up
        FastScript.remove( outputDir )


if __name__ == '__main__':
    unittest.main()


# EOF
