# -*- coding: utf-8 -*-
#
#  Build System Tools - a convenience wrapper around build systems
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


import collections
import glob
import grp
import io
import logging
import os
import re
import stat
import subprocess
import tempfile

from ToolBOSCore.Packages                 import PackageCreator
from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.Platforms                import Platforms
from ToolBOSCore.Settings                 import ToolBOSConf
from ToolBOSCore.Storage                  import VersionControl
from ToolBOSCore.Tools                    import RTMaps
from ToolBOSCore.Util                     import Any, FastScript


class InstallProcedure( object ):
    """
        This class represents the new Pythonic install procedure of
        ToolBOS.

        It follows the Template Method Design Pattern, which means that the
        default implementation (the so called 'template method') will be
        inherited and thus used unless a plugin doesn't overwrite it by
        itself.
            The design pattern also pre-defines the possible algorithm steps
        launched from the main entry method ("run()" in our case) resulting
        in an inversion of control (the run-method calls the plugins'
        callback function in pre-defined order).


        The following install routine target plugins are available:
          * installation into global SIT
          * installation into proxy SIT
          * tar archiver
    """

    def __init__( self, sourceTree=None, binaryTree=None,
                  stdout=None, stderr=None ):

        self.dryRun            = bool( FastScript.getEnv( 'DRY_RUN' ) )
        self.index             = []
        self.stdout            = stdout
        self.stderr            = stderr
        self.tempObjects       = []
        self.hostPlatform      = Platforms.getHostPlatform()
        self.platformList      = Platforms.getPlatformNames()
        self.details           = PackageDetector( sourceTree )
        self.projectURL        = None
        self.sitProxyPath      = None
        self.sitRootPath       = None
        self.dstSIT            = self.sitRootPath
        self.installRoot       = None
        self.startPath         = None

        self._outOfTree        = sourceTree and binaryTree and sourceTree != binaryTree
        self._sourceTree       = sourceTree
        self._binaryTree       = binaryTree if self._outOfTree else sourceTree
        self._installGroupID   = None
        self._installGroupName = None
        self._installUmask     = None
        self._protocolType     = 'sit://'

        self.details.retrieveMakefileInfo()
        self.details.retrieveVCSInfo()


    #------------------------------------------------------------------------
    # Template methods (in order of execution)
    #------------------------------------------------------------------------


    def showIntro( self ):
        pass


    def onStartup( self ):
        pass


    def preCollectMetaInfo( self ):
        pass


    def collectMetaInfo( self ):
        """
            Retrieve essential package meta-information such as name,
            version, and install category.
        """
        from ToolBOSCore.Storage.ProxyDir import isProxyDir
        from ToolBOSCore.Storage.SIT      import getPath
        from ToolBOSCore.Storage.SIT      import getParentPath

        self.projectURL     = self._protocolType + self.details.canonicalPath

        sitPath             = getPath()

        if isProxyDir( sitPath ):
            self.sitProxyPath = sitPath
            self.sitRootPath  = getParentPath( sitPath )
        else:
            self.sitRootPath  = sitPath


        env = FastScript.getEnv( 'BST_INSTALL_PREFIX' )

        if env:
            # forcing SIT root path with user-provided directory for
            # testing (TBCORE-1104)

            Any.requireIsTextNonEmpty( env )
            self.sitRootPath = env
            FastScript.mkdir( self.sitRootPath )


        if self.details.usePatchlevels and self.details.patchlevel is None:
            self._computePatchlevel()

        logging.info( 'package name:     %s', self.details.packageName     )
        logging.info( 'package version:  %s', self.details.packageVersion  )
        logging.info( 'package category: %s', self.details.packageCategory )
        logging.info( 'canonical path:   %s', self.details.canonicalPath   )
        logging.info( 'package:          %s', self.projectURL              )
        logging.info( 'patchlevel:       %s', self.details.patchlevel      )
        logging.info( 'source location:  %s', self.details.topLevelDir     )
        logging.info( 'proxy SIT:        %s', self.sitProxyPath            )
        logging.info( 'global SIT:       %s', self.sitRootPath             )
        logging.info( 'platform:         %s', self.hostPlatform            )

        Any.requireMsg( not os.path.isabs( self.details.packageCategory ),
                        'invalid package category "%s" (must be relative path)' % self.details.packageCategory )

        self._setUmask()

        try:
            self._setGroupName()
        except ValueError as details:
            logging.warning( 'unable to set user group in installation:' )
            logging.warning( details )


    def postCollectMetaInfo( self ):
        pass


    def makeDocumentation( self ):
        """
            Default implementation is to call the Documentation Creator,
            which in turn will create HTML documentation for the package.
        """
        from ToolBOSCore.BuildSystem.DocumentationCreator import DocumentationCreator

        if self._outOfTree:
            logging.warning( 'documentation creation in out-of-tree build not implemented' )
            return False


        if Any.getDebugLevel() > 3:
            output = None
        else:
            output = io.StringIO()

        dc = DocumentationCreator( self.details.topLevelDir, self.dstSIT,
                                   output, output, self.details )

        try:
            dc.generate()

        except AssertionError as e:

            logging.error( 'failed to create documentation: %s', e )
            return False

        except subprocess.CalledProcessError:

            if output:
                print( output.getvalue() )

            logging.error( 'failed to create documentation' )
            return False


    def makeShellfiles( self ):
        """
            Auto-generate BashSrc etc. files
        """
        from ToolBOSCore.Packages import PackageCreator
        PackageCreator.makeShellfiles( self.details.topLevelDir )


    def preCollectContent( self ):
        pass


    def collectContent( self ):
        """
            This method scans the source package for files/directories
            to be installed.

            The files aren't copied at this location. They are put in
            a dict mapping src => dst. The actual plugins implement the
            particular operation such as copying, linking, or whatsoever
            in their custom install() method.

            This method internally uses a smart package detector, so that
            different files are expected for the different kind of
            packages.

            If there is a 'pkgInfo.py' within the current package, it scans
            it for a list named 'install' which is supposed to contain
            tuples of ( srcPath, regexp, dstPath ). There are additional
            fields (see the documentation) to customize what gets
            installed and where.
        """
        self._extractVM()

        self._collectEssentials()

        self._registerComponent_ToolBOS()

        self._collectDefault()
        self._collectCustom()

        self._exclude()


    def postCollectContent( self ):
        """
            Shows the number of scheduled files
        """
        logging.info( 'scheduled %d files for installation', len( self.index ) )


    def confirmInstall( self ):
        """
            We want to give the user a chance to abort the installation
            in case of previous errors. So interactively ask if this is
            all OK.

            The interactive prompt will be skipped if the environment
            variable MAKEFILE_FASTINSTALL=TRUE or if BST.py is invoked
            with the '-y|--yes' option.
        """
        logging.info( 'ready for installation' )
        Any.logVerbatim( 3, '' )

        if FastScript.getEnv( 'MAKEFILE_FASTINSTALL' ) == 'FALSE' or \
           ToolBOSConf.getConfigOption( 'BST_confirmInstall' ) is True:

            try:
                prompt = '\t--> Install now? (Y/n)  '
                answer = input( prompt )
            except EOFError:
                # user hit <CTRL+D>
                raise KeyboardInterrupt( 'operation aborted by user' )

            if answer != '' and answer != 'y' and answer != 'Y':
                raise KeyboardInterrupt( 'operation aborted by user' )
            else:
                Any.logVerbatim( 3, '' )   # an additional newline after the prompt


    def preInstall( self ):
        """
            Prepare the installation.
        """
        pass


    def install( self ):
        """
            Performs the actual file operation, e.g. copying or symlinking
            the previously selected files and/or directories.
        """
        pass


    def setPermissions( self ):
        pass


    def postInstall( self ):
        """
            Finalize the installation.
        """
        pass


    def cleanUp( self ):
        """
            Removes temporary files and directories.
        """
        logging.info( 'removing temporary files' )

        for item in self.tempObjects:
            logging.debug( 'removing %s', item )
            FastScript.remove( item )


    def onExit( self ):
        pass


    @staticmethod
    def showOutro():
        """
            Shows some closing notes after the Install Procedure finished.
        """
        logging.info( 'Thank you for using ToolBOS!' )
        Any.logVerbatim( 3, '\n' + '-' * 78 + '\n\n' )


    #------------------------------------------------------------------------
    # main algorithm
    #------------------------------------------------------------------------


    def run( self ):
        """
            Main entry function
        """
        self.showIntro()

        self._showTitle( 'STAGE 1 # BASIC PACKAGE INFORMATION' )
        self.onStartup()
        self._executeHook( 'Install_onStartupStage1' )  # pkgInfo.py not read, yet
        self.preCollectMetaInfo()
        self.collectMetaInfo()
        self.postCollectMetaInfo()
        self._executeHook( 'Install_onExitStage1' )

        self._showTitle( 'STAGE 2 # AUTO-GENERATING FILES' )
        self._executeHook( 'Install_onStartupStage2' )
        self.makeShellfiles()
        self.makeDocumentation()
        self._executeHook( 'Install_onExitStage2' )

        self._showTitle( 'STAGE 3 # SCANNING PACKAGE' )
        self._executeHook( 'Install_onStartupStage3' )
        self.preCollectContent()
        self.collectContent()
        self.postCollectContent()
        self._executeHook( 'Install_onExitStage3' )

        self._showTitle( 'STAGE 4 # PERFORM FILE OPERATIONS' )
        self._executeHook( 'Install_onStartupStage4' )
        self.confirmInstall()
        self.preInstall()
        self._executeHook( 'preInstallHook' )
        self.install()
        self._executeHook( 'installHook' )
        self.setPermissions()
        self.postInstall()
        self._executeHook( 'postInstallHook' )
        self._executeHook( 'Install_onExitStage4' )

        self._showTitle( 'STAGE 5 # CLEAN-UP' )
        self._executeHook( 'Install_onStartupStage5' )
        self.cleanUp()
        self._executeHook( 'Install_onExitStage5' )
        self.onExit()
        self.showOutro()

        return True


    #------------------------------------------------------------------------
    # public helper functions
    #------------------------------------------------------------------------


    def copy( self, srcPath, dstPath=None, mandatory=False,
              relativeToSIT=False ):
        """
            Schedules the file or directory 'srcPath' for later
            installation. If mandatory=False and the file does not exist,
            the function will silently return.

            If 'srcPath' points to a directory, the entire content will
            be recursively added. If you don't want such behavior, please
            use copyMatching() -- or program individually.

            If the file should not appear on the same level, a relative
            'dstPath' can be provided.

            Note: Environment variables can be specified in both 'srcPath'
                  and 'dstPath', e.g. "config/${MAKEFILE_PLATFORM}".

                  However MAKEFILE_PLATFORM is a very specific one.
                  Besides the current value of this environment variable
                  we als look for other allowed values (other platform
                  strings). This means, with a single instruction you
                  can install files for multiple platforms in one shot
                  (see TBCORE-2148).
        """
        Any.requireIsTextNonEmpty( srcPath )
        Any.requireIsTextNonEmpty( self.startPath )


        # TBCORE-2148  Check if strings contain MAKEFILE_PLATFORM and
        #              attempt to copy files of all known platforms.

        multiArchInstall  = srcPath is not None and 'MAKEFILE_PLATFORM' in srcPath
        multiArchInstall |= dstPath is not None and 'MAKEFILE_PLATFORM' in dstPath

        if multiArchInstall:
            # call worker function for each platform, with modified parameters

            for platform in self.platformList:

                srcPathArch = srcPath.replace( '${MAKEFILE_PLATFORM}', platform )

                if dstPath is None:
                    dstPathArch = dstPath
                else:
                    dstPathArch = dstPath.replace( '${MAKEFILE_PLATFORM}', platform )

                self._copy( srcPathArch, dstPathArch, mandatory, relativeToSIT )

        else:
            # call worker function once with verbatim parameters
            self._copy( srcPath, dstPath, mandatory, relativeToSIT )

    def _copy( self, srcPath, dstPath, mandatory, relativeToSIT ):
        srcPath = FastScript.expandVars( srcPath )

        if dstPath is not None:
            dstPath = FastScript.expandVars( dstPath )

        if not mandatory and not os.path.exists( srcPath ):
            return

        if not dstPath:
            dstPath = srcPath
        else:
            Any.requireIsTextNonEmpty( dstPath )

        if srcPath == dstPath:
            logging.info( 'adding %s', dstPath )
        else:
            logging.info( 'adding %s --> %s', srcPath, dstPath )

        if os.path.isdir( srcPath ):
            for root, dirs, files in os.walk( srcPath ):

                for item in files:
                    itemSrcPath = os.path.join( root, item )

                    if dstPath:
                        itemDstPath = os.path.join( root.replace( srcPath, dstPath ),
                                                    item )

                    if itemDstPath.find( '.svn' ) == -1:   # do not install ".svn"
                        if relativeToSIT:
                            self.index.append( ( itemSrcPath, itemDstPath ) )
                        else:
                            self.index.append( ( itemSrcPath,
                                                 os.path.join( self.startPath, itemDstPath ) ) )

                # os.walks() puts symlinks to directories into the 'directories'
                # list, and not into 'files', hence symlinks like "focal64" -->
                # "bionic64" would not get installed, see JIRA ticket TBCORE-947
                for item in dirs:
                    itemSrcPath = os.path.join( root, item )

                    if os.path.islink( itemSrcPath ):
                        target      = os.readlink( itemSrcPath )
                        itemDstPath = os.path.join( root.replace( srcPath, dstPath ),
                                                    item )

                        logging.debug( 'found symlink to directory: %s --> %s',
                                       itemSrcPath, target )

                        self.link( target, itemDstPath )


        elif os.path.exists( srcPath ):
            if relativeToSIT:
                self.index.append( ( srcPath, dstPath ) )
            else:
                self.index.append( ( srcPath, os.path.join( self.startPath, dstPath ) ) )


    def copyMatching( self, srcDir, srcPattern, dstDir=None,
                      relativeToSIT=False ):
        r"""
            Schedules all files in the directory 'srcDir' which match
            the regular expression 'srcPattern' for later installation.

            If the file(s) should not appear on the same directory level,
            an alternative relative 'dstDir' can be provided, e.g.:

                copyMatching( 'doc',             # where to take from
                              r'\*.pdf',         # file pattern (regexp)
                              'manuals' )        # dir. where to install

            typical short-style usage:

                copyMatching( 'doc', r'.*\.pdf$' )

            with optional argument for destination directory:

                copyMatching( 'src', r'.*\.h', 'include' )

            This is a decorator for copyMatchingWorker(), which also shows
            some progress / debug infor about the copied files.

            Note: Environment variables can be specified in both 'srcDir'
                  and 'dstDir', e.g. "config/${MAKEFILE_PLATFORM}".

            Returns the number of files scheduled for installation
            (= number of files matching the regular expression).
        """
        Any.requireIsText( srcDir )
        Any.requireIsTextNonEmpty( srcPattern )
        # Any.requireIsText( dstDir )   # might be None

        srcDir = FastScript.expandVars( srcDir )

        if dstDir is not None:
            dstDir = FastScript.expandVars( dstDir )

        if srcDir == '':     # for convenience we allow empty srcDir
            srcDir = '.'

        if Any.isDir( srcDir ):
            logging.debug( 'searching for subDir="%s"...', srcDir )
        else:
            logging.debug( 'searching for subDir="%s"... Not found', srcDir )
            return []

        if not dstDir:
            dstDir = srcDir

        matching = self.copyMatchingWorker( srcDir, srcPattern, dstDir,
                                            relativeToSIT )

        if matching:
            logging.info( 'adding %s/<%s>', dstDir, srcPattern )
        else:
            logging.debug( 'not found: %s/<%s>', srcDir, srcPattern )

        return matching


    def copyMatchingWorker( self, srcDir, srcPattern, dstDir,
                            relativeToSIT=False ):
        r"""
            Schedules all files in the directory 'srcDir' which match
            the regular expression 'srcPattern' for later installation.

            If the file(s) should not appear on the same directory level,
            an alternative relative 'dstDir' can be provided, e.g.:

                copyMatching( 'doc',             # where to take from
                              r'\*.pdf',          # file pattern (regexp)
                              'manuals' )        # dir. where to install

            typical short-style usage:

                copyMatching( 'doc', r'.*\.pdf$' )

            with optional argument for destination directory:

                copyMatching( 'src', r'.*\.h', 'include' )

            Returns the number of files scheduled for installation
            (= number of files matching the regular expression).
        """
        Any.requireIsDir( srcDir )
        Any.requireIsTextNonEmpty( srcPattern )
        Any.requireIsTextNonEmpty( self.startPath )

        # we are not about file copying here, so do not check for real dir.
        # here (e.g. consider case when a tarball is created)
        #
        # Any.requireIsTextNonEmpty( dstDir )
        Any.requireIsText( dstDir )      # can be empty

        fileList = os.listdir( srcDir )
        try:
            regexp   = re.compile( srcPattern )
        except re.error as reError:
            logging.error( 'Message: %s', reError )
            logging.error( 'Pattern: \"%s\"', srcPattern )
            logging.error( 'Did you forget to escape the dot?' )
            logging.error( 'Did you provide a shell-wildcard?' )
            raise ValueError

        matching = list( filter( regexp.search, fileList ) )
        logging.debug( '%d items(s) in "%s", %d match expression',
                       len(fileList), srcDir, len(matching) )

        Any.requireIsList( matching )

        for entry in matching:
            src = os.path.join( srcDir, entry )
            dst = os.path.join( dstDir, entry )

            if relativeToSIT:
                self.index.append( ( src, dst ) )
            else:
                self.index.append( ( src, os.path.join( self.startPath, dst ) ) )

        return matching


    def copyMandatory( self, srcPath, dstPath=None, relativeToSIT=False ):
        """
            Schedules the file 'srcPath' for later installation.

            An AssertionError will be raised if the file does not exist.

            If the file(s) should not appear on the same directory level,
            an alternative relative 'dstDir' can be provided.

            Note: Environment variables can be specified in both 'srcPath'
                  and 'dstPath', e.g. "config/${MAKEFILE_PLATFORM}".
        """
        self.copy( srcPath, dstPath, mandatory=True,
                   relativeToSIT=relativeToSIT )


    def copyOptional( self, srcPath, dstPath=None, relativeToSIT=False ):
        """
            Schedules the file or directory 'srcPath' for later
            installation. If it does not exist, the function will silently
            return.

            If 'srcPath' points to a directory, the entire content will
            be recursively added. If you don't want such behavior, please
            use copyMatching() -- or program individually.

            If the file should not appear on the same level, a relative
            'dstPath' can be provided.

            Note: Environment variables can be specified in both 'srcPath'
                  and 'dstPath', e.g. "config/${MAKEFILE_PLATFORM}".
        """
        self.copy( srcPath, dstPath, mandatory=False,
                   relativeToSIT=relativeToSIT )


    @staticmethod
    def copyWorker( src, dst ):
        """
            A decorator for shutil.copy2() which preserves symlinks.
            (shutil.copy2() would copy the content instead.)
        """
        if os.path.lexists( dst ):      # lexists() considers broken links
            FastScript.remove( dst )

        dstDir = os.path.dirname( dst )

        # we had a case in AllPython where there was a file of same name
        # as 'dstDir', in case remove it first
        if os.path.isfile( dstDir ) or os.path.lexists( dstDir ):
            FastScript.remove( dst )

        if not os.path.isdir( dstDir ):
            FastScript.mkdir( dstDir )

        if os.path.islink( src ):
            target = os.readlink( src )
            FastScript.link( target, dst )
        else:
            # we had cases where some file attributes could not be applied
            # to a previously copied file, possibly some NFS hiccup
            # --> retry before raising exception
            FastScript.copyWithRetry( src, dst )


    def link( self, target, link, relativeToSIT=False ):
        """
            Schedules a symlink "link" for installation. The symlink will
            point to "target".

            Example:

              link( 'doc/examples', 'examples' )

            for a package "Libraries/Foo/1.0" will create a symlink
            $SIT/Libraries/Foo/1.0/examples --> doc/examples

            If relativeToSIT=True, long paths relative to SIT
            can be specified. This allows installing outside of the package
            directory.

            Example:

              link( '1.0.0', 'Libraries/Foo/1.0' )

            will yield a symlink $SIT/Libraries/Foo/1.0 --> 1.0.0

            Note: Environment variables can be specified in both 'link'
                  and 'target', e.g. "config/${MAKEFILE_PLATFORM}".
        """
        Any.requireIsTextNonEmpty( target )
        Any.requireIsTextNonEmpty( link )
        Any.requireIsTextNonEmpty( self.startPath )

        target = FastScript.expandVars( target )
        link   = FastScript.expandVars( link )

        ( fd, tmpFile ) = tempfile.mkstemp( prefix='install-' )

        # delete temporary file, create temporary symlink
        os.close( fd )
        FastScript.remove( tmpFile )
        FastScript.link( target, tmpFile )

        # schedule symlink for installation
        if relativeToSIT:
            linkPath = link
        else:
            linkPath = os.path.join( self.startPath, link )

        logging.info( 'adding %s --> %s', link, target )
        self.index.append( ( tmpFile, linkPath ) )
        self.tempObjects.append( tmpFile )


    #------------------------------------------------------------------------
    # private helper functions
    #------------------------------------------------------------------------


    def _collectEssentials( self ):
        """
            Collect basic files used by the ToolBOS SDK itself.
        """
        self.copyMandatory( 'install/BashSrc',          'BashSrc'    )
        self.copyMandatory( 'install/CmdSrc.bat',       'CmdSrc.bat' )
        self.copyMandatory( 'install/packageVar.cmake', 'packageVar.cmake' )
        self.copyMandatory( 'install/pkgInfo.py',       'pkgInfo.py' )


    def _collectDefault( self ):
        """
            Collect scripts, executables, libraries, documentation,...

        """
        self.copyMatching( 'bin', r'.*\.(m|php|py|sh)$', 'bin' )
        for platform in self.platformList:
            self.copyMatching( os.path.join( 'bin', platform ), '.*' )

        self.copyOptional( 'data' )
        self.copyOptional( 'doc/doxygen.tag' )
        self.copyOptional( 'doc/html' )
        self.copyMatching( 'doc', r'.*\.(jpg|log|pdf|png|txt)$' )
        self.copyOptional( 'etc' )
        self.copyOptional( 'include' )
        self.copyMatching( 'install', r'.*\.jar$', 'lib' )

        self.copyMatching( 'lib', r'.*\.jar$', 'lib' )
        for platform in self.platformList:
            self.copyMatching( os.path.join( 'lib', platform ),
                               '.*(a|def|dll|exp|lib|manifest|mex|mexa64|pck|so)' )

        if self.details.linkAllLibraries:
            dummyFile = os.path.join( 'install/LinkAllLibraries' )
            FastScript.setFileContent( dummyFile, '' )
            self.copyMandatory( dummyFile, 'LinkAllLibraries' )

        self.copyOptional( 'pymodules' )
        self.copyOptional( 'sbin' )
        self.copyMatching( 'src', r'.*\.(h|hpp)$', 'include' )
        self.copyOptional( 'web' )


    def _collectCustom( self ):
        """
            Collect user-defined files and directories
        """
        # "install" entries from pkgInfo.py
        for item in self.details.install:
            # whitelist may contain two kind of entries:
            # single string: srcDir
            # tuple:         ( srcDir, dstDir )

            if Any.isText( item ):
                workItem = ( item, item )  # dstDir=srcDir
            elif Any.isTuple(item) and len(item) == 2:
                workItem = item
            else:
                raise ValueError( 'unexpected object in section "install"' )

            logging.debug( '' )
            logging.debug( "custom install task: srcDir='%s' dstDir='%s'", *workItem )
            self.copy( *workItem )  # the asterisk explodes the tuple into 2 vars
            logging.debug( '' )


        # "installMatching" entries from pkgInfo.py
        for item in self.details.installMatching:
            # whitelist may contain two kind of tuples:
            # 2-element: ( srcDir, regexp )
            # 3-element: ( srcDir, regexp, dstDir )

            if len(item) == 2:
                workItem = ( item[0], item[1], item[0] )  # dstDir=srcDir
            elif len(item) == 3:
                workItem = item
            else:
                raise ValueError( 'unexpected tuple length=%d' % len(item) )

            logging.debug( '' )
            logging.debug( "custom install task: srcDir='%s' pattern='%s' dstDir='%s'", *workItem )
            self.copyMatching( *workItem )  # the asterisk explodes the tuple into 3 vars
            logging.debug( '' )


        # "installSymlinks" entries from pkgInfo.py
        for item in self.details.installSymlinks:
            # whitelist is list of tuples with 2 elements:
            # 2-element: ( target, link )

            if len(item) == 2:
                workItem = item
            else:
                raise ValueError( 'unexpected tuple length=%d' % len(item) )

            logging.debug( '' )
            logging.debug( "custom symlink task: target='%s' link='%s'", *workItem )
            self.link( *workItem )  # the asterisk explodes the tuple into 3 vars
            logging.debug( '' )


    def _computePatchlevel( self ):
        """
            Attempts to set the patchlevel from SVN revision.
            If this fails tries to compute from last globally installed
            revision.

            If package was never globally installed before
            --> raise exception.
        """
        from ToolBOSCore.Packages.ProjectProperties import splitVersion
        from ToolBOSCore.Storage.SIT                import getPath

        # check for environment variable
        env = FastScript.getEnv( 'MAKEFILE_PATCHLEVELVERSION' )

        if env:
            logging.info( 'found MAKEFILE_PATCHLEVELVERSION=%d', int(env) )
            self.details.patchlevel = int(env)


        if self.details.patchlevel is None:
            # try to set patchlevel from SVN revision
            if self.details.svnFound:
                self.details.patchlevel = self.details.svnRevision


        if self.details.patchlevel is None and not self.details.svnFound:
            # when not using SVN (e.g. Git), attempt to increment number of
            # last installation

            sitPath      = getPath()
            majorVersion = int( splitVersion( self.details.packageVersion )[0] )
            minorVersion = int( splitVersion( self.details.packageVersion )[1] )

            Any.requireIsTextNonEmpty( sitPath )
            Any.requireIsTextNonEmpty( self.details.canonicalPath )

            installRoot  = os.path.join( sitPath, self.details.canonicalPath )
            basedir      = os.path.dirname( installRoot )

            logging.debug( 'auto-detecting new patchlevel from last SIT installation' )
            existingPatchlevels = []

            if os.path.isdir( basedir ):
                for entry in sorted( os.listdir( basedir ) ):
                    tokens = splitVersion( entry )

                    # logging.debug( 'found existing version: %s', entry )

                    # keep a list of existing patchlevels
                    if int( tokens[0] ) == majorVersion and \
                       int( tokens[1] ) == minorVersion and \
                       tokens[2] != '':
                        existingPatchlevels.append( int(tokens[2]) )

            logging.debug( 'existing patchlevels for %d.%d: %s',
                           majorVersion, minorVersion, existingPatchlevels )

            if not existingPatchlevels:
                self.details.patchlevel = 0
            else:
                self.details.patchlevel = max(existingPatchlevels) + 1

            logging.debug( 'auto-detected new patchlevel: %d',
                           self.details.patchlevel )

        if self.details.patchlevel == -1:
            # fallback to zero as last resort
            self.details.patchlevel = 0

        Any.requireIsInt( self.details.patchlevel )


    def _exclude( self ) -> None:
        """
            Do not install files/directories appearing in the pkgInfo.py
            'installExclude' field, f.i. exclude them from getting installed.
        """
        excluded = self.details.installExclude

        if not excluded:
            return

        logging.info( 'skipping excluded files:' )

        toSkip = set()

        for pair in self.index:
            Any.requireIsTuple( pair )

            src = pair[0]

            for candidate in excluded:
                if src.startswith( candidate ):
                    logging.info( 'skipping %s', src )
                    toSkip.add( pair )

        for pair in toSkip:
            self.index.remove( pair )


    def _executeHook( self, name ):
        """
            Executes a user-defined function named "Install_<name>" which
            might be implemented in the package's pkgInfo.py file.

            Additionally a script "Install_<name>.sh" is searched.
            If present it will be executed.
        """
        Any.requireIsTextNonEmpty( name )

        try:
            f = self.details.installHooks[ name ]

            if f is not None:
                logging.debug( 'entering %s()', name )
                f( self )
                logging.debug( 'returned from %s()', name )

        except ( AttributeError, SyntaxError ) as details:
            logging.error( details )
            raise
        except KeyError:
            pass            # no such setting, this is OK


        if self.hostPlatform.startswith( 'windows' ):
            fileName = '%s.bat' % name
        else:
            fileName = './%s.sh' % name

        if os.path.exists( fileName ):
            logging.info( 'executing hook script: %s', fileName )
            FastScript.execProgram( fileName )


    def _extractVM( self ):
        """
            Attempts to run extractVM() over the package, in case it is
            a Virtual Module package.
        """
        if self.details.isComponent():
            from Middleware.BBMLv1.VirtualModules import extractVM

            srcDir     = 'src/'
            candidates = []
            candidates.extend( glob.glob( 'test/*.xml'  ) )
            candidates.extend( glob.glob( 'test/*.bbml' ) )

            try:
                candidates.remove( 'test/ModuleList.xml' )    # blacklisted
            except ValueError:
                pass   # no ModuleList.xml present

            if candidates:
                try:
                    logging.debug( 'trying to extract VM from %s', candidates[0] )
                    extractVM( self.details.topLevelDir, srcDir, candidates[0] )
                    self.copyMatching( 'src', r'.*\.xml$', 'include' )

                except ( AssertionError, IndexError ):    # most likely is not a VM package
                    logging.debug( "package doesn't seem to be a VM package" )
                except ValueError:
                    pass


    def _installWorker( self, rootDir ):
        """
            Copies all files from self.index() relative to <rootDir>.
        """
        Any.requireIsTextNonEmpty( rootDir )
        Any.requireIsDir( self.details.topLevelDir )

        for entry in self.index:
            key   = entry[0]
            value = entry[1]

            src   = os.path.join( self._binaryTree, key )

            if self._outOfTree and not os.path.exists( src ):
                # in case of out-of-tree builds also look for <sourceTree>/<src>
                src = os.path.join( self._sourceTree, key )

            dst = os.path.join( rootDir, value )

            if self.dryRun:
                logging.debug( '[DRY-RUN] cp %s %s', src, dst )
            else:
                self.copyWorker( src, dst )


    def _patchlevel_changeInstallRoot( self, sitPath ):
        Any.requireIsTextNonEmpty( sitPath )
        Any.requireIsTextNonEmpty( self.details.canonicalPath )

        if self.details.usePatchlevels:
            Any.requireIsInt( self.details.patchlevel )
            self.startPath = '%s.%d' % ( self.details.canonicalPath,
                                         self.details.patchlevel )
        else:
            self.startPath = self.details.canonicalPath

        self.installRoot = os.path.join( sitPath, self.startPath )
        logging.debug( 'installRoot=%s', self.installRoot )


    def _registerComponent_ToolBOS( self ):
        """
            Add a symlink to the pkgInfo.py file into the module index.
        """
        if self.details.isBBCM() or self.details.isBBDM():

            canonicalPath  = self.details.canonicalPath
            packageName    = self.details.packageName
            packageVersion = self.details.packageVersion

            symlinkFile    = '%s_%s.py' % ( packageName, packageVersion )
            symlinkRelPath = os.path.join( 'Modules', 'Index', symlinkFile )
            target         = os.path.join( '../..', canonicalPath, 'pkgInfo.py' )

            self.link( target, symlinkRelPath, True )


    def _setUmask( self ):
        """
            Look-up optional "installUmask" settings from

            a) env.variable
            b) pkgInfo.py
            c) ToolBOS.conf

            and in case set process umask accordingly.

            Note that in any case the provided umask is supposed to be a
            string, e.g. '0022'.
        """
        umask = FastScript.getEnv( 'MAKEFILE_INSTALL_UMASK' )

        if umask:
            logging.debug( 'found MAKEFILE_INSTALL_UMASK=%s', umask )

        if umask is None:
            umask = self.details.installUmask


        if umask is None:
            try:
                umask = ToolBOSConf.getConfigOption( 'installUmask' )
            except KeyError:
                pass                                # variable not set by user


        if umask is not None:

            if isinstance( umask, int ):
                # assume user wrote sth. like "umask = 2" in pkgInfo
                # --> interpret decimal value as octal
                self._installUmask = int( str(umask), 8 )

            else:
                # interpret as string, e.g. "umask = '0002'" in pkgInfo.py
                try:
                    self._installUmask = int( umask, 8 )    # store as octal
                except TypeError:
                    logging.error( 'invalid umask setting in pkgInfo.py' )
                    raise


            logging.info( 'setting umask=%s', umask )
            os.umask( self._installUmask )


    def _setGroupName( self ):
        """
            Look-up optional "installGroup" settings from

            a) env.variable
            b) pkgInfo.py
            c) ToolBOS.conf

            and in case set group name accordingly.
        """
        groupName = FastScript.getEnv( 'MAKEFILE_INSTALL_GROUPNAME' )

        if groupName:
            logging.debug( 'found MAKEFILE_INSTALL_GROUPNAME=%s', groupName )

        if groupName is None:
            groupName = self.details.installGroup

        if groupName is None:
            try:
                groupName = ToolBOSConf.getConfigOption( 'installGroup' )
            except KeyError:
                pass                        # variable not set by user

        if groupName is not None:
            Any.requireIsTextNonEmpty( groupName )

            try:
                groupID = grp.getgrnam( groupName ).gr_gid
                Any.requireIsIntNotZero( groupID )
                logging.info( 'setting group=%s (uid=%d)', groupName, groupID )

            except ( AssertionError, KeyError ):
                raise ValueError( '%s: No such user group' % groupName )

            self._installGroupID   = groupID
            self._installGroupName = groupName


    def _setPermissions( self, installRoot, sitRootPath ):
        """
            In case the user specified group permissions or different umask
            settings then they will get applied now.

            This is done here instead of at each copy-operation in order to
            ensure ALL files and subdirectories get the same settings.
            Otherwise some previously existing files/directories that are
            not considered by the install procedure would stay unchanged.
            Such behavior is not desired.
                Furthermore, in this implementation we can do tree-copying
            using the quite fast shutil.copytee().

            If the user does not have sufficient privileges to change
            groups and/or access modes then a warning will be displayed but
            the installation procedure can continue.
        """
        Any.requireIsDirNonEmpty( installRoot )
        Any.requireIsDir( sitRootPath )     # might be first proxy install.

        # set group and/or permissions
        groupID        = self._installGroupID
        groupName      = self._installGroupName
        umask          = self._installUmask

        # THEORY:
        #
        # In contrast to os.chown() / os.chmod() the functions os.lchown()
        # and os.lchmod() will not follow symbolic links. This is important
        # because we work a lot with symlinks to shared libraries, and we
        # want to set group permissions on the link itself.
        #
        # Apart from the obvious path, os.chown() / os.lchown() take two
        # further arguments for the desired UID and GID. Specifying either of
        # them as "-1" will keep their current value (= do not touch).
        #
        #
        # PRACTICE:
        #
        # On Ubuntu 12.04 the "os"-module lacks "lchmod()" even though it
        # should be there, see bug report:
        # https://mail.python.org/pipermail/python-list/2014-December/695982.html
        #
        # As a workaround we use os.chmod() and care not to call it on
        # symlinks.


        # Another issue: According to TBCORE-1033 one cannot change
        # ownership / set permission flags of the 'installRoot' directory
        # if belonging to another user.
        #
        # We agreed to ignore such OSError on the 'installRoot' directory,
        # but want to get informed about such problems for all files and
        # directories inside.

        if groupID is not None:

            warn = False

            try:
                # apply groupID to installRoot
                logging.debug( 'chgrp %s %s', groupName, installRoot )
                os.lchown( installRoot, -1, groupID )

            except OSError as details:
                logging.debug( details )
                warn = True


            # apply GID to installed content
            for root, dirs, files in os.walk( installRoot ):

                for item in dirs:
                    path = os.path.join( root, item )
                    logging.debug( 'chgrp %s %s', groupName, path )

                    try:
                        os.lchown( path, -1, groupID )
                    except OSError as details:
                        logging.debug( details )
                        warn = True

                for item in files:
                    path = os.path.join( root, item )
                    logging.debug( 'chgrp %s %s', groupName, path )

                    try:
                        os.lchown( path, -1, groupID )
                    except OSError as details:
                        logging.debug( details )
                        warn = True

            if warn:
                logging.warning( 'unable to set group=%s (see "-v" for details)', groupName )


        if umask is not None:

            dirMode = 0o777 & ~umask           # same for all directories
            warn    = False

            try:
                # apply umask to installRoot
                logging.debug( 'chmod %o %s', dirMode, installRoot )
                os.chmod( installRoot, dirMode )   # should not be a symlink

            except OSError as details:
                logging.debug( details )
                warn = True


            # apply umask to installed content
            for root, dirs, files in os.walk( installRoot ):

                for item in dirs:
                    path = os.path.join( root, item )
                    logging.debug( 'chmod %o %s', dirMode, path )

                    try:
                        os.chmod( path, dirMode )
                    except OSError as details:
                        logging.debug( details )
                        warn = True

                for item in files:
                    path = os.path.join( root, item )

                    # consider executable-flag of file when applying mode
                    #
                    # in case of symlink operate on the link itself
                    # (do not follow), CIA-1023
                    if stat.S_IXUSR & os.lstat( path )[stat.ST_MODE]:
                        fileMode = 0o777 & ~umask
                    else:
                        fileMode = 0o666 & ~umask

                    # <THEORY> (does not work due to bug in Ubuntu 12.04)
                    # logging.debug( 'chmod %o %s', fileMode, path )
                    # os.lchmod( path, fileMode )
                    # </THEORY>
                    #
                    # <WORKAROUND>
                    if not os.path.islink( path ):
                        logging.debug( 'chmod %o %s', fileMode, path )

                        try:
                            os.chmod( path, fileMode )
                        except OSError as details:
                            logging.debug( details )
                            warn = True
                    # </WORKAROUND>

            if warn:
                logging.warning( 'unable to set umask=%s (see "-v" for details)', str(umask) )


    @staticmethod
    def _showIntro( text ):
        """
            Show application name / headline at start-up.
        """
        Any.requireIsTextNonEmpty( text )

        version = ToolBOSConf.packageVersion
        Any.requireIsTextNonEmpty( version )

        display = 'TOOLBOS %s - %s' % ( version, text )

        Any.logVerbatim( 3, ''       )
        Any.logVerbatim( 3, 78 * '=' )
        Any.logVerbatim( 3, display  )
        Any.logVerbatim( 3, 78 * '=' )


    @staticmethod
    def _showTitle( title ):
        """
            Makes a visible break between the continuous loglines,
            to emphasize the installation stage transition.
        """
        Any.logVerbatim( 3, '\n' + '-' * 78 + '\n' )
        Any.logVerbatim( 3, title + '\n' )


class GlobalInstallProcedure( InstallProcedure ):

    def showIntro( self ):
        """
            Shows some opening header that the Install Procedure will start
            now.
        """
        self._showIntro( 'GLOBAL INSTALLATION PROCEDURE' )


    def postCollectMetaInfo( self ):
        Any.requireIsDir( self.sitRootPath )
        Any.requireIsTextNonEmpty( self.details.canonicalPath )

        try:
            self._vcsConsistencyCheck()
        except ValueError as details:
            FastScript.prettyPrintError( str(details) )
            raise SystemExit( details )

        self._patchlevel_changeInstallRoot( self.sitRootPath )


    def preInstall( self ):
        self._globalInstallReason()

        if self.details.installMode == 'clean':
            PackageCreator.uninstall( self.details.canonicalPath, True )


    def install( self ):
        """
            Performs the actual file operation, f.i. copying the previously
            selected files and/or directories into the global SIT.
        """
        Any.requireIsDir( self.sitRootPath )
        Any.requireIsTextNonEmpty( self.details.canonicalPath )

        logging.info( 'installing package... (this may take some time)' )

        logging.debug( '' )
        logging.debug( 'files to install:' )

        for entry in self.index:
            i, j = entry
            logging.debug( '%s --> %s', i, j )

        logging.debug( '' )

        self._installWorker( self.sitRootPath )
        self._ensureWorldWritableIndex()
        self._patchlevel_updateGlobalSymlink()
        self._updateProxyDir()


    def setPermissions( self ):
        self._setPermissions( self.installRoot, self.sitRootPath )


    def postInstall( self ):
        self._registerComponent_RTMaps()


    def _globalInstallReason( self ):
        """
            If the global SIT has been flagged to require a global install
            log message, the user will be interactively asked to input such.

            For batch processings, the user may also specify a message
            using the MAKEFILE_GLOBALINSTALLREASON environment variable.
        """
        if ToolBOSConf.getConfigOption( 'askGlobalInstallReason' ) is False:
            logging.debug( 'global install log disabled')
            return


        from ToolBOSCore.BuildSystem.GlobalInstallLog import GlobalInstallLog

        Any.requireIsTextNonEmpty( self.details.canonicalPath )

        try:
            reason = self._globalInstallReason_prompt()
        except ValueError:
            raise

        installRoot    = os.path.join( self.sitRootPath, self.details.canonicalPath )
        isFirstInstall = not os.path.exists( installRoot )
        msgType        = reason[:3]
        message        = reason[5:]

        g = GlobalInstallLog( self.details.canonicalPath, isFirstInstall,
                              msgType, message )

        # do not write in case MAKEFILE_CHEATCODE_42=TRUE is set
        if FastScript.getEnv( 'MAKEFILE_CHEATCODE_42' ) != 'TRUE':

            try:
                g.writeFile( self.dryRun )
            except ( IOError, OSError ) as details:
                # just that file might exist, especially during Nightly Build
                # two packages could by chance be installed simultaneously
                logging.warning( details )


    def _globalInstallReason_prompt(self):
        """
            Interactively asks the user for a global install reason.

            For batch processings, the user may also specify such message
            using the MAKEFILE_GLOBALINSTALLREASON environment variable.
        """
        Any.requireIsTextNonEmpty( self.details.canonicalPath )

        reason = FastScript.getEnv( 'MAKEFILE_GLOBALINSTALLREASON' )

        if not reason:
            logging.info( '' )
            logging.info( 'Please enter a reason for this global installation.' )
            logging.info( 'Syntax:  <TYPE>: <short description>' )
            logging.info( '' )
            logging.info( 'examples:' )
            logging.info( '    DOC: PDF manual updated' )
            logging.info( '    FIX: buffer overflow in _doCompute() fixed' )
            logging.info( '    IMP: improved performance by 20%' )
            logging.info( '    NEW: now supports shared memory' )
            logging.info( '' )
            logging.info( 'This will appear on the Global Install Log.' )
            logging.info( '' )

            try:
                prompt = '\n\t--> Reason:  '
                reason = input( prompt )
            except EOFError:
                # user hit <CTRL+D>
                raise KeyboardInterrupt( 'operation aborted by user' )

            if not reason:
                raise ValueError( 'no reason specified' )
            else:
                Any.logVerbatim( 0, '' )   # an additional newline after the prompt


        # remove leading and trailing spaces (if any)
        reason = reason.strip()

        try:
            self._globalInstallReason_verify(reason)
        except ValueError:
            raise

        return reason


    def _ensureWorldWritableIndex( self ):
        # when installing components, (try to) ensure the Index-directory is
        # world-writeable
        if self.details.isComponent():
            try:
                path = os.path.join( self.sitRootPath, 'Modules/Index' )
                logging.debug( 'chmod 0777 %s', path )
                os.chmod( path, 0o777 )
            except OSError as details:
                # probably not owner --> cannot change
                logging.debug( details )


    @staticmethod
    def _globalInstallReason_verify( reason ):
        """
            Checks if the provided input is somehow reasonable.

            It's not a sophisticated verification, but at least allows
            rejecting due to syntax errors (or too trivial messages).

            Throws 'ValueError' exceptions if messages are not OK.
            If the reason is OK it will return 'True'.
        """
        Any.requireIsTextNonEmpty( reason )

        # check for correct syntax
        if not re.match( '^(DOC|FIX|IMP|NEW)', reason ):
            msg = 'invalid reason type (must be one out of: DOC, FIX, IMP, NEW)'
            raise ValueError( msg )

        # syntax errors
        try:
            if reason[3] != ':':
                msg = 'invalid reason syntax (3rd character in message must be a colon (:) )'
                raise ValueError( msg )

            if reason[4] != ' ':
                msg = 'invalid reason syntax (4th character in message must be a blank/space)'
                raise ValueError( msg )
        except IndexError:
            raise ValueError( 'invalid reason (format: "TYPE: message")' )

        # given the type, the colon, a space and a minimum text length of
        # 5 characters, the overall length must at least be 10 characters
        if len(reason) < 10:
            msg = 'invalid reason (message too short)'
            raise ValueError( msg )

        if not re.match( r'^(DOC|FIX|IMP|NEW):\s\S+', reason ):
            msg = 'invalid reason syntax (please see examples)'
            raise ValueError( msg )

        # check for stupid message, check if reason contains at least 4
        # different characters
        if FastScript.countCharacters( reason ) < 4:
            msg = 'invalid reason (insufficient description)'
            raise ValueError( msg )

        return True

    def _patchlevel_updateGlobalSymlink(self):
        if self.details.usePatchlevels:

            # provide a normal version number symlink
            # within global installation, which will mainly be used
            symlink = os.path.join( self.sitRootPath,
                                    self.details.canonicalPath )
            target  = "%s.%d" % ( self.details.packageVersion,
                                  self.details.patchlevel )

            # ask the user whether or not to update the current symlink
            # (assume 'yes' in fastInstall-mode
            if FastScript.getEnv( 'MAKEFILE_FASTINSTALL' ) == 'TRUE':
                updateLink = True
            else:
                try:
                    prompt = '\n\t--> Update symlink %s --> %s (Y/n)?  ' % \
                             ( self.details.packageVersion, target )
                    answer = input( prompt )
                except EOFError:
                    # user hit <CTRL+D>
                    raise KeyboardInterrupt( 'operation aborted by user' )

                # remove leading and trailing spaces (if any)
                answer = answer.strip()

                if answer == '' or answer == 'y' or answer == 'Y':
                    updateLink = True
                else:
                    updateLink = False

                Any.logVerbatim( 0, '' )   # an additional newline after the prompt


            if updateLink:
                logging.info( 'updating version symlink' )
                FastScript.link( target, symlink )
            else:
                logging.info( 'keeping existing version symlink' )


    def _registerComponent_RTMaps( self ):
        """
            Register RTMaps component into user's index (if applicable).

            This step is skipped in case this is not an RTMaps package or
            the user does not have a proxy directory.
        """
        if self.details.isRTMapsPackage():

            if self.sitProxyPath:
                logging.info( 'registering RTMaps component' )
                RTMaps.registerNormalPackage( self.details.canonicalPath,
                                              self.sitProxyPath )
            else:
                logging.info( 'skipped RTMaps component registration (no proxy SIT found)' )


    def _updateProxyDir( self ):
        """
            Replace the symlink inside the proxy (if exists) by a one pointing
            to the global installation.
        """
        if self.sitProxyPath:
            symlink = os.path.join( self.sitProxyPath, self.details.canonicalPath )
            target  = os.path.join( self.sitRootPath,  self.details.canonicalPath )

            # delete old proxy content (might be directory with content in case
            # the package was installed in the proxy before)
            logging.debug( 'rm -r %s', symlink )   # symlink, or dir. content
            FastScript.remove( symlink )
            FastScript.link( target, symlink )

            if self.details.usePatchlevels:
                # provide the patchlevel-symlink within proxy, pointing to the
                # corresponding patchlevel in global SIT
                symlink = os.path.join( self.sitProxyPath,
                                        self.details.canonicalPath + '.' +
                                        str(self.details.patchlevel) )

                target  = os.path.join( self.sitRootPath,
                                        self.details.canonicalPath + '.' +
                                        str(self.details.patchlevel) )

                FastScript.link( target, symlink )


    def _vcsConsistencyCheck( self ):
        if FastScript.getEnv( 'MAKEFILE_SKIPSVNCHECK' ) == 'TRUE' or \
           ToolBOSConf.getConfigOption( 'BST_svnCheck' ) is False:

            logging.warning( 'VCS consistency check skipped' )
            return

        if not self.details.svnFound and not self.details.gitFound:
            logging.error( 'VCS consistency check failed' )
            msg = 'Global installation can only be done from a clean working tree.'
            raise ValueError( msg )


        vcs    = VersionControl.auto()
        errors = vcs.consistencyCheck()

        if errors:
            # Not performance-critical and too complex if rewritten.
            # pylint: disable=logging-not-lazy
            logging.error( errors[0] + ':' )
            logging.error( errors[1] )
            raise ValueError( errors[2] )

        logging.info( 'VCS consistency check passed' )


class ProxyInstallProcedure( InstallProcedure ):

    def __init__( self, sourceTree=None, binaryTree=None, stdout=None, stderr=None ):

        from ToolBOSCore.Storage import SIT

        super( ProxyInstallProcedure, self ).__init__( sourceTree, binaryTree, stdout, stderr )

        self.dstSIT = SIT.getPath()


    def showIntro( self ):
        """
            Shows some opening header that the Install Procedure will start
            now.
        """
        self._showIntro( 'PROXY INSTALLATION PROCEDURE' )


    def postCollectMetaInfo( self ):
        """
            Cancels the installation in case the user does not have a
            valid proxy directory where we could install to.
        """
        if not self.sitProxyPath:
            msg = 'Cannot perform proxy-installation: ' + \
                  '${SIT} points to "%s" which is not a proxy' % \
                  self.sitRootPath
            raise EnvironmentError( msg )


        Any.requireIsDir( self.sitProxyPath )
        self._patchlevel_changeInstallRoot( self.sitProxyPath )


    def makeDocumentation( self ):
        """
            Installing into proxy SIT is often used to debug a program.
            To speed-up installation time, we do not create the HTML
            documentation in this case.
        """
        logging.info( 'skipping documentation creation' )


    def install( self ):
        """
            Performs the actual file operation, f.i. copying the previously
            selected files and/or directories into the proxy SIT.
        """
        logging.info( 'installing package... (this may take some time)' )

        # replace symlink in proxy (not to accidently write into global SIT)
        if os.path.islink( self.installRoot ):
            logging.debug( 'rm %s', self.installRoot )
            os.remove( self.installRoot )

        # perform file operations
        self._installWorker( self.sitProxyPath )

        # when using patchlevels: provide a normal version number symlink
        # within proxy, pointing to global installation
        if self.details.usePatchlevels:
            symlink = os.path.join( self.sitProxyPath,
                                    self.details.canonicalPath )
            target  = "%s.%d" % ( self.details.packageVersion,
                                  self.details.patchlevel )

            FastScript.link( target, symlink )


    def setPermissions( self ):
        self._setPermissions( self.installRoot, self.sitProxyPath )


    def preInstall( self ):
        if self.details.installMode == 'clean':
            PackageCreator.uninstall( self.details.canonicalPath, False )


    def postInstall( self ):
        self._registerComponent_RTMaps()


    def _registerComponent_RTMaps( self ):
        """
            Register RTMaps component into user's index.
        """
        if self.details.isRTMapsPackage():
            logging.info( 'registering RTMaps component' )
            RTMaps.registerNormalPackage( self.details.canonicalPath,
                                          self.sitProxyPath )


class TarExportProcedure( InstallProcedure ):


    def __init__( self, sourceTree=None, binaryTree=None, stdout=None, stderr=None ):

        super( TarExportProcedure, self ).__init__( sourceTree, binaryTree, stdout, stderr )

        self._tmpDir   = None
        self._fileName = None


    def showIntro( self ):
        """
            Shows some opening header that the Tar Export Procedure will start
            now.
        """
        self._showIntro( 'TAR EXPORT PROCEDURE' )


    def confirmInstall( self ):
        """
            Suppress the confirmation by the user. Just do it.
        """
        pass


    def onStartup( self ):
        logging.debug( 'starting tar export' )

        self._tmpDir = tempfile.mkdtemp( prefix='install-' )
        self.tempObjects.append( self._tmpDir )
        logging.debug( 'tmpDir:          %s', self._tmpDir )


    def postCollectMetaInfo( self ):
        """
            Assemble the tarball's filename, in the form
            '<projectName>-<packageVersion>.tar.bz2
        """
        Any.requireIsTextNonEmpty( self.details.packageName )
        Any.requireIsTextNonEmpty( self.details.packageVersion )


        self.installRoot = self.details.canonicalPath

        # when using patchlevels: modify installRoot + provide symlink
        if self.details.usePatchlevels:
            Any.requireIsInt( self.details.patchlevel )
            self.startPath = '%s.%d' % ( self.details.canonicalPath,
                                         self.details.patchlevel )

            symlink = os.path.join( self.details.canonicalPath )
            target  = "%s.%d" % ( self.details.packageVersion,
                                  self.details.patchlevel )

            self.link( target, symlink, relativeToSIT=True )

        else:
            self.startPath = self.details.canonicalPath


        if self.details.usePatchlevels:
            self._fileName = './install/%s-%s.%d.tar.bz2' % ( self.details.packageName,
                                                              self.details.packageVersion,
                                                              self.details.patchlevel )
        else:
            self._fileName = './install/%s-%s.tar.bz2' % ( self.details.packageName,
                                                           self.details.packageVersion )
        logging.debug( 'filename=%s', self._fileName )


    def preInstall( self ):
        """
            Disables the interactive prompt.
        """
        pass


    def install( self ):
        """
            Performs the actual file operation, f.i. copying the previously
            selected files and/or directories into a temporary directory
            and create a tarball (*.tar.bz2) out of it.
        """
        Any.requireIsDir( self._tmpDir )

        self._installWorker( self._tmpDir )


    def setPermissions( self ):
        self._setPermissions( self._tmpDir, self._tmpDir )


    def postInstall( self ):
        """
            Packs the prepared content into a bzip2-compressed tarball.
        """
        import tarfile

        t = tarfile.open( self._fileName, 'w:bz2' )
        logging.info( 'writing %s...', self._fileName )

        for entry in self.index:
            key = entry[0]
            dst = entry[1]
            src = os.path.join( self._tmpDir, dst )

            logging.debug( dst )
            t.add( src, dst )

        t.close()


# EOF
