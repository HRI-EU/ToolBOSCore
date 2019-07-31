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

from ToolBOSCore.Settings           import UserSetup
from ToolBOSCore.Util               import FastScript
from ToolBOSCore.Util               import Any


class TestSetupWineMSVC( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_setupMSVC_withWine( self ):
        configDir = tempfile.mkdtemp( prefix='test-' )
        output    = StringIO() if Any.getDebugLevel() <= 3 else None


        # setup Wine
        UserSetup.setupWineDotNet( configDir, stdout=output, stderr=output )
        UserSetup.setupMSVC( configDir, 2012 )


        # check result
        Any.requireIsDirNonEmpty( configDir )
        Any.requireIsFileNonEmpty( os.path.join( configDir, 'user.reg' ) )
        Any.requireIsFileNonEmpty( os.path.join( configDir, 'system.reg' ) )
        Any.requireIsSymlink( os.path.join( configDir, 'dosdevices', 'c:' ) )
        Any.requireIsSymlink( os.path.join( configDir, 'dosdevices', 'z:' ) )

        msvcLink   = os.path.join( configDir, 'drive_c', 'msvc-sdk' )
        Any.requireIsSymlink( msvcLink )
        msvcTarget = os.path.realpath( msvcLink )
        Any.requireIsDirNonEmpty( msvcTarget )
        self.assertTrue( msvcTarget.find( 'External/MSVC/10.0' ) > 0 )


        # clean-up
        FastScript.remove( configDir )


    def test_setupMSVC_withoutWine( self ):
        configDir = tempfile.mkdtemp( prefix='test-' )


        # setup MSVC (implcitely setting up Wine if not present)
        UserSetup.setupMSVC( configDir, 2012 )


        # check result
        Any.requireIsDirNonEmpty( configDir )
        Any.requireIsFileNonEmpty( os.path.join( configDir, 'user.reg' ) )
        Any.requireIsFileNonEmpty( os.path.join( configDir, 'system.reg' ) )
        Any.requireIsSymlink( os.path.join( configDir, 'dosdevices', 'c:' ) )
        Any.requireIsSymlink( os.path.join( configDir, 'dosdevices', 'z:' ) )

        msvcLink   = os.path.join( configDir, 'drive_c', 'msvc-sdk' )
        Any.requireIsSymlink( msvcLink )
        msvcTarget = os.path.realpath( msvcLink )
        Any.requireIsDirNonEmpty( msvcTarget )
        self.assertTrue( msvcTarget.find( 'External/MSVC/10.0' ) > 0 )


        # clean-up
        FastScript.remove( configDir )


if __name__ == '__main__':
    unittest.main()


# EOF
