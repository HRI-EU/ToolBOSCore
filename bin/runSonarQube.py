#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  runs SonarQube scan to analyze the current package
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

from ToolBOSCore.Tools import SonarQube
from ToolBOSCore.Util  import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc   = "Launches the SonarQube scan to analyze the current package. " \
         "The SonarQube hostname is configured via ToolBOS.conf file, " \
         "the authentication token can be passed via cmd line option or env.var. " \
         "'SONAR_TOKEN' or ToolBOS.conf settings. If used in CI/CD pipelines, 'SONAR_TOKEN' " \
         "might be globally predefined by administrators."

argman = ArgsManagerV2.ArgsManager( desc )

argman.add_argument( '-t','--token', type=str,
                     help='user auth token (alternatively via env.var.SONAR_TOKEN or ' \
                          'via ToolBOS.conf settings)' )

argman.add_argument( '-b','--build', type=str,
                     help='command to build this package' )

argman.addExample( '%(prog)s -t <auth-token>' )
argman.addExample( '%(prog)s -t <auth-token> -b BST.py' )
argman.addExample( '%(prog)s -t <auth-token> -b ./build.sh' )
argman.addExample( '%(prog)s -b BST.py' )
argman.addExample( '%(prog)s' )

args         = vars( argman.run() )
buildCommand = args[ 'build' ]
token        = args[ 'token' ]


try:
    _token = SonarQube.readToken( token )

    if buildCommand:
        SonarQube.runBuildWrapper( buildCommand )

    # use the user provided auth token
    SonarQube.runScan( _token )
    sys.exit( 0 )

except ( AssertionError, KeyError ):
    logging.error( 'Failed to run SonarQube analysis' )
    sys.exit( -1 )


# EOF
