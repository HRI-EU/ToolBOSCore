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


import tempfile
import unittest

from ToolBOSCore.BuildSystem.GlobalInstallLog import GlobalInstallLog
from ToolBOSCore.Settings                     import ToolBOSSettings
from ToolBOSCore.Util                         import FastScript
from ToolBOSCore.Util                         import Any


class GlobalInstallLogEntryTest( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_addGlobalInstallLog( self ):
        msgType  = 'NEW'
        message  = 'Test message (unittest)'


        # create log entry
        logEntry = GlobalInstallLog( ToolBOSSettings.canonicalPath,
                                     isFirstInstall=False,
                                     msgType=msgType,
                                     message=message )
        fileName = tempfile.mkstemp( prefix='test-' )[1]
        logEntry.setFileName( fileName )
        logEntry.writeFile()

        Any.requireIsFileNonEmpty( fileName )
        content  = FastScript.getFileContent( fileName )


        # check result
        self.assertTrue( content.find( msgType ) > 0, "log file incorrect" )
        self.assertTrue( content.find( message ) > 0, "log file incorrect" )


        # clean-up
        FastScript.remove( fileName )


if __name__ == '__main__':
    unittest.main()



# EOF
