#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Configures the user's shell environment to use MSVC (with Wine)
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

from ToolBOSCore.Settings.UserSetup import setupMSVC
from ToolBOSCore.Util               import ArgsManagerV2
from ToolBOSCore.Settings           import ToolBOSConf


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = "Configures the user's shell environment to use MSVC (with Wine)."

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-p', '--path',
                    help='Wine config directory (default: $HOME/.wine)' )

argman.addArgument( '-m', '--msvc-version', type=int,
                    help='SDK version to setup (default: 2017)' )

argman.addExample( '%(prog)s' )

args    = vars( argman.run() )
path    = args['path']
version = args['msvc_version']

if not path:
    path = os.path.expandvars( '${HOME}/.wine' )

if not version:
    version = ToolBOSConf.getConfigOption( 'msvcVersion' )


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


logging.info( 'Wine config directory: %s', path )

if version not in ( 2008, 2010, 2012, 2017 ):
    logging.error( 'Unsupported MSVC version %s', version )

try:
    setupMSVC( path, version )
    logging.info( 'OK, MSVC compiler is ready.' )

except ( EnvironmentError, OSError, ValueError ) as details:
    logging.error( details )
    logging.error( 'MSVC setup failed!' )


# EOF
