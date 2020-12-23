#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  searches for projects locally installed in the SIT proxy, or pointing
#  to somewhere else than the root SIT (e.g. group proxy)
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
import sys

from ToolBOSCore.Storage import ProxyDir
from ToolBOSCore.Storage import SIT
from ToolBOSCore.Util    import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Lists all packages installed only in your SIT sandbox ("proxy directory").'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addExample( '%prog' )

args = vars( argman.run() )

verbose = args['verbose']


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


try:
    packageList = ProxyDir.findProxyInstallations( checkLinks=True )

except AssertionError as details:
    logging.error( details )
    sys.exit( -1 )


# suppress the specific package "Modules/Index/*" which contains
# registered components for DTBOS/RTMaps (see JIRA ticket TBCORE-910)
sitPath   = SIT.getPath()
indexPath = os.path.join( sitPath, 'Modules/Index' )

for project in packageList:

    if not project.startswith( indexPath ) or verbose:
        print( project )


# EOF
