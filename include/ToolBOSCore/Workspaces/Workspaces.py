# -*- coding: utf-8 -*-
#
#  ToolBOS workspace setup
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

from ToolBOSCore.Packages import PackageDetector, ProjectProperties
from ToolBOSCore.Storage import SIT
from ToolBOSCore.Storage import VersionControl
from ToolBOSCore.Tools import Git, SVN
from ToolBOSCore.Util  import Any

class ToolBOSWorkspace( object ):

    def __init__( self ):
        super( ToolBOSWorkspace, self ).__init__()

        self._packageList = []
        self._repo        = Git.LocalGitRepository()


    def addPackages( self, packageList ):
        Any.requireIsIterable( packageList )

        self._packageList.extend( packageList )


    def setup( self, packageList=None ):
        if packageList is not None:
            Any.requireIsList( packageList )

        cwd = os.getcwd()
        logging.info( 'setting up ToolBOS workspace in: %s', cwd )

        if Any.isIterable( packageList ):
            self.addPackages( packageList )


def printBuildCommands( orderedList ):
    """
        Prints the build-instruction for each package in the list, e.g.:

            build src/ToolBOSCore
            build src/ToolBOSLib
            build src/IniConfigFile
            build src/Middleware

        Note: The list shall already be sorted according to build order!
    """
    Any.requireIsListNonEmpty( orderedList )

    sitRootPath = SIT.getRootPath()
    commands    = []

    for canonicalPath in orderedList:
        ProjectProperties.requireIsCanonicalPath( canonicalPath )

        installRoot = os.path.join( sitRootPath, canonicalPath )
        Any.requireIsExisting( installRoot )

        detector    = PackageDetector.PackageDetector( installRoot )
        detector.retrieveMetaInfoFromSIT()

        vcsRelPath  = detector.vcsRelPath
        vcsRoot     = detector.vcsRoot


        if vcsRoot:
            Any.requireIsTextNonEmpty( vcsRoot )
            repo     = VersionControl.auto( vcsRoot )
            repoName = repo.getRepositoryName()

            if vcsRelPath:
                location = os.path.join( 'src', repoName, vcsRelPath )
            else:
                location = os.path.join( 'src', repoName )

            command  = 'build %s' % location

        else:
            command  = '# build %s# location unknown' % canonicalPath.ljust(70)

        commands.append( command )

    for command in commands:
        print( command )


def printFetchCommands( packageList, asSubModule=True ):
    """
        Prints the VCS fetch command for each package in the list.
        Duplicates will be removed, and output will be sorted for better
        readability, e.g.:

        asSubModule = True:
            git submodule add git@dmz-gitlab.honda-ri.de:TECH_Team/BPL.git
            git submodule add git@dmz-gitlab.honda-ri.de:ToolBOS/BasicComponents.git
            git submodule add git@dmz-gitlab.honda-ri.de:ToolBOS/ToolBOSLib.git

        asSubModule = False:
            git clone git@dmz-gitlab.honda-ri.de:TECH_Team/BPL.git
            git clone git@dmz-gitlab.honda-ri.de:ToolBOS/BasicComponents.git
            git clone git@dmz-gitlab.honda-ri.de:ToolBOS/ToolBOSLib.git
    """
    Any.requireIsIterable( packageList )
    Any.requireIsBool( asSubModule )

    sitRootPath = SIT.getRootPath()
    commands    = set()                     # avoids duplicates

    for canonicalPath in packageList:
        ProjectProperties.requireIsCanonicalPath( canonicalPath )

        installRoot = os.path.join( sitRootPath, canonicalPath )
        Any.requireIsExisting( installRoot )

        detector    = PackageDetector.PackageDetector( installRoot )
        detector.retrieveMetaInfoFromSIT()

        vcsRoot     = detector.vcsRoot


        if vcsRoot:
            Any.requireIsTextNonEmpty( vcsRoot )
            repo = VersionControl.auto( vcsRoot )

            if isinstance( repo, SVN.SVNRepository ):
                repo.setConfiguredUserName()
                command = repo.getSourceCodeCommand()

            elif isinstance( repo, Git.RemoteGitRepository ):
                command = repo.getSourceCodeCommand( asSubModule )

            else:
                raise TypeError( 'unexpected datatype: %s', type(repo) )

        else:
            command = '# VCS location unknown: %s' % canonicalPath

        commands.add( command )


    for command in sorted( commands ):
        print( command )


# EOF
