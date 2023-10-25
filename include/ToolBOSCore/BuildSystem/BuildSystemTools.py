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


import copy
import glob
import io
import logging
import os
import re
import subprocess

from ToolBOSCore.Packages                 import ProjectProperties
from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.Platforms                import Platforms
from ToolBOSCore.Settings.ToolBOSConf     import getConfigOption
from ToolBOSCore.Storage                  import SIT
from ToolBOSCore.Storage                  import PkgInfo
from ToolBOSCore.Util                     import Any
from ToolBOSCore.Util                     import FastScript


class BuildSystemTools( object ):

    def __init__( self ):
        self._hostPlatform   = Platforms.getHostPlatform()
        self._targetPlatform = self._hostPlatform
        self._oldCWD         = os.getcwd()
        self._origEnv        = copy.deepcopy( FastScript.getEnv() )
        self._stdout         = None
        self._stderr         = None

        self._sourceTree     = os.getcwd()
        self._binaryTree     = self._sourceTree
        self._outOfTree      = False
        self._buildDir       = os.path.join( self._sourceTree,
                                           'build',
                                           self._targetPlatform )

        self._buildType      = 'Release'
        self._crossCompiling = False
        self._isSetUp        = False
        self._isConfigured   = False
        self._isCompiled     = False
        self._runScripts     = FastScript.getEnv( 'BST_SKIP_SCRIPTS' ) != 'TRUE'

        self._cmakeModPath   = None
        self._cmakeOptions   = FastScript.getEnv( 'BST_CMAKE_OPTIONS' )

        self._detector       = PackageDetector( self._sourceTree )
        self._detector.retrieveMakefileInfo()

        try:
            self._parallelJobs = int( FastScript.getEnv( 'BST_BUILD_JOBS' ) )
        except ( KeyError, TypeError, ValueError ):
            self._parallelJobs = 1


    def configure( self ):
        """
            Get the package ready for building etc., e.g. create files required
            for the compilation.
        """
        self._setup()

        self._isConfigured = self._execTask( 'configure', self._cmakeConfigure )

        return self._isConfigured


    def compile( self ):
        """
            Main compiling/linking phase of the package.
        """
        # if package was not configured yet then do it now,
        #
        # Attention: Do not check for self._isConfigured because we allow
        #            "BST.py -b" which means build only (without configure).
        #            In such case self._isConfigured would be False and
        #            trigger an undesired re-configuration.
        #
        #            Better to check for existence of configure-artefact.
        self._setup()

        if not os.path.exists( self._buildDir ):
            self.configure()

        if not self._hostPlatform.startswith( 'windows' ):
            if not os.path.exists( os.path.join( self._buildDir, 'Makefile' ) ):
                self.configure()

        self._isCompiled = self._execTask( 'compile', self._cmakeCompile )

        return self._isCompiled


    def distclean( self ):
        """
            Performs a thorough cleaning of the package. This will remove all
            built files such as libraries or executables, but also auto-generated
            config- or temporary-files.

            Use this before importing a package to VCS.
        """
        logging.info( 'cleaning package' )

        if self._outOfTree:
            func = self._distclean_outOfTree
        else:
            func = self._distclean_inTree

        return self._execTask( 'distclean', func )


    def getBuildDir( self ):
        return self._buildDir


    def install( self ):
        """
            Installs a package into the Global SIT.
        """
        from ToolBOSCore.BuildSystem.InstallProcedure import GlobalInstallProcedure

        requireTopLevelDir( self._sourceTree )

        return GlobalInstallProcedure( self._sourceTree, self._binaryTree ).run()


    def makeDocumentation( self ):
        from ToolBOSCore.BuildSystem.DocumentationCreator import DocumentationCreator

        if self._outOfTree:
            logging.warning( 'documentation creation in out-of-tree build not implemented' )
            return False


        if Any.getDebugLevel() <= 3:
            # capture output so that it's not printed
            output = io.StringIO()
        else:
            output = None


        try:
            dstSIT = SIT.getPath()

            dc = DocumentationCreator( self._sourceTree, dstSIT, output, output )
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
        from ToolBOSCore.Packages import PackageCreator

        PackageCreator.makeShellfiles( self._sourceTree )


    def makeTarball( self ):
        """
            Creates a tarball with the same content as would be installed into
            the SIT.
        """
        from ToolBOSCore.BuildSystem.InstallProcedure import TarExportProcedure

        return TarExportProcedure( self._sourceTree, self._binaryTree ).run()


    def proxyInstall( self ):
        """
            Installs a package into the Proxy SIT.
        """
        from ToolBOSCore.BuildSystem.InstallProcedure import ProxyInstallProcedure

        requireTopLevelDir( self._sourceTree )

        return ProxyInstallProcedure( self._sourceTree, self._binaryTree ).run()


    def qualityCheck( self ):
        """
            Performs quality checks on the package.

            You may optionally specify list of rule IDs to run,
            and/or a list of files to consider.
            The default is to run all checkers on all files of the package.
        """
        from ToolBOSCore.SoftwareQuality.CheckRoutine import CheckRoutine

        cr = CheckRoutine()
        cr.run()

        return cr.overallResult()


    def runUnittest( self ):
        """
            There is no default Python-implementation for unittest.

            Hence we only search for and execute shellscripts
            such as unittest.sh.
        """
        dummy = lambda: True

        return self._execTask( 'unittest', dummy )


    def setStdOut( self, stdout ):
        self._stdout = stdout


    def setStdErr( self, stderr ):
        self._stderr = stderr


    def setSourceAndBinaryTree( self, sourceTree, binaryTree ):
        Any.requireIsDirNonEmpty( sourceTree )
        Any.requireIsDir( binaryTree )

        self._sourceTree = sourceTree
        self._binaryTree = binaryTree
        self._buildDir   = binaryTree
        self._outOfTree  = sourceTree and binaryTree

        self._detectBuildDir()
        self._detectModulePath()


    def setParallelJobs( self, number ):
        Any.requireIsIntNotZero( number )
        self._parallelJobs = number
        self._detectBuildCommand()

        # set env.var. so that child programs (incl. custom compile.sh
        # scripts) know about it
        FastScript.setEnv( 'BST_BUILD_JOBS', str(number) )


    def setBuildType( self, buildType ):
        Any.requireIsTextNonEmpty( buildType )

        Any.requireMsg( buildType in ( 'Release', 'Debug' ),
                        'invalid build type' )

        self._buildType = buildType


    def setTargetPlatform( self, platform ):
        Any.requireIsTextNonEmpty( platform )

        Any.requireMsg( platform in Platforms.getPlatformNames(),
                        "Unknown platform: %s" % platform )

        if platform != self._hostPlatform:
            self._crossCompiling = True
            self._targetPlatform = platform
            logging.info( 'targetPlatform=%s', self._targetPlatform )

            self._detectBuildDir()


    def uninstall( self, cleanGlobalInstallation=True ):
        from ToolBOSCore.Packages import PackageCreator

        detector = PackageDetector( self._sourceTree )
        detector.retrieveMakefileInfo()

        try:
            PackageCreator.uninstall( detector.canonicalPath,
                                      cleanGlobalInstallation )
            return True

        except OSError as details:
            logging.error( details )
            return False


    def upgrade( self ):
        from ToolBOSCore.CIA.PatchSystem import PatchSystem

        patcher = PatchSystem()
        patcher.run()


    def getCanonicalPath( self ):
        p = PackageDetector( self._sourceTree )
        p.retrieveMakefileInfo()
        canonicalPath = os.path.join( p.packageCategory,
                                      p.packageName,
                                      p.packageVersion )
        return canonicalPath


    def _assembleScriptCmd( self, name, forceFilePath=None ):
        Any.requireIsTextNonEmpty( name )

        # When compiling natively, under Linux the *.sh and on Windows the
        # *.bat needs to be executed.
        #
        # But also when cross-compiling we need to execute the script for
        # the host platform, f.i. a Windows *.bat script won't work on
        # Linux.
        #
        # Hence there is no need to check for the targetPlatform at all,
        # see TBCORE-1217.

        if self._hostPlatform.startswith( 'windows' ):
            filename = '%s.bat' % name
            cmd      = filename
        else:
            filename = '%s.sh' % name

            if forceFilePath:
                filename = forceFilePath

            if Any.getDebugLevel() > 3:
                cmd = 'bash -x ./%s' % filename
            else:
                cmd = './' + filename

        return filename, cmd


    def _cmakeConfigure( self ):
        requireTopLevelDir( self._sourceTree )


        # TBCORE-2163  silently return if no CMakeLists.txt present
        #              (e.g. in pure Python module)
        cmakeLists = os.path.join( self._sourceTree, 'CMakeLists.txt' )

        if not os.path.exists( cmakeLists ):
            logging.debug( '%s: No such file (skipping CMake execution)', cmakeLists )
            return True


        cmd = 'cmake -DCMAKE_MODULE_PATH=%s -DCMAKE_BUILD_TYPE=%s' % \
              ( self._cmakeModPath, self._buildType )

        if self._cmakeOptions is not None:
            cmd += ' %s' % self._cmakeOptions

        if self._outOfTree:
            cmd += ' -DBST_TOP_LEVEL_DIR=%s %s' % ( self._binaryTree,
                                                    self._sourceTree )

            FastScript.remove( 'CMakeCache.txt' )
            FastScript.remove( 'CMakeFiles' )
            FastScript.remove( 'cmake_install.cmake' )
        else:
            cmd += ' ../..'

            FastScript.remove( self._buildDir )
            FastScript.mkdir( self._buildDir )
            FastScript.changeDirectory( self._buildDir )


        try:
            retVal = FastScript.execProgram( cmd,
                                             stdout=self._stdout,
                                             stderr=self._stderr )

        except OSError as e:
            if e.errno == 2:                     # 'cmake' not installed
                raise EnvironmentError( "'cmake' is not installed" )
            else:
                raise

        except subprocess.CalledProcessError:
            retVal = -1
        finally:

            if not self._outOfTree:
                FastScript.changeDirectory( self._oldCWD )

        return True if retVal == 0 else False


    def _cmakeCompile( self ):
        requireTopLevelDir( self._sourceTree )


        # TBCORE-2163  silently return if no CMakeLists.txt present
        #              (e.g. in pure Python module)
        cmakeLists = os.path.join( self._sourceTree, 'CMakeLists.txt' )

        if not os.path.exists( cmakeLists ):
            logging.debug( '%s: No such file (skipping CMake execution)', cmakeLists )
            return True


        try:
            FastScript.execProgram( self._buildCmd,
                                    stdout=self._stdout,
                                    stderr=self._stderr,
                                    workingDir=self._buildDir )
            return True

        except subprocess.CalledProcessError:
            return False


    def _detectBuildCommand( self ):
        """
            Assembles the commandline to actually invoke the build toolchain.

            On Linux machines this returns 'make' (with some options),
            otherwise uses the build command specified in the used CMake
            generator.

            Why we can't use "cmake --build" on Linux? CMake does not
            support colored make-output due to some tty restrictions.

            For details see:
            http://cmake.3232098.n2.nabble.com/quot-cmake-build-quot-and-colors-td7584342.html
        """
        if self._hostPlatform.startswith( 'win' ):
            # On Windows the build configuration must be specified at build time,
            # not at configuration time
            #
            # http://stackoverflow.com/questions/19024259/how-to-change-the-build-type-to-release-mode-in-cmake

            self._buildCmd = 'cmake --build . --config Release'
        else:
            if self._parallelJobs == 1:
                self._buildCmd = 'make'
            else:
                self._buildCmd = 'make -j %d' % self._parallelJobs


    def _detectBuildDir( self ):
        if self._outOfTree:
            self._buildDir = self._binaryTree
        else:
            self._buildDir = os.path.join( self._sourceTree,
                                           'build',
                                           self._targetPlatform )

        logging.debug( 'build dir: %s', self._buildDir )


    def _detectModulePath( self ):
        # in out-of-tree build situations add the source-directory's
        # ToolBOS.conf to the extra search path for "getConfigOption()"
        # (TBCORE-1052)

        if self._outOfTree:
            envName  = 'TOOLBOSCONF_PATH'
            envValue = '%s:%s' % ( self._sourceTree, FastScript.getEnv( envName ) )
            logging.debug( 'registering extra ToolBOS.conf dir: %s', self._sourceTree )
            FastScript.setEnv( envName, envValue )

        cmakeModPath  = getConfigOption( 'BST_modulePath' )
        cmakeModPath  = FastScript.expandVars( cmakeModPath )

        if self._outOfTree and not os.path.isabs( cmakeModPath ):
            cmakeModPath = os.path.abspath( os.path.join( self._sourceTree, cmakeModPath ) )

        try:
            Any.requireIsDirNonEmpty( cmakeModPath )
        except AssertionError as details:
            logging.error( 'invalid setting of BST_modulePath in ToolBOS.conf' )
            logging.error( details )
            raise

        self._cmakeModPath = cmakeModPath


    def _execTask( self, name, corefunc ):
        Any.requireIsTextNonEmpty( name )
        Any.requireIsCallable( corefunc )

        logging.debug( 'Build System Tools: "%s" step started', name )

        status = self._runScript( 'pre-%s' % name )

        if status:
            self._switchToTargetEnv()

            coreScript = self._assembleScriptCmd( name )[0]

            if name in self._detector.scripts:
                filePath = self._detector.scripts[ name ]
                Any.requireIsFileNonEmpty( filePath )
                status = self._runScript( name, filePath=filePath )

            elif os.path.exists( coreScript ):
                status = self._runScript( name )

            else:
                status = corefunc()

            self._switchToHostEnv()

        if status:
            status = self._runScript( 'post-%s' % name )

        logging.debug( 'Build System Tools: "%s" step finished', name )
        return status


    def _distclean_outOfTree( self ):

        # Safety check (TBCORE-1635):
        #
        # We experienced that switching directories within Midnight
        # Commander and invoking a sub-shell with "BST.py -d" could lead
        # to an incorrect assumption that we perform an out-of-tree build
        # although it is a normal in-tree-build.
        #
        # In this case, the current package is considered to be a build
        # directory and deleted at "BST.py -d" -- effectively destroying
        # work results that have not been committed, yet.
        #
        # To prevent deletion in such cornercase we check for files and
        # directories that could indicate such cornercase:

        for candidate in ( 'CMakeLists.txt', 'packageVar.cmake',
                             'pkgInfo.py', 'src', 'build' ):

            if os.path.exists( candidate ):
                msg = 'TBCORE-1635 CORNERCASE DETECTED, PERFORMING EMERGENCY EXIT!'
                raise SystemExit( msg )

        logging.debug( 'passed safety check' )

        for entry in os.listdir( self._binaryTree ):
            try:
                FastScript.remove( entry )
            except ( IOError, OSError ) as details:
                logging.error( details )

        return True


    def _distclean_inTree( self ):
        from ToolBOSCore.Storage import VersionControl

        requireTopLevelDir( os.getcwd() )

        excludeSVN = re.compile( '.svn' )
        subDirList = FastScript.getDirsInDirRecursive( excludePattern=excludeSVN )
        subDirList.append( '.' )

        # do not cache those variables as their change would not be reflected
        # in such case (interactive sessions will continue to use the value
        # as it was at module loading time)
        verbose = True if os.getenv( 'VERBOSE' ) == 'TRUE' else False
        dryRun  = True if os.getenv( 'DRY_RUN' ) == 'TRUE' else False

        patternList = _getDistcleanPatterns()

        for subDir in subDirList:
            _cleanDir( subDir, patternList, verbose, dryRun )


        # specifically check for empty directories (mind the ".svn"):
        for candidate in ( 'doc', 'install', 'lib', 'obj' ):
            if os.path.isdir( candidate ):
                content = os.listdir( candidate )

                if not content:
                    FastScript.remove( candidate )  # does not contain ".svn"
                elif content == [ '.svn' ]:

                    # With recent versions of SVN there are no more ".svn"
                    # directories in all the various paths, instead of a
                    # single one in top-level directory. Therefore most
                    # likely this code is dead.

                    try:
                        vcs = VersionControl.auto()
                        vcs.remove( candidate )
                    except subprocess.CalledProcessError:
                        pass                        # keep it (safety first)

        return True


    def _runScript( self, name, filePath=None ):
        Any.requireIsTextNonEmpty( name )

        ( filename, cmd ) = self._assembleScriptCmd( name, forceFilePath=filePath )
        status = True

        if os.path.exists( filename ):
            try:
                FastScript.execProgram( cmd )
            except subprocess.CalledProcessError:
                status = False
            except OSError as details:
                logging.error( '%s: %s', cmd, str(details) )
                status = False

        return status


    def _setHostEnv( self ):
        """
            Set some environment variables which are used by some
            CMakeLists.txt / packageVar.cmake files.

            Note: Target-related env.variables (TARGETARCH etc.) will be
                  temp. modified by self._switchToTargetEnv() and
                  set back with self._switchToHostEnv().
        """
        hostArch = Platforms.getHostArch()
        hostOS   = Platforms.getHostOS()

        clangEnv = FastScript.getEnv( 'BST_USE_CLANG' )

        if clangEnv is None:
            try:
                useClang = PkgInfo.getPkgInfoContent()['BST_useClang']
            except ( AssertionError, KeyError ):
                useClang = getConfigOption( 'BST_useClang' )

            clangEnv = 'TRUE' if useClang else 'FALSE'

        else:
            useClang = True if clangEnv == 'TRUE' else False


        logging.debug( 'use Clang/LLVM: %s', useClang )

        envSettings  = { 'BST_USE_CLANG': clangEnv,
                         'HOSTARCH':      hostArch,
                         'HOSTOS':        hostOS,
                         'TARGETARCH':    hostArch,
                         'TARGETOS':      hostOS }

        FastScript.getEnv().update( envSettings )


    def _setup( self ):
        """
            Private setup phase. We do not do this in __init__() because
            not needed in all instances, and in many cases will be
            superfluous because needs to be re-done if one or the other
            setXY() function is called.

            Therefore we do it just before really needed.
        """
        if not self._isSetUp:
            self._setHostEnv()
            self._detectBuildCommand()
            self._detectBuildDir()
            self._detectModulePath()

            self._isSetUp = True


    def _switchToHostEnv( self ):
        if self._crossCompiling:
            logging.debug( 'switching to host environment (%s)',
                           self._hostPlatform )

            if self._targetPlatform.startswith( 'windows' ):
                from ToolBOSCore.Settings import UserSetup

                UserSetup.waitWineServerShutdown( UserSetup.getWineConfigDir() )

            FastScript.setEnv( self._origEnv )


    def _switchToTargetEnv( self ):
        """
            Load cross-compilers and board support packages
            when performing cross-compilation.
        """
        if self._crossCompiling:
            from ToolBOSCore.Platforms import CrossCompilation


            logging.debug( 'switching to target environment (%s)',
                           self._targetPlatform )

            CrossCompilation.switchEnvironment( self._targetPlatform )

            if self._targetPlatform.startswith( 'windows' ):
                from ToolBOSCore.Settings import UserSetup

                UserSetup.startWineServer( UserSetup.getWineConfigDir() )

            self._cmakeOptions = FastScript.getEnv( 'BST_CMAKE_OPTIONS' )


#----------------------------------------------------------------------------
# Settings, constants and defaults
#----------------------------------------------------------------------------


def getDefaultDistcleanPatterns():
    """
        Returns the list of filename patterns to be used by the
        distclean routine.
    """
    patternList = []

    for platform in Platforms.getPlatformNames():
        patternList.append( os.path.join( 'bin',      platform ) )
        patternList.append( os.path.join( 'examples', platform ) )
        patternList.append( os.path.join( 'lib',      platform ) )
        patternList.append( os.path.join( 'obj',      platform ) )
        patternList.append( os.path.join( 'src',      platform ) )
        patternList.append( os.path.join( 'test',     platform ) )
        patternList.append( os.path.join( 'wrapper',  platform ) )

    patternList.extend( [

                  # big directories first
                  'sources', 'build', '.tmp-install*', 'precompiled/package',

                  # compilation files
                  'makeDepend', 'ui_*h', 'qrc_*.cpp', 'moc_*.cpp', 'qt/*.h',
                  'qt/*.cpp', 'qt/moc_*cpp', '.*ui.md5', 'wrapper/*.mex*',

                  # editor backup files
                  '*~', '*.bak',

                  # temp. files left from previous program executions
                  '*.pyc', '*.backup.zip', 'LibIndex',

                  # pylint log files
                  '*_pylint.log',

                  # install procedure files
                  'install/??shSrc', 'bin/??shSrc',
                  'examples/??shSrc', 'test/??shSrc', 'install/CmdSrc.bat',
                  'doc/autoDoxyfile', 'doc/doxygen*', 'doc/*.tag',
                  'doc/html', 'matdoc.log', 'install/LinkAllLibraries',
                  'install/MD5SUMS', 'install/*.tar.gz', 'install/*.deb',
                  'install/*.tar.bz2', 'install/packageVar.cmake',
                  'install/pkgInfo.py', 'install/*.def',
                  'install/debControl.txt',
                  '[A-Za-z]*[A-Za-z]PHP', '[A-Za-z]*[A-Za-z]PY',
                  'run*([^.])', 'src/.*.h.md5', 'build4all.cfg', 'run' ] )

    return patternList


#----------------------------------------------------------------------------
# Public functions
#----------------------------------------------------------------------------


def setEnv():
    """
        This function loads the pkgInfo.py of each dependency package.
        If environment settings are found there they will be loaded into
        the environment of the current Python process.

        Example:
            The pkgInfo.py of Matlab states MATLAB_ROOT, PATH and
            LD_LIBRARY_PATH settings in its pkgInfo.py. Before compiling
            such variables must be set.

        On Linux, alternatively, this can be achieved by sourcing the
        BashSrc files. Nevertheless this is not possible in all cases
        (especially Matlab because multiple versions are available)
        when used within CIA.

        With some modifications this setEnv() approach conceptually
        potentially could also work on Windows.

        Attention: This function should only be called once (at least not
                   repeatedly when compiling the same package again from
                   within Python) to not unnecessarily increase the length
                   of PATH, LD_LIBRARY_PATH etc.
    """
    try:
        p = PackageDetector()
    except AssertionError:
        # XIF packages are generated on-the-fly during configure-phase.
        # We don't consider such packages for now (experimental code).
        return

    p.retrieveMakefileInfo()

    for package in p.dependencies + p.buildDependencies:
        try:
            envVars = PkgInfo.getPkgInfoContent( SIT.strip(package) )['envVars']
        except ( AssertionError, KeyError ):
            envVars = []                         # no envVars specified
        except ( IOError, OSError, SyntaxError ) as details:
            logging.error( details )
            raise RuntimeError( 'unable to read pkgInfo.py of %s' % package )

        if envVars:
            logging.debug( 'found environment settings:' )
            logging.debug( envVars )

            for varName, varValue in envVars:
                FastScript.setEnv_withExpansion( varName, varValue )


#----------------------------------------------------------------------------
# Private functions
#----------------------------------------------------------------------------


def isTopLevelDir( path='.' ):
    """
        Returns a boolean whether or not the provided directory is the
        top-level-directory of a source package.
    """
    regExpVersion   = re.compile( r"^(\d+\.\d+).*$" )
    projectVersion  = ProjectProperties.getPackageVersion( path, verbatim=True )
    versionDirFound = bool( regExpVersion.search( projectVersion ) )

    cmakeListsFile  = os.path.join( path, 'CMakeLists.txt' )
    packageVarFile  = os.path.join( path, 'packageVar.cmake' )
    pkgInfoFile     = os.path.join( path, 'pkgInfo.py' )

    if versionDirFound:
        return True
    else:
        return os.path.exists( cmakeListsFile ) or \
               os.path.exists( packageVarFile ) or \
               os.path.exists( pkgInfoFile )


def requireTopLevelDir( path='.' ):
    """
        Throws a RuntimeError in case the current working directory
        is not the top-level directory of a source package.
    """
    if path == '.' or not path:
        path = os.getcwd()

    Any.requireMsg( isTopLevelDir( path ),
                    '%s: not a top-level directory of a source package' % path )


def _getDistcleanPatterns():
    """
        Returns a list of regular expressions, which would be deleted by
        the distclean() function.

        To opt-in / opt-out patterns, create a Python file named
        'pkgInfo.py' within your project's top-level directory
        (e.g. inside Spam/42.0):

          delete      = [ 'deleteMe.*\\.txt' ]
          doNotDelete = [ 'install/??shSrc' ]

        The patterns in the 'doNotDelete' list should be taken from
        getDefaultDistcleanPatterns().
    """
    filename   = os.path.join( os.getcwd(), 'pkgInfo.py' )
    resultList = getDefaultDistcleanPatterns()

    try:
        content = PkgInfo.getPkgInfoContent()
    except AssertionError:
        return resultList


    try:
        for elem in content['delete']:
            resultList.append( elem )
            logging.debug( 'distclean opt-in: %s', elem )
    except TypeError as details:
        logging.error( 'error in %s: %s', filename, details )
    except KeyError:
        pass


    try:
        for elem in content['doNotDelete']:
            try:
                resultList.remove( elem )
                logging.debug( 'distclean opt-out: %s', elem )
            except ValueError:
                logging.debug( 'not in distclean-whitelist: %s', elem )
    except TypeError as details:
        logging.error( 'error in %s: %s', filename, details )
    except KeyError:
        pass


    return resultList


## ALERT! Mind to specify correctly as tuple with the comma, otherwise
##        it is a tuple of characters ;-) leading to that "." gets
##        entirely deleted!
##
#  Example:
##
## _removeList( ( 'pkgInfo.py', ), verbose, dryRun )

def _removeList( pathList, verbose, dryRun ):
    # pathList was just detected via glob.glob(), avoid additional check
    # if file exists (for speed-up reasons, but also this check would fail
    # in case of broken links)
    for path in pathList:
        if dryRun:
            logging.info( '-- DRY RUN --   not really deleting %s', path )
        else:
            FastScript.remove( path )


def _cleanDir( path, patternList, verbose, dryRun ):
    Any.requireIsText( path )
    Any.requireIsIterable( patternList )

    for pattern in patternList:
        patternFullPath = os.path.join( path, pattern )
        matchingList    = glob.glob( patternFullPath )

        if matchingList:
            _removeList( matchingList, verbose, dryRun )


# EOF
