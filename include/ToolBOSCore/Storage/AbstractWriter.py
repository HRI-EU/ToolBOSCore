# -*- coding: utf-8 -*-
#
#  GnuPG facade
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

from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.Util                     import Any
from ToolBOSCore.Util                     import FastScript


class AbstractWriter( object ):
    """
        Superclass where all shellfile writers derive from.
        See the Template Method design pattern for details.
    """

    def __init__( self, details ):
        """
            This constructor uses an existing PackageDetector instance
            to avoid multiple detection of package meta-information
            (for each derived subclass BashSrcWriter etc.)
        """
        Any.require( isinstance( details, PackageDetector ) )

        self.content = ''
        self.details = details


    def _deploy( self ):
        leadIn             = self.addLeadIn()
        basicInfo          = self.addBasicInfo()
        originalName       = self.addOriginalName()
        maintainer         = self.addMaintainer()
        repositoryInfo     = self.addRepositoryInfo()
        dependencies       = self.addDependencies()
        buildDependencies  = self.addBuildDependencies()
        recommendations    = self.addRecommendations()
        suggestions        = self.addSuggestions()
        buildSystemInfo    = self.addBuildSystemInfo()
        mainLoop           = self.addMainLoop()
        componentInterface = self.addComponentInterface()
        leadOut            = self.addLeadOut()

        Any.requireIsText( leadIn )
        Any.requireIsText( basicInfo )
        Any.requireIsText( originalName )
        Any.requireIsText( maintainer )
        Any.requireIsText( repositoryInfo )
        Any.requireIsText( dependencies )
        Any.requireIsText( buildDependencies )
        Any.requireIsText( recommendations )
        Any.requireIsText( suggestions )
        Any.requireIsText( buildSystemInfo )
        Any.requireIsText( mainLoop )
        Any.requireIsText( componentInterface )
        Any.requireIsText( leadOut )

        self.content       = leadIn + basicInfo + originalName + \
                             maintainer + repositoryInfo + dependencies + \
                             buildDependencies + recommendations + \
                             suggestions + buildSystemInfo + mainLoop + \
                             componentInterface + leadOut


    def _replace( self, string, substMap ):
        result = string

        for ( key, value ) in substMap.items():
            result = result.replace( key, value )

        return result


    def write( self, outputFile ):
        self._deploy()
        logging.info( 'generating %s', os.path.relpath( outputFile, os.getcwd() ) )
        FastScript.setFileContent( outputFile, self.content )


    def __str__( self ):
        return self.content


    def addLeadIn( self ):
        return ''

    def addBasicInfo( self ):
        return ''

    def addOriginalName( self ):
        return ''

    def addMaintainer( self ):
        return ''

    def addRepositoryInfo( self ):
        return ''

    def addDependencies( self ):
        return ''

    def addBuildDependencies( self ):
        return ''

    def addRecommendations( self ):
        return ''

    def addSuggestions( self ):
        return ''

    def addBuildSystemInfo( self ):
        return ''

    def addComponentInterface( self ):
        return ''

    def addMainLoop( self ):
        return ''

    def addLeadOut( self ):
        return ''


# EOF
