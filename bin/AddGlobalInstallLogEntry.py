#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  shell frontend for the GlobalInstallLog class
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

from ToolBOSCore.Util                         import ArgsManagerV2
from ToolBOSCore.BuildSystem.GlobalInstallLog import GlobalInstallLog


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'This script creates a new global install log entry.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-d', '--dry-run', action='store_true',
                    help='do not write the log entry, just show ' + \
                         'the information (for debugging)' )

argman.addArgument( '-n', '--new', action='store_true',
                    help='flag package as "new" (first installation)' )

argman.addArgument( '-t', '--type', type=str, default='NEW', metavar='TYPE',
                    help='log entry type ("NEW" [=default], "FIX" or "DOC")' )

argman.addArgument( 'installRoot', type=str,
                    help='install path (e.g. ${SIT}' + \
                         '/Libraries/Foo/1.0)' )

argman.addArgument( 'message', help='the log message' )

argman.addExample( '%(prog)s -d -t FIX "${SIT}/Libraries/Foo/1.0" "Message text"' )

args = vars( argman.run() )


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


try:
    logEntry = GlobalInstallLog( args['installRoot'],
                                 args['new'],
                                 args['type'],
                                 args['message'] )

    logEntry.writeFile( args['dry_run'] )

    if not args['dry_run']:
        logging.info( 'OK, file written' )

except OSError as details:
    logging.error( details )


# EOF
