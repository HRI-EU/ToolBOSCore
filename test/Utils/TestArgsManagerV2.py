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

from ToolBOSCore.Util                     import Any
from ToolBOSCore.Util                     import ArgsManagerV2
from ToolBOSCore.Util                     import FastScript


class TestArgManagerV2( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_API(self):

        example = 'BST.py   # build (setup once + compile)'
        desc = 'Download the source code of a particular package from SVN. ' \
               'By default will fetch the HEAD revision, but with "--global" ' \
               'will checkout the revision that was used at last globalinstall ' \
               'time. Please note that certain SVN servers may require ' \
               'additional steps before connecting, such as setting up ' \
               '"authorized keys" or SSH agents.'

        argman  = ArgsManagerV2.ArgsManager(desc)

        argman.addArgument('-a', '--all', action='store_true',
                           help='checkout full repository (not just specified version)')

        argman.addArgument('-g', '--global', action='store_true',
                           help='fetch last globally installed revision')

        argman.addExample('%(prog)s -a Libraries/MasterClock/1.6       # full repository')
        argman.addExample('%(prog)s -v -u monthy --global Libraries/MasterClock/1.6')
        argman.addExample( example )

        argman.setAllowUnknownArgs( True )

        args = vars(argman.run( [ '-v','--all' ] ) )

        self.assertTrue( args['all'] )
        self.assertTrue( args['verbose'] )
        self.assertFalse( args['global'] )


if __name__ == '__main__':
    unittest.main()


# EOF
