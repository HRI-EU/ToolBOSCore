#!/usr/bin/env python3
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

argman.addArgument( '-r', '--repofile', action='store',
                    help="Python file with whitelist of projects to visit, "
                         "e.g.: projectRoots = ['./path/to/Foo', './path/to/Bar']" )

argman.addArgument( 'command', help='command to execute within projects' )

argman.addExample( '%(prog)s "svn st"' )
argman.addExample( '%(prog)s -v -f script.sh' )
argman.addExample( '%(prog)s -r repoInfo.py "BST.py -q"' )

args         = vars( argman.run() )

command      = args['command']
ignoreErrors = args['ignore_errors']
repofile     = args['repofile']
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

    if repofile:
        Any.requireIsFileNonEmpty( repofile )

        content = FastScript.execFile( repofile )
        try:
            dirList = content["projectRoots"]
            Any.requireIsList( dirList )
        except ( AssertionError, KeyError ):
            logging.error( "Key 'projectRoots' found but is of type '%s'", type(dirList) )
            logging.error( "Please specify the whitelist of project root paths as a list "
                           "named 'projectRoots' in %s", repofile )
            return False

        logging.debug( 'Project roots specified in %s: %s', repofile, dirList )

    else:
        allDirList = []                  #all dirs and subdir that contains pkgInfo.py or CMakeList.txt
        topDirList = []

        ignorePattern  = re.compile( "^/.[aA-zZ]*$" )

        for path in FastScript.getDirsInDirRecursive( excludePattern=ignorePattern ):
            if os.path.isfile( os.path.join( path, 'pkgInfo.py' ) ):
                allDirList.append( path )
            elif os.path.isfile( os.path.join( path, 'CMakeLists.txt' ) ):
                allDirList.append( path )

        # topDirList will contain all main directories which also have subdirectories in allDirList
        for a in allDirList:
            for b in allDirList:
                if a == b:
                    continue
                elif a + "/" in b:
                    topDirList.append(b)
                else:
                    continue

        # remove elements in topDirList from allDirList
        dirList = [ x for x in allDirList if x not in topDirList ]

        logging.debug( 'Project roots found are : %s', dirList )

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


if repofile and not Any.isFile( repofile ):
    logging.error( '%s: No such file', repofile )
    sys.exit( -1 )


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
