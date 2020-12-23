#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Creates a minimalistic SIT (bootstrap procedure)
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

from ToolBOSCore.Storage import CopyTreeFilter, SIT
from ToolBOSCore.Util    import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parameters
#----------------------------------------------------------------------------


desc = 'Creates a minimalistic SIT which will only contain the ' \
       'ToolBOS SDK and some essential packages.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-b', '--buildSDK', action='store_true',
                    help='include essential build environment' )

argman.addArgument( '-d', '--documentation', action='store_true',
                    help='filter-out / exclude documentation' )

argman.addArgument( '-p', '--platforms', default=None,
                    help='copy only binaries of specified platforms (comma-separated)' )

argman.addArgument( '-r', '--resolveLTS', action='store_true',
                    help='copy content of LTS packages' )

argman.addArgument( 'path', help='directory where to create the new SIT' )

argman.addExample( '%(prog)s -bd /tmp/newSIT' )
argman.addExample( '%(prog)s --platforms=bionic64,focal64 /tmp/newSIT' )

argman.setAllowUnknownArgs( True )

args       = vars( argman.run() )
unhandled  = argman.getUnhandledArguments()

buildSDK   = args['buildSDK']
filterDocu = args['documentation']
path       = args['path']
platforms  = args['platforms']
resolveLTS = args['resolveLTS']


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


if os.path.exists( path ):
    logging.error( '%s: directory exists', path )
    raise SystemExit()


# setup filtering

if platforms:
    try:
        platformList = platforms.split( ',' )
    except AssertionError as details:
        logging.error( details )
        raise SystemExit()

else:
    platformList = []


copyFilter = CopyTreeFilter.CopyTreeFilter( platformList )
copyFilter.filterDocu = filterDocu


# create new SIT

logging.info( 'bootstrapping SIT in %s', path )
SIT.bootstrap( path, buildSDK, True, copyFilter.callback, resolveLTS )


# EOF
