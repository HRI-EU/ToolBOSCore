#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  create a new SVN repository and do initial package import
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
import os.path

from ToolBOSCore.Settings import ToolBOSSettings
from ToolBOSCore.Storage  import CMakeLists
from ToolBOSCore.Tools    import SVN
from ToolBOSCore.Util     import Any
from ToolBOSCore.Util     import ArgsManagerV2
from ToolBOSCore.Util     import FastScript


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Imports everything from the current directory into SVN. The ' \
       'install category information is taken from the CMakeLists.txt ' \
       'file so please check it before. To import a package, please ' \
       'call this script from the directory which has all the version ' \
       'directories inside (see example).'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addExample( 'cd MyPackage' )
argman.addExample( '%(prog)s' )

argman.run()


#----------------------------------------------------------------------------
# Helper functions
#----------------------------------------------------------------------------


def findFile( fileName ):
    """
        Tries to find a file called <fileName> somewhere below the
        directory named 'path'.

        If none is found, an IOError will be raised.

        If multiple files would be present (e.g. within multiple versions
        of the package), only the first one is returned. However, most
        likely at module import time there shouldn't be so many parallel
        versions, yet. And additionally, the package's SIT category
        most often does not change.
    """
    for subdir in FastScript.getDirsInDir( os.getcwd() ):
        filePath = os.path.join( subdir, fileName )

        if os.path.exists( filePath ):
            logging.debug( 'probing for %s: found', filePath )
            return filePath
        else:
            logging.debug( 'probing for %s: Not found', filePath )

    raise IOError( 'No %s found' % fileName )


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


# discover SVN server to use, package name and category
cwd           = os.getcwd()
server        = ToolBOSSettings.getConfigOption( 'defaultSVNServer' )
reposPath     = ToolBOSSettings.getConfigOption( 'defaultSVNRepositoryPath' )
packageName   = os.path.basename( cwd )
category      = None

try:
    # search for CMakeLists.txt
    filePath  = findFile( 'CMakeLists.txt' )
    Any.requireIsFileNonEmpty( filePath )

    content   = FastScript.getFileContent( filePath )
    Any.requireIsTextNonEmpty( content )

    category  = CMakeLists.getCategory( content )
    Any.requireIsTextNonEmpty( category )

except IOError:
    msg = 'It seems you are not calling this script from the '      + \
          '"PackageName" directory (the one that contains all the ' + \
          'version directories).     Maybe need "cd MyPackage" '    + \
          'or "cd .."?'

    FastScript.prettyPrintError( msg )


repositoryURL = SVN.SVNRepository.composeURL( server, reposPath,
                                              category, packageName )

Any.requireIsTextNonEmpty( server        )
Any.requireIsTextNonEmpty( reposPath     )
Any.requireIsTextNonEmpty( packageName   )
Any.requireIsTextNonEmpty( category      )
Any.requireIsTextNonEmpty( repositoryURL )

logging.info( 'server:       %s', server        )
logging.info( 'location:     %s', reposPath     )
logging.info( 'category:     %s', category      )
logging.info( 'package name: %s', packageName   )
logging.info( 'repository:   %s', repositoryURL )


# prevent importing an existing working copy (by looking for ".svn"
# directories)
for root, dirs, files in os.walk( cwd ):
    for entry in dirs:

        if entry == '.svn':
            path = os.path.join( root, entry )
            msg  = 'Found directory "%s"! You can\'t import an ' \
                   'existing working copy!' % path
            FastScript.prettyPrintError( msg )


repo = SVN.SVNRepository( repositoryURL )

# check if repository exists (we won't overwrite!)
try:
    if repo.exists():
        msg = "CANCELLED! Repository exists!"
        FastScript.prettyPrintError( msg )

except ValueError as details:
    if str(details).find( 'Permission denied' ) != -1:
        msg = "CANCELLED! Repository exists! (but permission denied)"
        FastScript.prettyPrintError( msg )


# create new repository
repo.create()


# import content to new repository
logging.info( 'uploading data...' )
cmd = 'svn import -m "initial import" %s' % repositoryURL
FastScript.execProgram( cmd )


# move away original directory and download fresh working copy
logging.debug( 'cd ..' )
FastScript.changeDirectory( '..' )

oldName = os.path.basename( cwd )
bakName = oldName + '.bak'
logging.info( 'renaming %s --> %s', oldName, bakName )
os.rename( oldName, bakName )

logging.info( 'downloading working copy...' )
repo = SVN.SVNRepository( repositoryURL )
repo.checkout()


logging.info( 'SVN import successful' )

msg = 'Directory structure has been changed! Please go one directory '   + \
      'up     ("cd ..") and call "cd %s" there to reload the ' % oldName + \
      'directory contents!'

FastScript.prettyPrintError( msg )


# EOF
