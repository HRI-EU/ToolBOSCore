# -*- coding: utf-8 -*-
#
#  Functions to create a new package
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
import subprocess

from ToolBOSCore.Packages        import ProjectProperties
from ToolBOSCore.Platforms       import Platforms
from ToolBOSCore.Storage         import CMakeLists
from ToolBOSCore.Storage.PkgInfo import getPkgInfoContent
from ToolBOSCore.Util            import FastScript


class PackageDetector( object ) :
    """
        Retrieves advanced properties of a package, such as used programming
        languages etc.

        To avoid repetitive reads of the pkgInfo.py file, you may cache
        its values in a dict and provide it as parameter. This may improve
        performance by avoiding redundant file I/O.
    """

    def __init__( self, projectRoot=None, pkgInfoContent=None ):
        if not projectRoot:
            projectRoot = ProjectProperties.detectTopLevelDir()

        if not projectRoot:
            raise AssertionError( 'unknown project root location' )

        FastScript.requireIsDir( projectRoot )

        if pkgInfoContent is not None:
            FastScript.requireIsDict( pkgInfoContent )


        # general meta-info
        self.canonicalPath     = None
        self.cmakelistsContent = None
        self.hasCMakeLists     = None
        self.installRoot       = None
        self.isDeprecated      = None
        self.packageCategory   = None
        self.packageName       = None
        self.packageVersion    = None   # e.g. "2.0"
        self.packageVersionRaw = None   # e.g. "2.0-rc3" (corresponds to dir.name)
        self.patchlevel        = None   # e.g. 42
        self.topLevelDir       = None
        self.versionTokens     = None   # e.g. ( "2", "0", "123" )

        # dependencies
        self.buildDependencies = []     # direct build-deps
        self.buildDependsArch  = {}
        self.dependencies      = []     # direct deps
        self.dependsArch       = {}
        self.inheritedProjects = []     # deps. + recommend. (used in BashSrc)
        self.recommendations   = []
        self.suggestions       = []

        # general pkgInfo.py settings
        self.pkgInfoContent    = pkgInfoContent
        self.copyright         = None
        self.docFiles          = None
        self.docTool           = None
        self.install           = []
        self.installExclude    = []
        self.installHooks      = {}
        self.installMatching   = []
        self.installSymlinks   = []
        self.installGroup      = None
        self.installUmask      = None
        self.installMode       = 'incremental'
        self.usePatchlevels    = False
        self.userSrcContent    = None
        self.userSrcEnv        = ()
        self.userSrcAlias      = ()
        self.userSrcBashCode   = ()
        self.userSrcCmdCode    = ()

        # revision control system
        self.gitBranch         = None
        self.gitFound          = None
        self.gitCommitIdLong   = None
        self.gitCommitIdShort  = None
        self.gitOrigin         = None
        self.gitRelPath        = None
        self.gitRepositoryRoot = None
        self.vcsBranch         = None
        self.vcsFound          = None
        self.vcsURL            = None
        self.vcsRelPath        = None
        self.vcsRevision       = None
        self.vcsRoot           = None

        # current user (likely the maintainer when working on source tree)
        self.userAccount       = None
        self.userName          = None

        # maintainer (filesystem owner when accessing SIT packages)
        self.maintainerAccount = None
        self.maintainerName    = None


        cmakePath              = os.path.join( projectRoot, 'CMakeLists.txt' )
        self.hasCMakeLists     = os.path.exists( cmakePath )
        self.buildCommand      = None

        self.topLevelDir       = projectRoot
        self.packageName       = ProjectProperties.getPackageName( self.topLevelDir )
        self.packageVersion    = ProjectProperties.getPackageVersion( self.topLevelDir, False )
        self.packageVersionRaw = ProjectProperties.getPackageVersion( self.topLevelDir, True )
        self.versionTokens     = ProjectProperties.splitVersion( self.packageVersionRaw )

        FastScript.requireIsTextNonEmpty( self.packageName )
        FastScript.requireIsTextNonEmpty( self.packageVersion )


        # compute typical directory names (may not be present!)
        hostPlatform           = Platforms.getHostPlatform()
        FastScript.requireIsTextNonEmpty( hostPlatform )

        self.binDir            = os.path.join( self.topLevelDir, 'bin' )
        self.binDirArch        = os.path.join( self.topLevelDir, 'bin', hostPlatform )
        self.buildDir          = os.path.join( self.topLevelDir, 'build' )
        self.buildDirArch      = os.path.join( self.topLevelDir, 'build', hostPlatform )
        self.examplesDir       = os.path.join( self.topLevelDir, 'examples' )
        self.examplesDirArch   = os.path.join( self.topLevelDir, 'examples', hostPlatform )
        self.includeDir        = os.path.join( self.topLevelDir, 'include' )
        self.installDir        = os.path.join( self.topLevelDir, 'install' )
        self.libDir            = os.path.join( self.topLevelDir, 'lib' )
        self.libDirArch        = os.path.join( self.topLevelDir, 'lib', hostPlatform )
        self.srcDir            = os.path.join( self.topLevelDir, 'src' )
        self.testDir           = os.path.join( self.topLevelDir, 'test' )
        self.testDirArch       = os.path.join( self.topLevelDir, 'test', hostPlatform )

        self.scripts           = {}

        if self.hasCMakeLists:
            # source tree, C/C++ package
            self.cmakelistsContent = FastScript.getFileContent( cmakePath )

            if self.cmakelistsContent:
                self.packageCategory = CMakeLists.getCategory( self.cmakelistsContent )
            else:
                logging.debug( 'skipping empty %s', cmakePath )

        else:
            # source tree w/o CMakeLists.txt, or package installed in SIT
            self.cmakelistsContent = None

            try:
                self.packageCategory = ProjectProperties.getPackageCategoryFromPath( projectRoot )
            except AssertionError:
                raise AssertionError( 'unable to detect package category' )

        if self.packageCategory:
            self.canonicalPath      = os.path.join( self.packageCategory,
                                                    self.packageName,
                                                    self.packageVersion )

        self._retrieveCurrentUser()

        # FastScript.requireIsTextNonEmpty( self.maintainerAccount ) # might be empty
        # FastScript.requireIsTextNonEmpty( self.maintainerName )    # might be empty
        FastScript.requireIsTextNonEmpty( self.packageName )
        FastScript.requireIsTextNonEmpty( self.packageVersion )
        FastScript.requireIsTextNonEmpty( self.packageVersionRaw )
        FastScript.requireIsTextNonEmpty( self.topLevelDir )
        FastScript.requireIsTextNonEmpty( self.userAccount )
        FastScript.requireIsTextNonEmpty( self.userName )


    #------------------------------------------------------------------------
    # SIT Category
    #------------------------------------------------------------------------


    def isExternal( self ):
        """
            Returns 'True' if the package is an open source or commercial
            external software which has not been developed at HRI-EU.
        """
        FastScript.requireIsTextNonEmpty( self.packageCategory )

        if self.packageCategory == 'External' or self._exists( 'src/sources.tar.bz2' ):
            return True
        else:
            return False


    #------------------------------------------------------------------------
    # Content type
    #------------------------------------------------------------------------


    def hasMainProgram( self, files=None ):
        """
            Searches in the package for main program source code files,
            typically located in 'bin/', 'examples/', and 'test/'.

            Provide 'files' with absolute paths to skip (repetitive)
            searching in the filesystem.
        """
        dirs = ( self.binDir, self.examplesDir, self.testDir )

        if FastScript.isIterable( files ):

            for filePath in files:
                filePath = os.path.abspath( filePath )

                if filePath.endswith( '.c' ) or filePath.endswith( '.cpp' ):

                    if filePath.startswith( dirs ):
                        logging.debug( 'found main program: %s', filePath )
                        return True

            return False

        else:
            logging.info( 'searching in filesystem' )

            for directory in dirs:
                hasCFile   = self._search( directory, '.c' )
                hasCppFile = self._search( directory, '.cpp' )

                if hasCFile or hasCppFile:
                    return True

            return False


    def isCPackage( self ):
        """
            Returns True if package contains C code in source directory.
        """
        return self._hasSourceFiles( '.c' )


    def isCppPackage( self ):
        """
            Returns True if package contains C++ code in source directory.
        """
        return self._hasSourceFiles( '.cpp' )


    def isPythonPackage( self, files=None ):
        """
            Returns True if it finds any *.py file in the optionally provided
            filelist or anywhere within the package, excluding pkgInfo.py.

            The exception of pkgInfo.py is made in order that a package
            containing C/C++ sources accompanied by a pkgInfo.py settings
            file isn't considered a Python module.
        """
        if files is None:
            files = FastScript.getFilesInDirRecursive( '.' )

        FastScript.requireIsIterable( files )

        for filePath in files:
            fileName = os.path.basename( filePath )
            if fileName != 'pkgInfo.py' and fileName.endswith( '.py' ):
                return True

        return False


    def isPythonModule( self ):
        """
            Returns True if it finds an __init__.py file anywhere within the
            package.
        """
        return self._search( self.topLevelDir, '__init__.py' )


    #------------------------------------------------------------------------
    # Values extracted from build system
    #------------------------------------------------------------------------


    def retrieveMakefileInfo( self ):
        """
            Helper function which retrieves all relevant information from
            build system.

            This function needs to be called before accessing the
            corresponding member fields.
        """
        if self.cmakelistsContent:
            self._parseCMakeLists()

        self._parsePkgInfo()
        self._getInheritedProjects()


    def retrieveMetaInfoFromSIT( self ):
        """
            Helper function which retrieves as much as possible information
            from a package installed into SIT, f.i. all info from pkgInfo.py.
        """
        self._parsePkgInfo()
        self.vcsRevision = self.gitCommitIdLong


        if self.gitOrigin and self.gitCommitIdLong:
            self.vcsBranch   = self.gitBranch
            self.vcsRevision = self.gitCommitIdLong
            self.vcsRelPath  = self.gitRelPath
            self.vcsURL      = self.gitOrigin
            self.vcsRoot     = self.gitOrigin

            FastScript.requireIsTextNonEmpty( self.vcsURL )
            FastScript.requireIsTextNonEmpty( self.vcsRevision )
            FastScript.isOptional( self.vcsRelPath )

        if not self.vcsURL:
            logging.debug( 'no Git repository information found' )

        self.isDeprecated = ProjectProperties.isDeprecated( self.canonicalPath )


    def retrieveVCSInfo( self ):
        """
            Helper function which retrieves all relevant information from
            underlying revision control system (Git).

            This function needs to be called before accessing the
            corresponding member fields.
        """
        self._retrieveGitInfo()

        if self.gitFound:
            self.vcsFound    = True
            self.vcsRevision = self.gitCommitIdLong
            self.vcsURL      = self.gitOrigin

        if not self.vcsURL:
            logging.debug( 'no Git repository information found' )


    #------------------------------------------------------------------------
    # Private helper functions
    #------------------------------------------------------------------------


    def _expandListOfTuples( self, l ):
        result = []

        for record in l:
            newRecord = ( record[0],    # probably no need to expand var.name
                          self._expandPlaceholders( record[1] ) )
            result.append( newRecord )

        return result


    def _expandListOfStrings( self, l ):
        result = []

        for line in l:
            newLine = self._expandPlaceholders( line )
            result.append( newLine )

        return result


    def _expandPlaceholders( self, s ):
        """
            replace placeholders in pkgInfo.py strings
        """
        FastScript.requireIsTextNonEmpty( self.packageCategory )
        FastScript.requireIsTextNonEmpty( self.packageName )
        FastScript.requireIsTextNonEmpty( self.packageVersion )

        installRoot = '${SIT}/%s/%s/%s' % ( self.packageCategory,
                                            self.packageName,
                                            self.packageVersion )

        result = s
        result = result.replace( '${INSTALL_ROOT}',     installRoot )
        result = result.replace( '${PACKAGE_CATEGORY}', self.packageCategory )
        result = result.replace( '${PACKAGE_NAME}',     self.packageName )
        result = result.replace( '${PACKAGE_VERSION}',  self.packageVersion )

        # also expand legacy strings
        result = result.replace( '${PROJECT_NAME}',     self.packageName )
        result = result.replace( '${FULL_VERSION}',     self.packageVersion )
        result = result.replace( '${PROJECT_START_PATH}', '${SIT}/' + self.packageCategory )

        return result


    def _parseCMakeLists( self ):
        if self.hasCMakeLists:
            filename          = os.path.join( self.topLevelDir, 'CMakeLists.txt' )
            logging.debug( 'reading %s', filename )

            content           = FastScript.getFileContent( filename )
            self.dependencies = CMakeLists.getDependencies( content )


    def _parsePkgInfo( self ):
        try:
            if not self.pkgInfoContent:
                self.pkgInfoContent = getPkgInfoContent( dirName=self.topLevelDir )
        except( AssertionError, IOError, OSError ):
            # Many packages lack a pkgInfo.py file within the source tree,
            # f.i they have no customizations. However in the SIT
            # installation such file exists if installed with our
            # Install Procedure. Handcrafted "LTS"-package might not have it.
            return
        except ( NameError, SyntaxError ):
            raise


        def getValue( key, default=None ):
            try:
                result = self.pkgInfoContent[ key ]
                # logging.debug( '%s=%s', key, result )
            except KeyError:
                result = default    # no such setting, fall back to default

            return result


        # 2019-02-13  Legacy, can be dropped later on
        self.gitBranch         = getValue( 'branch',           self.gitBranch )
        self.gitCommitIdLong   = getValue( 'commitID',         self.gitCommitIdLong )
        self.gitOrigin         = getValue( 'origin',           self.gitOrigin )
        self.gitRelPath        = getValue( 'repoRelPath',      self.gitRelPath )
        self.packageName       = getValue( 'package',          self.packageName ) # legacy 2018-09-26

        # 2020-07-14  Legacy, can be dropped later on
        self.packageCategory   = getValue( 'section',          self.packageCategory )

        # supposed to be used:
        self.userSrcAlias      = getValue( 'aliases',          self.userSrcAlias )
        self.buildCommand      = getValue( 'buildCommand',     'BST.py -sb' )
        self.buildDependencies = getValue( 'buildDepends',     self.buildDependencies )
        self.buildDependsArch  = getValue( 'buildDependsArch', self.buildDependsArch )
        self.packageCategory   = getValue( 'category',         self.packageCategory )
        self.copyright         = getValue( 'copyright',        self.copyright )
        self.dependencies      = getValue( 'depends',          self.dependencies )
        self.dependsArch       = getValue( 'dependsArch',      self.dependsArch )
        self.userSrcEnv        = getValue( 'envVars',          self.userSrcEnv )
        self.userSrcBashCode   = getValue( 'bashCode',         self.userSrcBashCode )
        self.gitBranch         = getValue( 'gitBranch',        self.gitBranch )
        self.gitCommitIdLong   = getValue( 'gitCommitID',      self.gitCommitIdLong )
        self.gitOrigin         = getValue( 'gitOrigin',        self.gitOrigin )
        self.gitRelPath        = getValue( 'gitRelPath',       self.gitRelPath )
        self.docFiles          = getValue( 'docFiles',         self.docFiles )
        self.docTool           = getValue( 'docTool',          self.docTool )
        self.install           = getValue( 'install',          self.install )

        for name in ( 'Install_onStartupStage1',
                      'Install_onStartupStage2',
                      'Install_onStartupStage3',
                      'Install_onStartupStage4',
                      'Install_onStartupStage5',
                      'Install_onExitStage1',
                      'Install_onExitStage2',
                      'Install_onExitStage3',
                      'Install_onExitStage4',
                      'Install_onExitStage5' ):
            self.installHooks[ name ] = getValue( name )

        self.installExclude    = getValue( 'installExclude',   self.installExclude )
        self.installGroup      = getValue( 'installGroup',     self.installGroup )
        self.installMatching   = getValue( 'installMatching',  self.installMatching )
        self.installMode       = getValue( 'installMode',      self.installMode  )
        self.installSymlinks   = getValue( 'installSymlinks',  self.installSymlinks )
        self.installUmask      = getValue( 'installUmask',     self.installUmask )
        self.packageName       = getValue( 'name',             self.packageName )
        self.patchlevel        = getValue( 'patchlevel',       self.patchlevel )
        self.recommendations   = getValue( 'recommends',       self.recommendations )
        self.scripts           = getValue( 'scripts',          self.scripts )
        self.suggestions       = getValue( 'suggests',         self.suggestions )
        self.usePatchlevels    = getValue( 'usePatchlevels',   self.usePatchlevels )
        self.packageVersion    = getValue( 'version',          self.packageVersion )    # both the same
        self.packageVersionRaw = getValue( 'version',          self.packageVersionRaw ) #    - " -


        if self.packageCategory and self.packageName and self.packageVersion:
            self.canonicalPath = os.path.join( self.packageCategory,
                                               self.packageName,
                                               self.packageVersion )

        self.userSrcEnv        = self._expandListOfTuples( self.userSrcEnv )
        self.userSrcAlias      = self._expandListOfTuples( self.userSrcAlias )
        self.userSrcBashCode   = self._expandListOfStrings( self.userSrcBashCode )
        self.userSrcCmdCode    = self._expandListOfStrings( self.userSrcCmdCode )

        if self.gitCommitIdLong:
            self.gitCommitIdShort = self.gitCommitIdLong[0:7]

        FastScript.requireIsIn( self.installMode, ( 'clean', 'incremental' ),
                         'invalid value of "installMode" in pkgInfo.py' )


    def _retrieveCurrentUser( self ):
        self.userAccount = FastScript.getCurrentUserName()
        self.userName    = FastScript.getCurrentUserFullName()

        if not self.userName:
            self.userName = self.userAccount


    def retrieveMaintainer( self ):
        try:
            data = self.pkgInfoContent[ 'maintainer' ]
        except ( KeyError, TypeError ):     # TypeError: pkgInfo might be None
            data = ProjectProperties.getMaintainerFromFilesystem( self.canonicalPath )
        except AssertionError:
            logging.debug( '%s: not a canonical path', self.canonicalPath )
            return
        except OSError:
            # unable to determine maintainer from SIT
            return

        if isinstance( data, tuple ):
            self.maintainerAccount = data[0]
            self.maintainerName    = data[1]

        else:
            FastScript.requireIsTextNonEmpty( data )
            self.maintainerAccount = data
            self.maintainerName    = data


    def _retrieveGitInfo( self ):
        from ToolBOSCore.Tools import Git

        try:
            repo = Git.LocalGitRepository()

            self.gitBranch         = repo.getCurrentBranch()
            self.gitCommitIdLong   = repo.getLastCommit()
            self.gitCommitIdShort  = repo.getLastCommit( short=True )
            self.gitRepositoryRoot = repo.detectRepositoryRoot()
            self.gitRelPath        = repo.getRepoRelativePath()
            self.gitFound          = True

            logging.debug( 'Git repo detected at %s (relPath=%s)',
                           self.gitRepositoryRoot, self.gitRelPath )
            try:
                self.gitOrigin    = repo.getOrigin()
            except ValueError as details:
                logging.debug( details )

        except ( subprocess.CalledProcessError, OSError ):
            logging.debug( 'this is not a Git repository' )
            self.gitFound = False

        except ValueError as details:  # e.g. has no 'origin'
            logging.warning( details )
            self.gitFound = False


    def _getInheritedProjects( self ):
        # This is a legacy combination of the real (not build-)dependencies
        # and recommendations. They all will get sourced to be in the PATH.
        #
        # Note that Non-SIT-dependencies (e.g. "deb://binutils") get
        # filtered out.

        from ToolBOSCore.Storage.SIT import strip

        tmpList = FastScript.reduceList( self.dependencies +
                                         self.recommendations )

        tmpList = filter( lambda s: not s.startswith( 'deb://' ), tmpList )

        self.inheritedProjects = list( map( lambda s: strip( s ), tmpList ) )


    def _exists( self, relativePath ):
        """
            Returns 'True' if <topLevelDir>/relativePath exists.
        """
        path = os.path.join( self.topLevelDir, relativePath )
        return os.path.exists( path )


    def _hasSourceFiles( self, extension ):
        """
            Searches in the "src" directory (and below) for files named
            "*extension" and returns True/False if found.

                if _hasSourceFiles( '.h' ) == True:
                    ...

            Note that a 'dot' needs to be provided if desired.
        """
        return self._search( os.path.join( self.topLevelDir, 'src' ), extension )


    def _replace( self, string, substMap ):
        result = string

        for ( key, value ) in substMap.items():
            result = result.replace( key, value )

        return result


    def _replaceList( self, candidates, substMap ):
        resultList = []

        for elem in candidates:
            resultList.append( self._replace( elem, substMap ) )

        return resultList


    def _search( self, path, extension ):
        """
            Searches in 'path' (and below) for files named "*extension"
            and returns True/False if found, e.g.:

                if search( path, '.py' ) == True:
                    ...

            Note that a 'dot' needs to be provided if desired.
        """
        logging.debug( 'searching in %s for *%s files', path, extension )

        for path, dirs, files in os.walk( path ):
            for fileName in files:
                if fileName.endswith( extension ):
                    return True

        return False


# EOF
