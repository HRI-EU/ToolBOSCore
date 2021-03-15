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


import tempfile
import unittest

from ToolBOSCore.BuildSystem.GlobalInstallLog import GlobalInstallLog
from ToolBOSCore.Settings                     import ToolBOSConf
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
        logEntry = GlobalInstallLog( ToolBOSConf.canonicalPath,
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
