#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Launches the Klocwork Desktop GUI to analyze the current package
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
import tempfile

from ToolBOSCore.Tools import Klocwork
from ToolBOSCore.Util  import Any, ArgsManagerV2, FastScript


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Launches the Klocwork Desktop GUI to analyze the current package.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-d', '--dataDir', action='store', type=str,
                    metavar='PATH',
                    help='Klocwork data dir. (default: /tmp)' )

argman.addExample( '%(prog)s' )
argman.addExample( '%(prog)s -d ./klocworkData' )

args    = vars( argman.run() )
dataDir = args['dataDir']


if dataDir:
    deleteDir     = False
    klocworkDir   = dataDir
    Any.requireIsTextNonEmpty( klocworkDir )
    Any.requireMsg( klocworkDir not in ( '.', '..' ), "invalid path names!" )

else:
    deleteDir     = True
    klocworkDir   = tempfile.mkdtemp( prefix='klocwork-' )


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


logging.info( 'Klocwork data directory: %s', klocworkDir )

try:
    Klocwork.createLocalProject( klocworkDir )
    Klocwork.startGUI( klocworkDir, blocking=True )
    status = 0

except AssertionError as details:
    logging.error( details )
    status = -1

except KeyboardInterrupt:
    # user pressed <Ctrl+C>
    status = -1


if deleteDir:
    FastScript.remove( klocworkDir )

sys.exit( status )


# EOF
