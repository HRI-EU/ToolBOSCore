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
