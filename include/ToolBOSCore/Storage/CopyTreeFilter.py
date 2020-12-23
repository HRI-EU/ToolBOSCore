#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Callback for shutil.copytree() to filter-out undesired content when copying
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


import logging
import os
import os.path

from ToolBOSCore.Platforms.Platforms import getPlatformNames
from ToolBOSCore.Util                import Any


class CopyTreeFilter( object ):

    blacklist  = None

    # True = filter-out, False = do export
    filterDocu = None
    filterSDK  = None


    def __init__( self, platformWhitelist ):


        Any.requireIsList( platformWhitelist )

        self.filterDocu = False
        allPlatforms    = getPlatformNames()
        self.blacklist  = frozenset( frozenset(allPlatforms) -
                                     frozenset(platformWhitelist) )


    def callback( self, path, fileList ):
        """
            Callback function for shutil.copytree() for filtering out
            undesired files and directories.
        """
        excludeList = []

        for item in fileList:

            if item in self.blacklist:

                excludeList.append( item )
                logging.debug( 'filtered-out: %s', os.path.join( path, item ) )

            elif self.filterDocu:
                if item == 'doc' or path.endswith( '/doc' ):
                    excludeList.append( item )
                    logging.debug( 'filtered-out: %s', os.path.join( path, item ) )


        return excludeList


# EOF

