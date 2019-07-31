#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  checkout a particular package from SVN, using the git-svn bridge
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
from ToolBOSCore.Storage  import GitSVNBridge
from ToolBOSCore.Storage  import SIT
from ToolBOSCore.Util     import Any
from ToolBOSCore.Util     import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Download the source code of a particular package from an SVN ' + \
       'server into a local git repository (using the git-svn bridge). ' + \
       'Mind that git will clone the entire repository, so this may ' + \
       'take some time and diskspace. Please note that certain SVN ' + \
       'servers may require additional steps before connecting, such ' + \
       'as setting up "authorized keys" or SSH agents.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-u', '--user',
                    help='account name to use for SVN server' )

argman.addArgument( 'package',
                    help='absolute or canonical package path' )

argman.addExample( '%(prog)s Libraries/MasterClock/1.6' )
argman.addExample( '%(prog)s -v -u monthy Libraries/MasterClock/1.6' )
argman.addExample( '%(prog)s ${SIT}/Libraries/MasterClock/1.6' )

args = vars( argman.run() )

package  = SIT.strip( args['package'] )  # strip-off the SIT part if provided
userName = args[ 'user' ]


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


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


# look for repository URL

sitPath     = SIT.getPath()
installRoot = os.path.join( sitPath, package )
url         = None
detector    = None

try:
    detector = PackageDetector.PackageDetector( installRoot )
except AssertionError:
    pass                            # package not found in SIT


if detector is not None:

    detector.retrieveMetaInfoFromSIT()

    if detector.gitOrigin:

        logging.info( 'found Git repo: %s', detector.gitOrigin )
        logging.info( 'Package is maintained via Git and does not need the Git-SVN bridge.' )
        logging.info( 'Please use GitClone.py instead.' )
        sys.exit( -2 )

    elif detector.svnRepositoryURL:

        url = detector.svnRepositoryURL


if url is None:
    # try to guess SVN location as last resort
    url = ProjectProperties.guessSVNLocation( package )


Any.requireIsTextNonEmpty( url )


# strip-off the version from the URL to fetch the entire package
# (e.g. "Serialize" instead of "3.0" only)

url = os.path.dirname( url )


# clone the package using the Git-SVN bridge

repo = GitSVNBridge.GitSVNBridge( url )
repo.checkIsOnMasterServer()

Any.requireIsTextNonEmpty( url )

try:
    repo.setUserName( userName )

    Any.setDebugLevel( logging.DEBUG )   # print executed command
    repo.clone()


except OSError as details:
    logging.error( details.strerror )
except subprocess.CalledProcessError as details:
    raise SystemExit()
except KeyboardInterrupt:
    # user pressed <Ctrl+C>
    sys.exit( -1 )


# EOF
