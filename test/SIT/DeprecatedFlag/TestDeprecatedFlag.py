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
import unittest

from ToolBOSCore.Packages import ProjectProperties
from ToolBOSCore.Settings import ToolBOSSettings
from ToolBOSCore.Util     import FastScript
from ToolBOSCore.Util     import Any


class TestBootstrap( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_isDeprecated( self ):
        canonicalPath = ToolBOSSettings.canonicalPath

        logging.info( 'testing canonicalPath=%s', canonicalPath )
        ProjectProperties.requireIsCanonicalPath( canonicalPath )

        # ToolBOSCore never becomes deprecated, I hope ;-)
        self.assertFalse( ProjectProperties.isDeprecated( canonicalPath ) )

        # check for invalid parameter types (boolean + list)
        self.assertRaises( AssertionError, ProjectProperties.isDeprecated, True )
        self.assertRaises( AssertionError, ProjectProperties.isDeprecated, [ 1, 2, 3 ] )


if __name__ == '__main__':
    unittest.main()


# EOF
