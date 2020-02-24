# -*- coding: utf-8 -*-
#
#  Model for packages that are compatible with 'BST.py'
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


import copy
import logging
import os

from ToolBOSCore.Packages                 import ProjectProperties
from ToolBOSCore.Packages.AbstractPackage import AbstractPackage
from ToolBOSCore.Packages.DebianPackage   import DebianPackage
from ToolBOSCore.Packages.MetaInfoCache   import MetaInfoCache
from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.Platforms.Platforms      import getHostPlatform
from ToolBOSCore.Storage                  import SIT
from ToolBOSCore.Storage.PkgInfoInterface import PkgInfoInterface
from ToolBOSCore.Util                     import Any


class BSTPackage( AbstractPackage ):
    """
        A software package in ToolBOS SDK scope, f.i. which can be
        installed into SIT and/or processed with "BST.py".
    """
    def __init__( self, url=None ):
        super( BSTPackage, self ).__init__( url )

        self.detector = None


    def getDepInstallCmd_APT( self ):
        """
            Returns the Debian/Ubuntu command-line to install all the
            dependencies found by retrieveDependencies().
        """
        from ToolBOSCore.Platforms import Debian

        Any.requireIsSet( self.depSet, 'Please call .retrieveDependencies() first' )

        if self.depSet:
            deps = list( self.depSet )
            deps.sort()
            return Debian.getDepInstallCmd( deps )
        else:
            return None


    def open( self, topLevelDir ):
        self.detector = PackageDetector( topLevelDir )
        self.detector.retrieveMakefileInfo()
        self.url      = 'sit://' + self.detector.canonicalPath


    def retrieveDependencies( self, recursive,
                              normalDeps=True, buildDeps=False,
                              recommendations=False, suggestions=False ):
        Any.requireIsNotNone( self.detector, 'Please call .open() first' )
        Any.requireIsBool( recursive )
        Any.requireIsBool( normalDeps )
        Any.requireIsBool( buildDeps )
        Any.requireIsBool( recommendations )
        Any.requireIsBool( suggestions )

        self.detector.retrieveMakefileInfo()

        self.depSet  = set()
        self.depTree = list()
        debPrefix    = 'deb://'
        sitPrefix    = 'sit://'
        hostPlatform = getHostPlatform()


        if normalDeps:
            self.depSet = set( self.detector.dependencies )

            try:
                self.depSet.update( self.detector.dependsArch[ hostPlatform ] )
            except KeyError:
                pass                             # no such setting, this is OK


        if buildDeps:
            self.depSet.update( self.detector.buildDependencies )

            try:
                self.depSet.update( self.detector.buildDependsArch[ hostPlatform ] )
            except KeyError:
                pass                             # no such setting, this is OK


        # create a temporary copy of self.depSet while iterating,
        # otherwise leads to "RuntimeError: Set changed size during iteration"
        for packageURL in copy.copy( self.depSet ):
            ProjectProperties.requireIsURL( packageURL )

            error = False

            if packageURL.startswith( sitPrefix ):
                depPkg = BSTProxyInstalledPackage( packageURL )
                try:
                    depPkg.open()

                    if recursive:
                        depPkg.retrieveDependencies( recursive, normalDeps, buildDeps,
                                                     recommendations, suggestions )
                    else:
                        depPkg.depSet  = set()
                        depPkg.depTree = list()
                except AssertionError as details:
                    logging.debug( details )
                    depPkg.depSet  = set()
                    depPkg.depTree = list()
                    error          = True

            elif packageURL.startswith( debPrefix ):
                depPkg = DebianPackage( packageURL )

                try:
                    depPkg.retrieveDependencies()
                except EnvironmentError as details:
                    logging.warning( details )
                    depPkg.depSet  = set()
                    depPkg.depTree = list()

            else:
                raise ValueError( 'Unknown URL prefix in "%s"' % packageURL )

            if not error:
                self.depSet.update( depPkg.depSet )

            self.depSet.add( packageURL )
            self.depTree.append( depPkg )



class BSTSourcePackage( BSTPackage ):
    """
        Represents a software package in source-tree form, i.e.
        a Git / SVN working copy where the developer may run the
        compilation process.
    """
    def __init__( self, url=None ):
        super( BSTSourcePackage, self ).__init__( url )

        self.creator     = None
        self.documenter  = None
        self.installer   = None
        self.sqChecker   = None


    def open( self, topLevelDir ):
        super( BSTSourcePackage, self ).open( topLevelDir )

        self.detector.retrieveVCSInfo()


    def prepareQualityCheck( self, enabled=None ):
        from ToolBOSCore.SoftwareQuality import CheckRoutine

        self.sqChecker = CheckRoutine.CheckRoutine( self.detector.topLevelDir,
                                                    self.detector )


    def setSQLevel( self, level ):
        from ToolBOSCore.SoftwareQuality import CheckRoutine

        Any.requireIsTextNonEmpty( level )

        if level == CheckRoutine.sqLevelDefault:
            self.pkgInfo_remove( 'sqLevel' )     # no need to store
        else:
            self.pkgInfo_set( 'sqLevel', level )


    def pkgInfo_remove( self, key ):
        Any.requireIsTextNonEmpty( key )

        try:
            pkgInfo = PkgInfoInterface( self.detector )
            pkgInfo.remove( key )
            pkgInfo.write()

            del pkgInfo

        except SyntaxError:
            logging.error( 'SyntaxError in pkgInfo.py' )
            logging.error( 'unable to remove setting "%s"', key )


    def pkgInfo_set( self, key, value ):
        Any.requireIsTextNonEmpty( key )

        try:
            pkgInfo = PkgInfoInterface( self.detector )
            pkgInfo.set( key, value )
            pkgInfo.write()

            del pkgInfo

        except SyntaxError:
            logging.error( 'SyntaxError in pkgInfo.py' )
            logging.error( 'unable to save setting "%s"', key )


class BSTInstalledPackage( BSTPackage ):
    """
        Represents a software package which is installed in the
        Software Installation Tree (SIT).
    """
    _sitPath       = SIT.getPath()
    _metaInfoCache = None


    def __init__( self, url=None ):
        super( BSTInstalledPackage, self ).__init__( url )

        self.revDepSet  = None
        self.revDepTree = None


    def open( self, topLevelDir ):
        super( BSTInstalledPackage, self ).open( topLevelDir )


    def isInstalled( self ):
        # if package could not be opened then self.detector is None,
        # hence accessing self.detector.topLevelDir won't work
        if self.detector is None:
            return False

        Any.requireIsTextNonEmpty( self.detector.topLevelDir )
        Any.requireIsTextNonEmpty( self._sitPath )

        return os.path.exists( os.path.join( self._sitPath,
                                             self.detector.topLevelDir ) )


    def retrieveReverseDependencies( self, recursive ):
        self._ensureMetaInfoCache()

        self.revDepSet  = set()
        self.revDepTree = list()

        for depURL in self._metaInfoCache.getReverseDependencies( self.url ):
            ProjectProperties.requireIsURL( depURL )

            # no Debian packages can appear in reverse dependencies of SIT packages
            depPackage = BSTInstalledPackage( depURL )
            depPackage.detector = self._metaInfoCache.getDetector( depURL )

            if recursive:
                depPackage.retrieveReverseDependencies( recursive )
                self.revDepSet.update( depPackage.revDepSet )

            self.revDepSet.add( depURL )
            self.revDepTree.append( depPackage )


    def _ensureMetaInfoCache( self ):
        """
            Creates and populates the internal MetaInfoCache,
            if not already existing.
        """
        if not BSTInstalledPackage._metaInfoCache:
            BSTInstalledPackage._metaInfoCache = MetaInfoCache()
            BSTInstalledPackage._metaInfoCache.populate()


    def setMetaInfoCache( self, metaInfoCache ):
        Any.requireIsInstance( metaInfoCache, MetaInfoCache )

        BSTInstalledPackage._metaInfoCache = metaInfoCache


class BSTProxyInstalledPackage( BSTInstalledPackage ):
    """
        Represents a software package which is installed in the
        Proxy-SIT of the developer.
    """
    _sitPath = SIT.getPath()


    def open( self, package=None ):
        if self.url:
            ProjectProperties.requireIsURL( self.url )
            package = ProjectProperties.splitURL( self.url )[1]
        else:
            ProjectProperties.requireIsCanonicalPath( package )

        topLevelDir = os.path.join( SIT.getPath(), package )

        super( BSTProxyInstalledPackage, self ).open( topLevelDir )


class BSTGloballyInstalledPackage( BSTInstalledPackage ):
    """
        Represents a software package which is installed in the
        Global SIT of the site running ToolBOS SDK.
    """
    _sitPath = SIT.getRootPath()


    def open( self, package=None ):
        if self.url:
            ProjectProperties.requireIsURL( self.url )
            package = ProjectProperties.splitURL( self.url )[1]
        else:
            ProjectProperties.requireIsCanonicalPath( package )

        topLevelDir = os.path.join( SIT.getRootPath(), package )

        super( BSTGloballyInstalledPackage, self ).open( topLevelDir )


# EOF
