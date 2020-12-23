#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  clones a particular SIT package from blessed repository
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
import subprocess
import sys

from ToolBOSCore.Packages import PackageDetector, ProjectProperties
from ToolBOSCore.Storage  import SIT
from ToolBOSCore.Tools    import Git
from ToolBOSCore.Util     import Any
from ToolBOSCore.Util     import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Clones the source code of a particular package from its blessed ' + \
       'Git repository into a local Git repository.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-u', '--user',
                    help='account name to use for Git server' )

argman.addArgument( 'package',
                    help='absolute or canonical package path' )

argman.addExample( '%(prog)s Libraries/MasterClock/1.6' )
argman.addExample( '%(prog)s ${SIT}/Libraries/MasterClock/1.6' )
argman.addExample( '%(prog)s -v /hri/sit/latest/Libraries/MasterClock/1.6' )

args = vars( argman.run() )

package  = SIT.strip( args['package'] )  # strip-off the SIT part if provided
userName = args[ 'user' ]


#----------------------------------------------------------------------------
# Functions
#----------------------------------------------------------------------------


def main( package ):

    # When using shell tab-completion on SIT paths for the canonical path,
    # a trailing slash might be added. Remove this before proceeding.

    if package.endswith( '/' ):
        package = package[:-1]
        logging.debug( 'package truncated to: %s', package )


    try:
        ProjectProperties.requireIsCanonicalPath( package )
    except AssertionError as details:
        logging.error( details )
        raise SystemExit


    # stop if package is maintained via SVN

    svnUrl = ProjectProperties.getSVNLocationFromFilesystem( package )

    if svnUrl:
        logging.debug( 'found SVN URL: %s', svnUrl )
        logging.error( '' )
        logging.error( 'Package is maintained via SVN and cannot be cloned.' )
        logging.error( 'Use GitCheckout.py to access it in Git-style using the git-svn bridge :-)' )
        logging.error( '' )
        sys.exit( -2 )


    # try to look-up repository URL from SIT, if not found do at least
    # a good guess

    installRoot = os.path.join( SIT.getPath(), package )

    try:
        detector    = PackageDetector.PackageDetector( installRoot )
        detector.retrieveMetaInfoFromSIT()

        url         = detector.gitOrigin

    except AssertionError as e:
        logging.error( e )
        raise SystemExit()


    # logging.debug( 'guessing Git location...' )
    # url = ProjectProperties.guessGitLocation( package )     # TODO: implement guessing

    if not url:
        logging.error( 'unable to determine Git repository location' )
        sys.exit( -1 )


    Any.requireIsTextNonEmpty( url )

    repo = Git.RemoteGitRepository( url )

    # warn if cloning from unofficial host (see CIA-1062)
    repo.checkIsOnMasterServer()



    if userName:
        repo.setUserName( userName )

    Any.setDebugLevel( logging.DEBUG )   # print executed command
    repo.clone()


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


try:
    main( package )

except KeyboardInterrupt:
    # user pressed <Ctrl+C>
    print( '' )
    logging.info( 'cancelled' )
    sys.exit( -1 )

except ( AssertionError, OSError, subprocess.CalledProcessError ) as e:
    logging.error( e )

    # show stacktrace in verbose mode
    if Any.getDebugLevel() >= 5:
        raise

    sys.exit( -1 )


# EOF
