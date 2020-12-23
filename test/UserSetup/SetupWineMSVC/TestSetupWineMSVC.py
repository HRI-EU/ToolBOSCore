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


import io
import os
import tempfile
import unittest

from ToolBOSCore.Settings           import UserSetup
from ToolBOSCore.Util               import FastScript
from ToolBOSCore.Util               import Any


class TestSetupWineMSVC( unittest.TestCase ):

    _msvc = 2017

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_setupMSVC_withWine( self ):
        configDir = tempfile.mkdtemp( prefix='test-' )
        output    = io.StringIO() if Any.getDebugLevel() <= 3 else None


        # setup Wine
        UserSetup.setupWineDotNet( configDir, stdout=output, stderr=output, msvc=self._msvc )
        UserSetup.setupMSVC( configDir, self._msvc )


        # check result
        Any.requireIsDirNonEmpty( configDir )
        Any.requireIsFileNonEmpty( os.path.join( configDir, 'user.reg' ) )
        Any.requireIsFileNonEmpty( os.path.join( configDir, 'system.reg' ) )
        Any.requireIsSymlink( os.path.join( configDir, 'dosdevices', 'c:' ) )
        Any.requireIsSymlink( os.path.join( configDir, 'dosdevices', 'z:' ) )

        msvcLink   = os.path.join( configDir, 'drive_c', 'BuildTools' )
        Any.requireIsSymlink( msvcLink )
        msvcTarget = os.path.realpath( msvcLink )
        Any.requireIsDirNonEmpty( msvcTarget )
        self.assertTrue( msvcTarget.find( 'Data/wine.net/1.1' ) > 0 )


        # clean-up
        FastScript.remove( configDir )


    def test_setupMSVC_withoutWine( self ):
        configDir = tempfile.mkdtemp( prefix='test-' )


        # setup MSVC (implcitely setting up Wine if not present)
        UserSetup.setupMSVC( configDir, self._msvc )


        # check result
        Any.requireIsDirNonEmpty( configDir )
        Any.requireIsFileNonEmpty( os.path.join( configDir, 'user.reg' ) )
        Any.requireIsFileNonEmpty( os.path.join( configDir, 'system.reg' ) )
        Any.requireIsSymlink( os.path.join( configDir, 'dosdevices', 'c:' ) )
        Any.requireIsSymlink( os.path.join( configDir, 'dosdevices', 'z:' ) )

        msvcLink   = os.path.join( configDir, 'drive_c', 'BuildTools' )
        Any.requireIsSymlink( msvcLink )
        msvcTarget = os.path.realpath( msvcLink )
        Any.requireIsDirNonEmpty( msvcTarget )
        self.assertTrue( msvcTarget.find( 'Data/wine.net/1.1' ) > 0 )


        # clean-up
        FastScript.remove( configDir )


if __name__ == '__main__':
    unittest.main()


# EOF
