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

from ToolBOSCore.Tools import SonarQube
from ToolBOSCore.Util  import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc   = "Launches the SonarQube scan to analyze the current package. " \
         "This script can be used locally or in CI pipeline. " \
         "Pass the parameter `token` only when using locally. " \
         "When using this in the CI pipeline `token` is " \
         "already set by Gitlab admins. Pass the parameter " \
         "`build` for projects that needs to be compiled beforehand."

argman = ArgsManagerV2.ArgsManager( desc )

argman.add_argument( '-t','--token', type=str,
                     help='user token generated via SonarQube GUI' )

argman.add_argument( '-b','--build', type=str,
                     help='command to build this package' )

argman.addExample( '%(prog)s -t 123456789' )
argman.addExample( '%(prog)s -t 123456789 -b BST.py' )
argman.addExample( '%(prog)s -t 123456789 -b ./build.sh' )
argman.addExample( '%(prog)s -b BST.py' )
argman.addExample( '%(prog)s' )

args         = vars( argman.run() )
buildCommand = args[ 'build' ]
token        = args[ 'token' ]


try:
    if buildCommand:
        SonarQube.runBuildWrapper( buildCommand )

    SonarQube.runScan( token )

except AssertionError as e:
    logging.error( "an error occurred in the system" )


# EOF
