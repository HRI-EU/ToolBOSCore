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


import glob
import logging
import os
import unittest

from six import StringIO

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


        for program in pyScripts + shScripts + executables:

            basename = os.path.basename( program )
            Any.requireIsTextNonEmpty( basename )

            logging.info( 'processing %s', basename )

            output   = StringIO()
            cmd      = '%s --help' % program
            fileName = os.path.join( 'ReferenceData', '%s.txt' % basename )

            Any.requireIsTextNonEmpty( cmd )
            Any.requireIsTextNonEmpty( fileName )

            FastScript.execProgram( cmd, stdout=output, stderr=output )

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
