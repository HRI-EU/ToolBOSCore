# -*- coding: utf-8 -*-
#
#  Cache and retrieve information about packages installed in the SIT
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


import os

from ToolBOSCore.Packages                 import ProjectProperties
from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.Storage                  import SIT
from ToolBOSCore.Util                     import Any


class MetaInfoCache( object ):

    def __init__( self ):
        self._cache = {}


    def populate( self ):
        """
            Scans all package in SIT and stores the ground-truth pkgInfo.py
            information into one giant hashtable for later fast access.

            The assignment is "packageURL": { pkgInfo data }
        """
        sitPath        = SIT.getPath()
        canonicalPaths = SIT.getCanonicalPaths( sitPath )
        Any.requireIsListNonEmpty( canonicalPaths )


        for canonicalPath in canonicalPaths:
            ProjectProperties.requireIsCanonicalPath( canonicalPath )

            packageURL  = 'sit://' + canonicalPath
            installRoot = os.path.join( sitPath, canonicalPath )
            detector    = PackageDetector( installRoot )
            detector.retrieveMakefileInfo()

            self._cache[ packageURL ] = detector


    def getDetector( self, packageURL ):
        ProjectProperties.requireIsURL( packageURL )

        return self._cache[ packageURL ]


    def getReverseDependencies( self, packageURL ):
        ProjectProperties.requireIsURL( packageURL )

        result = set()

        for candidateURL, detector in self._cache.items():
            ProjectProperties.requireIsURL( candidateURL )

            if packageURL in detector.dependencies:
                result.add( candidateURL )

        return result


    def setCache( self, cache ):
        Any.requireIsDict( cache )

        self._cache = cache


# EOF
