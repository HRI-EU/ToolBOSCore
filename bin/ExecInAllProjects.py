#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Execute a task within each project below the current working directory
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


import logging
import os
import re
import subprocess
import sys

from ToolBOSCore.Util import Any
from ToolBOSCore.Util import ArgsManagerV2
from ToolBOSCore.Util import FastScript


#----------------------------------------------------------------------------
# Commandline parameters
#----------------------------------------------------------------------------


desc = 'Execute a command within each project below the current ' + \
       'working directory.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-f', '--file',
                    help='path to script to execute within each project' )

argman.addArgument( '-i', '--ignore-errors', action='store_true',
                    help='ignore errors', )

argman.addArgument( '-l', '--list', action='store_true',
                    help='whitelist of projects to visit' )

argman.addArgument( 'command', help='command to execute within projects' )

argman.addExample( '%(prog)s "svn st"' )
argman.addExample( '%(prog)s -f script.sh' )
argman.addExample( '%(prog)s -v -l whitelist.txt "svn st"' )

args         = vars( argman.run() )

command      = args['command']
ignoreErrors = args['ignore_errors']
listfile     = args['list']
scriptfile   = args['file']


if not command and not scriptfile:
    raise SystemExit( "You need to specify a command (or script) to execute." )

if command and scriptfile:
    raise SystemExit( "Please do not specify a command (as argument) and a script together." )

if not command and scriptfile:
    command = os.path.realpath( scriptfile )


#----------------------------------------------------------------------------
# Functions
#----------------------------------------------------------------------------


def execInAllProjects( command ):
    Any.requireIsTextNonEmpty( command )


    # determine list of packages (and versions) to visit

    dirList = []
    oldcwd  = os.getcwd()

    if listfile:
        Any.requireIsFileNonEmpty( listfile )

        # read subdirectories from file, and remove trailing newlines
        dirList = FastScript.getFileContent( listfile, splitLines=True )
        dirList = map( str.strip, dirList )
    else:
        noSVN   = re.compile( "^.svn$" )
        for path in FastScript.getDirsInDirRecursive( excludePattern=noSVN ):
            if os.path.isfile( os.path.join( path, 'CMakeLists.txt' ) ):
                dirList.append( path )


    # execute the task

    for entry in dirList:
        workingDir = os.path.realpath( os.path.join( oldcwd, entry ) )

        logging.debug( 'cd %s', workingDir )
        logging.info( 'workingDir=%s', workingDir )

        FastScript.changeDirectory( workingDir )

        try:
            FastScript.execProgram( command )
        except subprocess.CalledProcessError as e:

            if ignoreErrors:
                logging.warning( e )
            else:
                raise

        FastScript.changeDirectory( oldcwd )


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


try:
    execInAllProjects( command )

except KeyboardInterrupt:
    # user pressed <Ctrl+C>
    print( '' )
    logging.info( 'cancelled' )
    sys.exit( -1 )

except ( AssertionError, OSError, subprocess.CalledProcessError ) as e:
    logging.error( 'unable run run command "%s": %s', command, e )

    # show stacktrace in verbose mode
    if Any.getDebugLevel() >= 5:
        raise

    sys.exit( -1 )


# EOF
