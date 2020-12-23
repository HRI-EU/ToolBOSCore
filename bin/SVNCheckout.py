#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  checkout a particular package from SVN
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


import logging
import os
import subprocess
import sys

from ToolBOSCore.Packages import ProjectProperties
from ToolBOSCore.Storage  import PkgInfo, SIT
from ToolBOSCore.Tools    import SVN
from ToolBOSCore.Util     import Any, ArgsManagerV2, FastScript


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Download the source code of a particular package from SVN. ' \
       'By default will fetch the HEAD revision, but with "--global" ' \
       'will checkout the revision that was used at last globalinstall ' \
       'time. Please note that certain SVN servers may require ' \
       'additional steps before connecting, such as setting up ' \
       '"authorized keys" or SSH agents.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-a', '--all', action='store_true',
                    help='checkout full repository (not just specified version)' )

argman.addArgument( '-g', '--global', action='store_true',
                    help='fetch last globally installed revision' )

argman.addArgument( '-r', '--revision',
                    help='revision to checkout (default: HEAD)' )

argman.addArgument( '-u', '--user',
                    help='account name to use for SVN server' )

argman.addArgument( 'package',
                    help='package (absolute or canonical path)' )

argman.addExample( '%(prog)s -a Libraries/MasterClock/1.6       # full repository' )
argman.addExample( '%(prog)s -v -u monthy --global Libraries/MasterClock/1.6' )
argman.addExample( '%(prog)s ${SIT}/Libraries/MasterClock/1.6' )
argman.addExample( '%(prog)s -r 30 sit://Libraries/MasterClock/1.6' )

args     = vars( argman.run() )

fetchAll = args['all']
package  = SIT.strip( args['package'] )  # strip-off the SIT part if provided
revision = args['revision']
userName = args[ 'user' ]

if not revision:
    revision = 'HEAD'


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


# first try to look-up repository URL from SIT, if not found do at least
# a good guess

url = ProjectProperties.guessSVNLocation( package )


# strip-off the version from the URL to fetch entire repository (if requested)
if fetchAll:
    url = os.path.dirname( url )

Any.requireIsTextNonEmpty( url )


# revision to fetch
if args[ 'global' ]:
    try:
        revision = PkgInfo.getSVNRevision( package )

        Any.requireIsInt( revision )
        Any.require( revision != -1 )
        logging.info( 'SVN revision = %d', revision )

    except ( AssertionError, IOError ):
        logging.error( '' )
        logging.error( 'unable to detect last globally installed revision' )
        logging.error( 'falling back to HEAD revision' )
        logging.error( '' )


projectName = ProjectProperties.splitPath( package )[1]
Any.requireIsTextNonEmpty( projectName )


# create directory with name of package when downloading a particular version,
# and cd into it
if not fetchAll:
    FastScript.mkdir( projectName )
    FastScript.changeDirectory( projectName )

repo = SVN.SVNRepository( url )
repo.checkIsOnMasterServer()

try:
    if userName:
        repo.setUserName( userName )
    else:
        repo.setConfiguredUserName()

    repo.checkout( revision )

    if os.path.exists( projectName ):
        logging.debug( 'chmod 0700 %s', projectName )
        os.chmod( projectName, 0o700 )

except OSError as details:
    logging.error( details.strerror )
except subprocess.CalledProcessError as details:
    raise SystemExit()
except KeyboardInterrupt:
    # user pressed <Ctrl+C>
    sys.exit( -1 )


# EOF
