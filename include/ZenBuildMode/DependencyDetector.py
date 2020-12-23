#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Helper script for Zen Build Mode: [Reverse] dependency detection
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


import base64
import logging

import dill

from ToolBOSCore.BuildSystem        import BuildSystemTools
from ToolBOSCore.Packages           import BSTPackage
from ToolBOSCore.Packages           import ProjectProperties
from ToolBOSCore.Storage            import SIT
from ToolBOSCore.Util               import Any
from ToolBOSCore.Util               import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Part of Zen Build Mode, not intended for standalone use.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-q', '--quiet', action='store_true',
                    help='hardly show any output' )

argman.addArgument( 'topLevelDir',
                    help='top-level directory of source tree' )

argman.addArgument( 'package',
                    help='SIT package (or: "none" to disable)' )

argman.addExample( '%(prog)s . Libraries/MasterClock/1.6' )

args          = vars( argman.run() )

canonicalPath = args['package']
quiet         = args['quiet']
topLevelDir   = args['topLevelDir']


if quiet:
    Any.setDebugLevel( logging.CRITICAL )


try:
    BuildSystemTools.requireTopLevelDir( topLevelDir )
except RuntimeError as details:
    raise SystemExit( details )


try:
    ProjectProperties.requireIsCanonicalPath( canonicalPath )
except AssertionError as details:
    raise SystemExit( details )


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


logging.info( 'retrieving dependencies...' )
bstpkg_src = BSTPackage.BSTSourcePackage()
bstpkg_src.open( topLevelDir )
bstpkg_src.retrieveDependencies( True )

logging.info( 'retrieving reverse dependencies...' )
bstpkg_global = BSTPackage.BSTGloballyInstalledPackage()

try:
    bstpkg_global.open( canonicalPath )
    bstpkg_global.retrieveReverseDependencies( True )
except AssertionError as details:
    # most likely: package is not globally installed
    logging.info( details )

    bstpkg_global.revDepSet = set()


Any.requireIsSet( bstpkg_src.depSet )
Any.requireIsSet( bstpkg_global.revDepSet )

fullSet             = bstpkg_src.depSet | bstpkg_global.revDepSet
sitProxyPath        = SIT.getPath()
sitRootPath         = SIT.getRootPath()
installStatus       = {}
installStatusLocal  = {}
installStatusProxy  = {}
installStatusGlobal = {}


logging.debug( 'retrieving install status of [reverse-]dependencies...' )

for packageURL in fullSet:
    protocol, remainder = ProjectProperties.splitURL( packageURL )

    # _installStatus is the generic form, holding the installStatus
    # for Debian packages (= locally) and SIT packages (= in proxy)
    # since those are the effective locations for compiling sources

    if protocol == 'deb':
        status = ProjectProperties.isInstalled( packageURL )
        installStatus[ packageURL ]      = status
        installStatusLocal[ packageURL ] = status
        logging.debug( 'installed locally : %s = %s', packageURL, status )

    else:
        status = ProjectProperties.isInstalled( packageURL, sitProxyPath )
        installStatus[ packageURL ]      = status
        installStatusProxy[ packageURL ] = status
        logging.debug( 'installed in proxy: %s = %s', packageURL, status )

        status = ProjectProperties.isInstalled( packageURL, sitRootPath )
        installStatusGlobal[ packageURL ] = status
        logging.debug( 'installed globally: %s = %s', packageURL, status )


# also retrieve info about current package

packageURL = bstpkg_src.url

status = ProjectProperties.isInstalled( packageURL, sitProxyPath )
installStatusProxy[ packageURL ] = status
logging.debug( 'installed in proxy: %s = %s', packageURL, status )

status = ProjectProperties.isInstalled( packageURL, sitRootPath )
installStatusGlobal[ packageURL ] = status
logging.debug( 'installed globally: %s = %s', packageURL, status )


data = { 'bstpkg_src':          bstpkg_src,
         'bstpkg_global':       bstpkg_global,
         'installStatus':       installStatus,
         'installStatusLocal':  installStatusLocal,
         'installStatusProxy':  installStatusProxy,
         'installStatusGlobal': installStatusGlobal }


dillPayload   = dill.dumps( data )
Any.requireIsInstance( dillPayload, bytes )

base64payload = base64.b64encode( dillPayload )
Any.requireIsInstance( base64payload, bytes )

strPayload = str( base64payload, 'utf-8' )
Any.requireIsInstance( strPayload, str )


print( strPayload, end='' )


# EOF
