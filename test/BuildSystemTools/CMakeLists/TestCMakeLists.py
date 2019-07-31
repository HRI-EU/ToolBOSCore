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


import unittest

from ToolBOSCore.Storage import CMakeLists
from ToolBOSCore.Util    import Any
from ToolBOSCore.Util    import FastScript


class TestCMakeLists( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_getDependenciesFromCMakeLists( self ):
        testFile = 'TestCMakeLists.txt'
        expected = [ 'sit://DevelopmentTools/ToolBOSCore/2.0',
                     'sit://Libraries/BPLBase/7.0',
                     'sit://Libraries/MasterClock/1.7' ]

        content  = FastScript.getFileContent( testFile )
        returned = CMakeLists.getDependencies( content )

        self.assertEqual( expected, returned )


if __name__ == '__main__':
    unittest.main()


# EOF
