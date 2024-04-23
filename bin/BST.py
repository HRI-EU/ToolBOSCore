#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Build System Tools - high-level build system functions
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

from ToolBOSCore.BuildSystem         import BuildSystemTools
from ToolBOSCore.Platforms.Platforms import getHostPlatform
from ToolBOSCore.Util                import ArgsManagerV2
from ToolBOSCore.Util                import FastScript
from ToolBOSCore.Util                import Any


#----------------------------------------------------------------------------
# Helper functions
#----------------------------------------------------------------------------


def _checkForUpdates():
    """
        Check if there are any updates for this package.
    """
    from ToolBOSCore.CIA.PatchSystem import PatchSystem

    logging.debug( 'checking for updates' )

    oldDebugLevel = Any.getDebugLevel()
    Any.setDebugLevel( 1 )

    patcher = PatchSystem()
    result  = patcher.run( dryRun=True )

    Any.setDebugLevel( oldDebugLevel )

    if len(result) > 0:
        logging.info( '' )
        logging.info( '\033[7;37m\033[1;31m' + ' ' * 60 + '\033[0m' )
        logging.info( '\033[1;31mupdates are available for this package:\033[0m' )

        for patch in result:
            logging.info( '  - %s', patch[0] )

        logging.info( '' )
        logging.info( '' )
        logging.info( '\033[0;31mYou may apply them using "BST.py --upgrade".\033[0m' )
        logging.info( '\033[7;37m\033[1;31m' + ' ' * 60 + '\033[0m' )
        logging.info( '' )
    else:
        logging.debug( 'no need to patch' )


def _createPackage( args, flatStyle ):
    from ToolBOSCore.Packages import PackageCreator


    try:
        templateName = args[0]
    except IndexError:
        templateName = None


    if templateName is None:
        # cmdline arguments were not specified, open GUI in this case
        from ToolBOSCore.Packages.PackageCreatorGUI import PackageCreatorGUI
        PackageCreatorGUI().main()
        return True

    elif templateName == 'help':
        _showAvailableTemplates()
        return True

    else:
        try:
            packageName    = args[1]
            packageVersion = args[2]
            return PackageCreator.runTemplate( templateName, packageName, packageVersion,
                                               flatStyle=flatStyle )
        except IndexError:
            logging.error( 'Please specify a package name and version (see help)' )
            return False


def _parseSqArgs( cr, argv ):
    import re

    from ToolBOSCore.SoftwareQuality import CheckRoutine, Common, Rules

    Any.requireIsInstance( cr, CheckRoutine.CheckRoutine )
    Any.requireIsList( argv )

    try:
        # ensure that script-name does not appear in this list
        argv.remove( sys.argv[0] )
    except ValueError:
        pass


    ruleIDs     = Rules.getRuleIDs()
    forceDirs   = set()
    forceFiles  = set()
    forceLevel  = None
    forceGroups = None
    forceRules  = []

    for arg in argv:

        if arg in ruleIDs:
            logging.debug( 'requested checking rule ID: %s', arg )
            forceRules.append( arg )

        elif os.path.isdir( arg ):
            logging.debug( 'requested checking directory: %s', arg )
            forceDirs.add( os.path.abspath( arg ) )

        elif os.path.exists( arg ):
            logging.debug( 'requested checking file: %s', arg )
            forceFiles.add( os.path.abspath( arg ) )

        elif arg.startswith( 'sqLevel=' ):
            tmp = re.search( 'sqLevel=(\S+)', ' '.join(argv) )

            if tmp:
                forceLevel = tmp.group(1)
            else:
                msg = f"Wrong usage: please specify a quality level {Common.sqLevelNames}"
                raise ValueError( msg )

        elif arg.startswith( 'group=' ):
            tmp = re.search( 'group=(\S+)', ' '.join(argv) )

            if tmp:
                forceGroups = tmp.group(1)
            else:
                msg = f"Wrong usage: please specify at least one group {Common.sectionKeys}"
                raise ValueError( msg )

        else:
            msg = '%s: No such file or directory, or rule ID' % arg
            raise ValueError( msg )


    if forceDirs:
        logging.debug( 'check directories: %s', forceDirs )
        cr.setDirs( forceDirs )

    if forceFiles:
        logging.debug( 'check files: %s', forceFiles )
        cr.setFiles( forceFiles )

    if forceLevel:
        logging.debug( 'check level: %s', forceLevel )
        cr.setLevel( forceLevel )

    if forceGroups:
        logging.debug( 'check groups: %s', forceGroups )
        cr.setRulesForGroups( forceGroups )

    if forceRules:
        logging.debug( 'check rules: %s', forceRules )
        cr.setRules( forceRules )
        cr.showSummary( False )
    else:
        cr.showSummary( True )


def _runPatchSystemGUI():
    logging.info( 'starting zen update' )

    from ToolBOSCore.CIA import PatchSystemGUI

    PatchSystemGUI.run()


def _runCheckRoutineDialog():
    from ToolBOSCore.ZenBuildMode    import QtPackageModel
    from ToolBOSCore.SoftwareQuality import CheckRoutineDialog

    logging.info( 'starting software quality check GUI' )

    projectRoot = os.getcwd()

    model = QtPackageModel.BSTPackageModel()
    model.open( projectRoot )

    CheckRoutineDialog.run( model )


def _runZenBuildModeGUI():
    from ToolBOSCore.ZenBuildMode import MainWindow

    logging.info( 'starting zen build mode' )

    projectRoot = os.getcwd()
    MainWindow.MainWindow( projectRoot ).main()


def _showAvailableTemplates():
    """
        Lists all available templates on the console.
    """
    from ToolBOSCore.Packages import PackageCreator


    print( '' )
    print( '\nAvailable templates:' )
    print( '--------------------\n' )

    for template in PackageCreator.getTemplatesAvailable():
        print( '  %s' % template )

    print( '\n\nExample usage:' )
    print( '--------------\n' )

    print( "<template>       -- specifies the type of package to be created" )
    print( "<packageName>    -- descriptive name of new software project" )
    print( "<packageVersion> -- version number, e.g.:" )
    print( "                    0.1 = initial development" )
    print( "                    1.0 = first release" )
    print( "                    1.1 = minor update" )
    print( "                    2.0 = major change\n" )

    print( "BST.py -n <template> <packageName> <packageVersion>" )
    print( "e.g.:" )
    print( "BST.py -n C_Library MyPackage 0.1\n" )

    print( "This will result in the following directory structure:" )
    print( "MyPackage/" )
    print( "└── 1.0" )
    print( "    ├── bin" )
    print( "    ├── CMakeLists.txt" )
    print( "    ├── doc" )
    print( "    ├── examples" )
    print( "    ├── src" )
    print( "    │   ├── MyPackage.c" )
    print( "    │   └── MyPackage.h" )
    print( "    └── test\n" )


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


env = FastScript.getEnv( 'BST_BUILD_JOBS' )

if env:
    jobs = int( env )
else:
    jobs = 1

hostPlatform = getHostPlatform()


desc = 'The Build System Tools (BST.py) are used for various tasks ' \
       'dealing with compiling, installing and maintaining software ' \
       'packages. They are used as an abstraction layer to the ' \
       'underlying build system and utilities.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-a', '--all', action='store_true',
                    help='same as distclean, setup, build and test' )

argman.addArgument( '-B', '--build-type', default='Release',
                    help='build type: Release|Debug (default: Release)' )

argman.addArgument( '-b', '--build', action='store_true',
                    help='compile package' )

argman.addArgument( '-d', '--distclean', action='store_true',
                    help='remove all buildsystem-related files' )

argman.addArgument( '--deprecate', action='store_true',
                    help='mark a version of a package as deprecated' )

argman.addArgument( '--deprecate-all', action='store_true',
                    help='mark a whole package as deprecated' )

argman.addArgument( '-f', '--shellfiles', action='store_true',
                    help='generate install/{BashSrc,pkgInfo.py} etc.' )

argman.addArgument( '--flat', action='store_true', default=False,
                    help='create new-style (flat) package structures' )

argman.addArgument( '-i', '--install', action='store_true',
                    help='install package into global SIT' )

argman.addArgument( '-j', '--jobs', default=jobs, type=int,
                    help='run number of compile jobs in parallel (default: %d)' % jobs )

argman.addArgument( '-k', '--codecheck', action='store_true',
                    help='static source code analysis' )

argman.addArgument( '-l', '--list', action='store_true',
                    help='list all used env. variables + build settings' )

argman.addArgument( '-M', '--message', action='store', type=str, default='',
                    help='message for global installation and deprecation' )

argman.addArgument( '-m', '--doc', action='store_true',
                    help='make API documentation (HTML)' )

argman.addArgument( '-n', '--new', action='store_true',
                    help='create new package from template (see examples below)' )

argman.addArgument( '-p', '--platform', default=hostPlatform,
                    help='cross-compile for specified target platform ' + \
                          '("-p help" to list supported platforms)' )

argman.addArgument( '-q', '--quality', action='store_true',
                    help='run software quality checks' )

argman.addArgument( '-r', '--release', action='store_true',
                    help='create release tarball' )

argman.addArgument( '-s', '--setup', action='store_true',
                    help='setup/configure the package for being built' )

argman.addArgument( '-t', '--test', action='store_true' ,
                    help='run the unittest suite of the package' )

argman.addArgument( '-U', '--uninstall', action='store_true' ,
                    help='remove package from SIT' )

argman.addArgument( '-u', '--upgrade', action='store_true' ,
                    help='automatic upgrade (apply all available patches)' )

argman.addArgument( '-x', '--proxy', action='store_true',
                    help='install package into SIT-Proxy (sandbox)' )

argman.addArgument( '-y', '--yes', action='store_true',
                    help='reply "yes" to all prompts, f.i. run non-interactively' )

argman.addArgument( '-z', '--zen', action='store_true',
                    help='zen build mode (GUI)' )

argman.addExample( '%(prog)s                             # build (setup once + compile)' )
argman.addExample( '%(prog)s -avx                        # all + install into proxy (verbose)' )
argman.addExample( '%(prog)s -ai                         # all + install globally' )
argman.addExample( '%(prog)s -bv                         # build in verbose mode' )
argman.addExample( '%(prog)s /path/to/sourcetree         # out-of-tree build' )
argman.addExample( '%(prog)s -p help                     # show cross-compile platforms' )
argman.addExample( '%(prog)s -p windows-amd64-vs2017     # cross-compile for Windows' )
argman.addExample( '%(prog)s -n                          # create new packages (GUI-version)' )
argman.addExample( '%(prog)s -n help                     # show available templates' )
argman.addExample( '%(prog)s -n --flat C_Library Foo 1.0 # create new-style C library "Foo"' )
argman.addExample( '%(prog)s -q                          # run quality checks (configured for this package)' )
argman.addExample( '%(prog)s -q --all                    # run all quality checks' )
argman.addExample( '%(prog)s -q src C01 C02 C03          # run specified checks on "src" only' )
argman.addExample( '%(prog)s -q sqLevel=advanced         # check with specified quality level' )
argman.addExample( '%(prog)s -q group=GEN,PY             # check only rules for GEN & PY group' )
argman.addExample( '%(prog)s -u                          # check for updates / apply patches' )
argman.addExample( '%(prog)s --uninstall                 # remove package from SIT' )
argman.addExample( '%(prog)s --deprecate                 # deprecate this package' )
argman.addExample( '%(prog)s --deprecate Foo/Bar/1.0     # deprecate specified package' )

argman.setAllowUnknownArgs( True )

args          = vars( argman.run() )
unhandled     = argman.getUnhandledArguments()
noArgs        = len( sys.argv ) == 1            # sys.argv[0] == /path/to/BST.py

allTargets    = args['all']
build         = args['build']
buildType     = args['build_type']
codecheck     = args['codecheck']
distclean     = args['distclean']
deprecate     = args['deprecate']
deprecate_all = args['deprecate_all']
documentation = args['doc']
flatStyle     = args['flat']
globalInstall = args['install']
jobs          = args['jobs']
listEnv       = args['list']
message       = args['message']
new           = args['new']
platform      = args['platform']
proxyInstall  = args['proxy']
quality       = args['quality']
release       = args['release']
shellfiles    = args['shellfiles']
setup         = args['setup']
test          = args['test']
uninstall     = args['uninstall']
upgrade       = args['upgrade']
verbose       = args['verbose']
yes           = args['yes']
zen           = args['zen']

sourceTree    = None
binaryTree    = None
outOfTree     = False

# proxy- and global-installations are mutually exclusive
if globalInstall and proxyInstall:
    msg = '"--install" and "--proxy" cannot be used together'
    logging.error( msg )
    sys.exit( -1 )


#----------------------------------------------------------------------------
# Main
#----------------------------------------------------------------------------


if yes:
    FastScript.setEnv( 'MAKEFILE_FASTINSTALL', 'TRUE' )


if message:
    FastScript.setEnv( 'MAKEFILE_GLOBALINSTALLREASON', message )


try:

    if platform == 'help':
        from ToolBOSCore.Platforms.CrossCompilation import getSwitchEnvironmentList

        candidates = getSwitchEnvironmentList( hostPlatform )
        Any.requireIsList( candidates )

        if not candidates:
            logging.info( 'No cross-compilation from %s hosts implemented :-(', hostPlatform )
        else:
            print( '\nSupported cross-compilation platforms on %s hosts:\n' % hostPlatform )
            for candidate in candidates:
                print( ' * %s' % candidate )
            print( '\n' )

        sys.exit( 0 )


    # if all arguments are False (just calling "BST.py"), fallback to
    # default operation (compile, auto-detect if configure is needed)

    if not any ( [ allTargets, build, codecheck, deprecate, deprecate_all,
                   distclean, documentation, globalInstall, listEnv, quality,
                   proxyInstall, release, setup, shellfiles, test, uninstall,
                   upgrade, zen ] ):
        build = True


    if not quality and unhandled:
        # if quality-check was not requested on commandline then assume
        # the last unhandled argument is source-tree location
        # ("out-of-tree build")
        candidate = unhandled[ -1 ]
        cwd       = os.getcwd()

        # check that unhandled[-1] is not by chance the script itself
        if candidate != sys.argv and Any.isDir( candidate ):
            sourceTree = os.path.abspath( candidate )
            binaryTree = os.path.abspath( os.getcwd() )

            # if "." etc. are used --> treat as in-tree build
            if sourceTree == binaryTree:
                sourceTree = None
                binaryTree = None
            else:
                logging.info( 'source tree: %s', sourceTree )
                logging.info( 'binary tree: %s', binaryTree )
                outOfTree = True



    # When using out-of-tree builds recycle the 'bst' object so
    # that the user does not need to pass the source-tree location
    # all the time

    bstCache = 'bstCache.dill'

    try:
        # this file will only be present if we perform out-of-tree
        # builds and calling BST.py again, however if user explicitly
        # requested "-s|--setup" then we do not recycle it
        #
        # as shortcut we throw an exception which is caught below
        if setup:
            raise AssertionError( 'skipped recycling cachefile' )


        if os.path.exists( bstCache ):

            FastScript.tryImport( 'dill' )
            import dill

            try:
                f = open( bstCache, 'rb' )
                bst = dill.load( f )
                f.close()
            except EOFError as details:
                raise FileNotFoundError( details )
            except dill.UnpicklingError as e:
                logging.warning( 'unable to deserialize %s: %s', bstCache, e )
                logging.warning( 'ignoring cache file!' )
                raise IOError( e )

            logging.debug( '%s found', bstCache )

        else:
            raise FileNotFoundError( '%s: No such file' % bstCache )

    except ( AssertionError, KeyError, IOError ):

        logging.debug( 'initializing Build System Tools' )
        bst = BuildSystemTools.BuildSystemTools()

        if outOfTree:
            bst.setSourceAndBinaryTree( sourceTree, binaryTree )

            try:
                FastScript.tryImport( 'dill' )
                import dill

                from ToolBOSCore.External.atomicfile import AtomicFile

                with AtomicFile(bstCache, 'wb') as f:
                    dill.dump( bst, f )
            except ( IOError, OSError ) as details:
                logging.debug( 'unable to create %s', bstCache )
                logging.debug( details )


    bst.setBuildType( buildType )
    bst.setParallelJobs( jobs )
    bst.setTargetPlatform( platform )


    if allTargets and not quality:
        distclean     = True
        setup         = True
        build         = True
        test          = True
        documentation = True


    if uninstall:
        if proxyInstall:
            cleanGlobalInstallation = False
        else:
            cleanGlobalInstallation = True

        if not bst.uninstall( cleanGlobalInstallation ):
            sys.exit( -6 )


    if distclean:
        bst.distclean()


    if new:
        status = _createPackage( unhandled, flatStyle )
        sys.exit( 0 if status else -5 )


    if zen:
        FastScript.tryImport( 'PyQt5' )

        if upgrade:
            _runPatchSystemGUI()

        elif quality:
            _runCheckRoutineDialog()

        else:
            _runZenBuildModeGUI()

        sys.exit( 0 )


    if setup or noArgs:
        if not bst.configure():
            sys.exit( -2 )


    if upgrade:
        from ToolBOSCore.CIA.PatchSystem import PatchSystem

        patcher = PatchSystem()
        patcher.run()


    if build or noArgs:
        if not bst.compile():
            sys.exit( -3 )


    if shellfiles:
        bst.makeShellfiles()


    if test:
        if not bst.runUnittest():
            sys.exit( -4 )


    if documentation:
        bst.makeDocumentation()


    if codecheck:
        from ToolBOSCore.Tools import Klocwork

        logging.info( 'analyzing project structure and build options' )
        Klocwork.createLocalProject()

        logging.info( 'performing static source code analysis' )
        Klocwork.codeCheck( logToConsole=True )


    if quality:
        from ToolBOSCore.SoftwareQuality import CheckRoutine

        sqArgs = unhandled

        try:
            # ensure that script-name does not appear in this list
            sqArgs.remove( sys.argv[0] )
        except ValueError:
            pass

        cr = CheckRoutine.CheckRoutine()

        if unhandled:
            _parseSqArgs( cr, unhandled )

        # exclude 3rd-party content from being checked:
        cr.excludeDir( './external' )
        cr.excludeDir( './3rdParty' )

        if allTargets:
            # ignore all the sqOptOut rules and flags and
            # perform SQ checks for all the available rules
            cr.setup( False )
        else:
            # consider the rules and level set in the pkgInfo
            cr.setup()
        cr.run()

        if cr.overallResult() is not True:
            sys.exit( -5 )


    if proxyInstall:
        if os.path.isfile( 'installHook.sh' ):
            logging.error( '3rd party packages do not support Proxy-SIT installation :-/' )
            sys.exit( -7 )

        else:
            bst.proxyInstall()
            sys.exit( 0 )


    if globalInstall:
        sys.exit( 0 if bst.install() else -1 )


    if release:
        if os.path.isfile( 'installHook.sh' ):
            logging.error( '3rd party packages do not support generating tarballs :-/' )
            sys.exit( -7 )

        else:
            bst.makeTarball()
            sys.exit( 0 )

    if deprecate or deprecate_all:
        from ToolBOSCore.Packages.ProjectProperties import setDeprecated

        if unhandled:
            canonicalPath = unhandled[-1]
        else:
            canonicalPath = bst.getCanonicalPath()
        if not setDeprecated( canonicalPath,
                              allVersions=deprecate_all,
                              message=message ):
            sys.exit( -8 )

        sys.exit( 0 )

except KeyboardInterrupt:
    # user pressed <Ctrl+C>
    print( '' )
    logging.info( 'cancelled' )
    sys.exit( -1 )

except ( AssertionError, EnvironmentError, RuntimeError, SyntaxError,
         ValueError ) as details:

    # e.g. unsupported cross-compilation
    logging.error( f'{details.__class__.__name__}: {details}' )

    # show stacktrace in verbose mode
    if Any.getDebugLevel() >= 5:
        raise

    sys.exit( -1 )


sys.exit( 0 )


# EOF
