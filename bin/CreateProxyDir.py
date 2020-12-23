#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  creates an SIT sandbox ("proxy directory") for the user
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
import os.path

from ToolBOSCore.Storage import ProxyDir
from ToolBOSCore.Storage import SIT
from ToolBOSCore.Util    import ArgsManagerV2
from ToolBOSCore.Util    import FastScript


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


logging.basicConfig( level=logging.DEBUG )


# TBCORE-1215: consider $SIT as default root path if present (and not a proxy)

sitEnvVar = FastScript.getEnv( 'SIT' )

if sitEnvVar:

    if ProxyDir.isProxyDir( sitEnvVar ):
        sitRootPath  = SIT.getDefaultRootPath()
    else:
        sitRootPath  = sitEnvVar

else:
    sitRootPath = SIT.getDefaultRootPath()


sitProxyPath     = SIT.getDefaultProxyPath()
sitVersion       = SIT.getVersion()


# Replace the username in the sitProxyPath by a generic placeholder so that
# the unittests relying on the consistent output will pass, see TBCORE-1378.
#
# Also replace a particular SIT build identifier.

userName         = FastScript.getCurrentUserName()
sitProxyPathHelp = sitProxyPath.replace( 'latest', '<build>' )
sitProxyPathHelp = sitProxyPathHelp.replace( userName, '<user>' )


desc = 'Create a sandbox for the Software Installation Tree (SIT) ' \
       'in the directory specified with -p|--proxyDir, or in the ' \
       'default location "%s" (where <build> will be replaced by ' \
       'the SIT release identifier such as "latest").' % sitProxyPathHelp

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-b', '--build',
                    help='SIT release to use (default: "%s")' % sitVersion )

argman.addArgument( '-g', '--globalDir',
                    help='path to global SIT (default: %s)' % sitRootPath )

argman.addArgument( '-p', '--proxyDir',
                    help='path to proxy SIT (default: %s)' % sitProxyPathHelp )

argman.addExample( '%(prog)s' )
argman.addExample( '%(prog)s -b testing' )
argman.addExample( '%(prog)s -g /hri/sit/oldstable -p /tmp/mySIT' )

args      = vars( argman.run() )

build     = args['build']
proxyDir  = args['proxyDir']
globalDir = args['globalDir']


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


if build:
    sitRootPath  = os.path.join( SIT.getDefaultRootBaseDir(), 'builds', build )
    sitProxyPath = os.path.join( SIT.getDefaultProxyBaseDir(), build )

    try:
        assert os.path.exists( sitRootPath ), '%s: No such directory (or symlink)' % sitRootPath
    except AssertionError as details:
        raise SystemExit( details )


if proxyDir:
    sitProxyPath = proxyDir

if globalDir:
    sitRootPath  = globalDir


logging.info( 'SIT Parent: %s', sitRootPath )
logging.info( 'SIT Proxy:  %s\n', sitProxyPath )

answer = input( 'Is this correct (Y/n)? ' )

if answer == '' or answer == 'y' or answer == 'Y':
    try:
        print( '' )
        ProxyDir.createProxyDir( sitRootPath, sitProxyPath )
    except AssertionError as details:
        logging.error( details )


# EOF
