#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Create ground truth data for HelpText unittest
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


#----------------------------------------------------------------------------
# Includes
#----------------------------------------------------------------------------


import glob
import logging
import os

from ToolBOSCore.Platforms          import Platforms
from ToolBOSCore.Util               import Any
from ToolBOSCore.Util               import FastScript
from six import StringIO


verbose = FastScript.getEnv( 'VERBOSE' ) == 'TRUE'

if verbose:
    Any.setDebugLevel( logging.DEBUG )
else:
    Any.setDebugLevel( logging.INFO )


#----------------------------------------------------------------------------
# Private functions
#----------------------------------------------------------------------------


def normalizeOutput( string ):
    result = string

    # replace possible platform names by placeholder

    for candidate in Platforms.getPlatformNames():
        result = result.replace( candidate, '${MAKEFILE_PLATFORM}' )

    return result


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


tcRoot       = FastScript.getEnv( 'TOOLBOSCORE_ROOT' )
hostPlatform = Platforms.getHostPlatform()
binDirNoArch = os.path.join( tcRoot, 'bin' )

Any.requireIsDirNonEmpty( binDirNoArch )

# unset VERBOSE and BST_BUILD_JOBS make output comparable
origEnv      = FastScript.getEnv()
FastScript.unsetEnv( 'VERBOSE' )
FastScript.unsetEnv( 'BST_BUILD_JOBS' )

pyScripts    = glob.glob( os.path.join( binDirNoArch, '*.py' ) )
shScripts    = glob.glob( os.path.join( binDirNoArch, '*.sh' ) )
executables  = glob.glob( os.path.join( binDirNoArch, hostPlatform, '*' ) )


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

    content  = normalizeOutput( output.getvalue() )
    Any.requireIsTextNonEmpty( content )

    FastScript.setFileContent( fileName, content )
    Any.requireIsFileNonEmpty( fileName )


# EOF
