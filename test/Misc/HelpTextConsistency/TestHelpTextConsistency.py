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


import glob
import io
import logging
import os
import subprocess
import unittest

from ToolBOSCore.Platforms import Platforms
from ToolBOSCore.Util      import Any, FastScript


def normalizeOutput( string ):
    result = string

    # replace possible platform names by placeholder

    for candidate in Platforms.getPlatformNames():
        result = result.replace( candidate, '${MAKEFILE_PLATFORM}' )

    return result


class TestHelpTextConsistency( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_helpText( self ):
        tcRoot       = FastScript.getEnv( 'TOOLBOSCORE_ROOT' )
        hostPlatform = Platforms.getHostPlatform()
        binDirNoArch = os.path.join( tcRoot, 'bin' )

        Any.requireIsDirNonEmpty( binDirNoArch )

        pyScripts    = glob.glob( os.path.join( binDirNoArch, '*.py' ) )
        shScripts    = glob.glob( os.path.join( binDirNoArch, '*.sh' ) )
        executables  = glob.glob( os.path.join( binDirNoArch, hostPlatform, '*' ) )


        # unset VERBOSE and BST_BUILD_JOBS to make output comparable
        origEnv      = FastScript.getEnv()
        FastScript.unsetEnv( 'VERBOSE' )
        FastScript.unsetEnv( 'BST_BUILD_JOBS' )


        for program in sorted( pyScripts + shScripts + executables ):

            basename = os.path.basename( program )
            Any.requireIsTextNonEmpty( basename )

            logging.info( 'processing %s', basename )

            output   = io.StringIO()
            cmd      = '%s --help' % program
            fileName = os.path.join( 'ReferenceData', '%s.txt' % basename )

            Any.requireIsTextNonEmpty( cmd )
            Any.requireIsTextNonEmpty( fileName )

            try:
                FastScript.execProgram( cmd, stdout=output, stderr=output )
            except subprocess.CalledProcessError:
                # error is handled below instead
                pass

            expected = FastScript.getFileContent( fileName )
            result   = normalizeOutput( output.getvalue() )

            Any.isTextNonEmpty( expected )
            Any.isTextNonEmpty( result )

            if result != expected:
                logging.info( 'differences in output of %s:', basename )
                logging.info( '<result>\n%s', result )
                logging.info( '</result>' )
                logging.info( '<expected>\n%s', expected )
                logging.info( '</expected>' )

                self.fail( 'help text of %s differs' % basename )

        FastScript.setEnv( origEnv )


if __name__ == '__main__':
    unittest.main()


# EOF
