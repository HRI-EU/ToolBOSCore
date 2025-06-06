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
from ToolBOSCore.Util                import ArgsManagerV2, FastScript


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
                    help='message for deprecation' )

argman.addArgument( '-m', '--doc', action='store_true',
                    help='make API documentation (HTML)' )

argman.addArgument( '-p', '--platform', default=hostPlatform,
                    help='cross-compile for specified target platform ' + \
                          '("-p help" to list supported platforms)' )

argman.addArgument( '-q', '--quality', action='store_true',
                    help='[REMOVED]' )

argman.addArgument( '-r', '--release', action='store_true',
                    help='create release tarball' )

argman.addArgument( '-s', '--setup', action='store_true',
                    help='setup/configure the package for being built' )

argman.addArgument( '-t', '--test', action='store_true' ,
                    help='run the unittest suite of the package' )

argman.addArgument( '-U', '--uninstall', action='store_true' ,
                    help='remove package from SIT' )

argman.addArgument( '-x', '--proxy', action='store_true',
                    help='install package into SIT-Proxy (sandbox)' )

argman.addArgument( '-y', '--yes', action='store_true',
                    help='reply "yes" to all prompts, f.i. run non-interactively' )

argman.addArgument( '-z', '--zen', action='store_true',
                    help='[REMOVED]' )

argman.addExample( '%(prog)s                             # build (setup once + compile)' )
argman.addExample( '%(prog)s -avx                        # all + install into proxy (verbose)' )
argman.addExample( '%(prog)s -ai                         # all + install globally' )
argman.addExample( '%(prog)s -bv                         # build in verbose mode' )
argman.addExample( '%(prog)s /path/to/sourcetree         # out-of-tree build' )
argman.addExample( '%(prog)s -p help                     # show cross-compile platforms' )
argman.addExample( '%(prog)s -p windows-amd64-vs2017     # cross-compile for Windows' )
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
platform      = args['platform']
proxyInstall  = args['proxy']
quality       = args['quality']
release       = args['release']
shellfiles    = args['shellfiles']
setup         = args['setup']
test          = args['test']
uninstall     = args['uninstall']
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


try:

    if platform == 'help':
        from ToolBOSCore.Platforms.CrossCompilation import getSwitchEnvironmentList

        candidates = getSwitchEnvironmentList( hostPlatform )
        FastScript.requireIsList( candidates )

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
                   zen ] ):
        build = True


    if not quality and unhandled:
        # if quality-check was not requested on commandline then assume
        # the last unhandled argument is source-tree location
        # ("out-of-tree build")
        candidate = unhandled[ -1 ]
        cwd       = os.getcwd()

        # check that unhandled[-1] is not by chance the script itself
        if candidate != sys.argv and FastScript.isDir( candidate ):
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
                logging.warning( 'unable to parse %s: %s', bstCache, e )
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

                with open( bstCache, 'wb' ) as f:
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


    if zen:
        logging.error( 'Feature was removed' )
        sys.exit( -9 )


    if setup or noArgs:
        if not bst.configure():
            sys.exit( -2 )


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
        logging.error( 'Feature was removed' )
        sys.exit( -9 )


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
    if FastScript.getDebugLevel() >= 5:
        raise

    sys.exit( -1 )


sys.exit( 0 )


# EOF
