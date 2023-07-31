#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Create ground truth data for HelpText unittest
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


#----------------------------------------------------------------------------
# Includes
#----------------------------------------------------------------------------


import glob
import io
import logging
import os

from ToolBOSCore.Platforms          import Platforms
from ToolBOSCore.Util               import Any
from ToolBOSCore.Util               import FastScript


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

FastScript.remove( 'ReferenceData' )


for program in pyScripts + shScripts + executables:

    basename = os.path.basename( program )
    Any.requireIsTextNonEmpty( basename )

    logging.info( 'processing %s', basename )

    output   = io.StringIO()
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
