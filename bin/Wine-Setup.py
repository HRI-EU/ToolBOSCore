#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Configures the user's shell environment to use Wine
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


import io
import logging
import os

from ToolBOSCore.Settings import UserSetup
from ToolBOSCore.Util     import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


defaultPath = os.path.expandvars( '${HOME}/.wine' )


desc = "Initial configuration of Wine, e.g. for cross-compilation with BST.py."

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-p', '--path', default=defaultPath,
                    help='config directory (default: $HOME/.wine)' )

argman.addExample( '%(prog)s' )

args = vars( argman.run() )
path = args['path']


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


# suppress all Wine warnings that would confuse normal users
output = io.StringIO()

try:
    UserSetup.setupWineDotNet( path, stdout=output, stderr=output )
    logging.info( 'OK, Wine is ready.' )

except OSError as details:
    logging.error( details.strerror )
    logging.error( 'Wine setup failed!' )


# EOF
