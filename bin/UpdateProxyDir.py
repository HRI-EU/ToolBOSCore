#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  updates and repairs the user's SIT sandbox ("proxy directory")
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
import sys

from ToolBOSCore.Settings import UserSetup
from ToolBOSCore.Storage  import ProxyDir
from ToolBOSCore.Util     import Any
from ToolBOSCore.Util     import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Update your Software Installation Tree (SIT) sandbox and ' + \
       'ToolBOS settings (if necessary).'

argman = ArgsManagerV2.ArgsManager( desc )


argman.addArgument( '-b', '--keep-broken', action='store_false', default=True,
                    help='do not remove broken symlinks' )

argman.addArgument( '-c', '--no-check', action='store_false', default=True,
                    help='ignore symlinks not pointing into global SIT' )

argman.addArgument( '-d', '--dry-run', action='store_true',
                    help='do not actually do anything' )

argman.addArgument( '-e', '--keep-empty', action='store_false', default=True,
                    help='ignore empty categories and leftovers from packages' )

argman.addArgument( '-f', '--find', action='store_true',
                    help='find proxy installations' )

argman.addArgument( '-i', '--keep-index', action='store_false', default=True,
                    help='do not touch RTMaps *.pck index' )

argman.addArgument( '-n', '--no-new', action='store_false', default=True,
                    help='do not add links to new packages' )

argman.addArgument( '-r', '--remove', action='store_true',
                    help='remove proxy-installations + link into global SIT' )

argman.addArgument( '-s', '--skip', action='store_false', default=True,
                    help='skip clean-up of unused files in ~/.HRI' )

argman.addArgument( '-u', '--no-upgrade', action='store_false', default=True,
                    help='do not upgrade patchlevel-version symlinks' )

argman.addExample( '%(prog)s' )
argman.addExample( '%(prog)s --no-check --verbose' )
argman.addExample( '%(prog)s -r                          # ATTENTION!' )

args                     = vars( argman.run() )

checkProxyLinkTarget     = args['no_check']
checkProxyLinkedVersion  = args['no_upgrade']
cleanHomeDirectory       = args['skip']
dryRun                   = args['dry_run']
find                     = args['find']
linkNewPackagesIntoProxy = args['no_new']
removeBrokenSymlinks     = args['keep_broken']
removeEmptyCategories    = args['keep_empty']
removeProxyInstallations = args['remove']
updateRTMapsIndex        = args['keep_index']


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


if find:

    try:
        for project in ProxyDir.findProxyInstallations( checkLinks=True ):
            print( project )
        sys.exit( 0 )

    except AssertionError as details:
        logging.error( details )
        sys.exit( -1 )

else:

    try:
        UserSetup.silentUpgrade()
        ProxyDir.updateProxyDir( removeBrokenSymlinks,
                                 removeEmptyCategories,
                                 linkNewPackagesIntoProxy,
                                 checkProxyLinkTarget,
                                 checkProxyLinkedVersion,
                                 removeProxyInstallations,
                                 cleanHomeDirectory,
                                 updateRTMapsIndex,
                                 dryRun )

    except ( AssertionError, OSError, ValueError ) as details:
        # show stacktrace in verbose mode
        if Any.getDebugLevel() >= 5:
            raise
        else:
            logging.error( details )

    except KeyboardInterrupt:
        # user pressed <Ctrl+C>
        sys.exit( -1 )


# EOF
