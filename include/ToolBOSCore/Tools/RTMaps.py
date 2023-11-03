#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  RTMaps interface
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
import re
import os

from ToolBOSCore.Packages            import ProjectProperties
from ToolBOSCore.Platforms.Platforms import getPlatformNames
from ToolBOSCore.Storage             import ProxyDir, SIT
from ToolBOSCore.Util                import Any, FastScript


def getIndexBaseDir( sitProxyPath=None ):
    """
        Returns the path to the user's index base directory.

        If 'sitProxyPath' is omitted then the current Proxy-SIT is used.
    """
    if sitProxyPath is None:
        sitProxyPath = SIT.getPath()

    ProxyDir.requireIsProxyDir( sitProxyPath )

    indexBaseDir = os.path.join( sitProxyPath, 'Modules', 'Index' )

    return indexBaseDir


def isInstalled( sitRootPath ):
    """
        Returns a boolean whether or not RTMaps is available in SIT.
    """
    Any.requireIsDir( sitRootPath )

    installBaseDir = os.path.join( sitRootPath, 'External', 'RTMaps' )

    return os.path.exists( installBaseDir )


def getVersionsAvailable( sitRootPath ):
    """
        Returns a list of strings with the RTMaps versions installed
        in the specified SIT, e.g. ['4.20', '4.21']
    """
    Any.requireIsDir( sitRootPath )

    installBaseDir = os.path.join( sitRootPath, 'External', 'RTMaps' )
    Any.requireIsDirNonEmpty( installBaseDir )

    resultList = FastScript.getDirsInDir( installBaseDir )
    Any.requireIsListNonEmpty( resultList )

    return resultList


def updateComponentIndex( sitRootPath, sitProxyPath, dryRun ):
    """
        Cleans the index directory and creates all symlinks from scratch.
    """
    Any.requireIsDir( sitRootPath )
    Any.requireIsDir( sitProxyPath )
    Any.requireIsBool( dryRun )

    ProxyDir.requireIsProxyDir( sitProxyPath )

    indexBaseDir = getIndexBaseDir( sitProxyPath )

    # We would like to start with a fresh indexBaseDir, however cannot delete
    # it because it also contains the DTBOS *.def files. Hence we only remove
    # subdirectories (corresponding to the RTMaps versions) within this
    # directories and keep *.def files as they are. See TBCORE-974).
    #
    #FastScript.remove( indexBaseDir )

    for subDir in FastScript.getDirsInDir( indexBaseDir ):
        path = os.path.join( indexBaseDir, subDir )
        FastScript.remove( path )


    for version in getVersionsAvailable( sitRootPath ):
        dstDir = os.path.join( indexBaseDir, version )
        logging.debug( 'mkdir %s', dstDir )

        if not dryRun:
            FastScript.mkdir( dstDir )

    logging.debug( 'updating RTMaps component index...' )

    registerDistributionPackages( sitRootPath, sitProxyPath, dryRun )
    registerNormalPackages( sitRootPath, dryRun )
    registerNormalPackages( sitProxyPath, dryRun )


def registerNormalPackages( sitPath, dryRun=False ):
    """
        Searches the SIT for RTMaps packages and invokes
        registerHondaPackage() for each of them.
    """
    Any.requireIsDir( sitPath )
    Any.requireIsBool( dryRun )

    sitProxyPath = SIT.getPath()
    ProxyDir.requireIsProxyDir( sitProxyPath )

    searchBaseDir = os.path.join( sitPath, 'Modules', 'RTMaps' )
    # Any.requireIsTextNonEmpty( searchBaseDir ) # dir. might not exist
    Any.requireIsTextNonEmpty( searchBaseDir )

    indexBaseDir  = getIndexBaseDir( sitProxyPath )
    # Any.requireIsDir( indexBaseDir )           # dir. might not exist
    Any.requireIsTextNonEmpty( indexBaseDir )

    logging.debug( 'SIT path:       %s', sitPath )
    logging.debug( 'search basedir: %s', searchBaseDir )
    logging.debug( 'index basedir:  %s', indexBaseDir )


    # find *.pck files
    logging.debug( 'scanning %s...', searchBaseDir )
    pckPaths = FastScript.findFiles( searchBaseDir, ext='.pck' )
    Any.requireIsList( pckPaths )

    logging.debug( 'found HORP files:' )

    for pckPath in sorted( pckPaths ):
        logging.debug( f'  * {pckPath}' )
    logging.debug( '' )

    # process each *.pck file (tokenize path and create symlink)
    for pckPath in pckPaths:
        logging.debug( f'processing {pckPath}' )

        # the *.pck file is located on the 3rd subdirectory level relative
        # to the installRoot, so compute the installRoot based on this
        tokens         = pckPath.split( os.path.sep )
        installRoot    = os.path.sep.join( tokens[:-3] )
        package        = SIT.strip( installRoot )

        Any.requireIsDir( installRoot )
        Any.requireIsTextNonEmpty( package )

        try:
            registerNormalPackage( package, sitProxyPath, indexBaseDir, dryRun )
        except ValueError as e:
            logging.error( e )


def registerNormalPackage( package, sitProxyPath=None, indexBaseDir=None, dryRun=False ):
    """
        Creates a symlink to the *.pck file of 'package' within the RTMaps
        index.

        RTMAPS_VERSION is taken from the dependency list of the package.
    """
    if sitProxyPath is None:
        sitProxyPath = SIT.getPath()

    if indexBaseDir is None:
        indexBaseDir = getIndexBaseDir( sitProxyPath )

    logging.debug( f'processing package: {package}' )

    ProjectProperties.requireIsCanonicalPath( package )
    Any.requireIsDir( sitProxyPath )
    Any.requireIsDir( indexBaseDir )
    Any.requireIsBool( dryRun )

    platformList   = getPlatformNames()
    packageName    = ProjectProperties.getPackageName( package )
    packageVersion = ProjectProperties.getPackageVersion( package )
    versionTokens  = ProjectProperties.splitVersion( packageVersion )
    majorVersion   = int( versionTokens[0] )
    minorVersion   = int( versionTokens[1] )
    installRoot    = os.path.join( sitProxyPath, package )

    Any.requireIsListNonEmpty( platformList )
    Any.requireIsTextNonEmpty( packageName )
    Any.requireIsTextNonEmpty( packageVersion )
    Any.requireIsDir( installRoot )


    deps = ProjectProperties.getDependencies( package )
    try:
        Any.requireIsListNonEmpty( deps )
    except AssertionError:
        logging.debug( 'empty list of dependencies in RTMaps package is unplausible' )
        msg = "%s: unable to retrieve dependencies, please check SIT installation" % package
        raise ValueError( msg )

    expr = re.compile( r'^sit://External/RTMaps/(\d+\.\d+)' )


    # detect RTMaps version used by package
    rtmapsVersion = ''

    for dep in deps:
        tmp = expr.match( dep )

        if tmp:
            rtmapsVersion = tmp.group(1)
            break

    Any.requireIsTextNonEmpty( rtmapsVersion )
    logging.debug( '%s depends on RTMaps %s', package, rtmapsVersion )


    libDir   = os.path.join( installRoot, 'lib' )
    pckFiles = FastScript.findFiles( libDir, ext='.pck' )

    Any.requireMsg( len(pckFiles) > 0,
                    package + ": No *.pck file found, forgot to compile?" )

    for relPath in pckFiles:
        pckFileName = os.path.basename( relPath )
        pckPackage  = os.path.splitext( pckFileName )[0]
        pckFileExt  = os.path.splitext( pckFileName )[1]

        logging.debug( 'registering %s', pckPackage )

        for platform in platformList:
            pckPath = os.path.join( libDir, platform, pckFileName )
            dstDir  = os.path.join( indexBaseDir, rtmapsVersion, platform )

            if os.path.exists( pckPath ):
                symlinkFile = '%s_%d.%d%s' % ( pckPackage, majorVersion,
                                                minorVersion, pckFileExt )
                symlinkPath = os.path.join( dstDir, symlinkFile )
                target      = pckPath

                FastScript.link( target, symlinkPath, dryRun )


def registerDistributionPackages( sitRootPath, sitProxyPath, dryRun=False ):
    """
        Searches the SIT for packages shipped with RTMaps itself
        (by Intempora).
    """
    Any.requireIsDir( sitRootPath )
    ProxyDir.requireIsProxyDir( sitProxyPath )
    Any.requireIsBool( dryRun )

    platformList   = getPlatformNames()
    rtmapsVersions = getVersionsAvailable( sitRootPath )

    Any.requireIsListNonEmpty( platformList )
    Any.requireIsListNonEmpty( rtmapsVersions )

    installBaseDir = os.path.join( sitRootPath, 'External', 'RTMaps' )

    indexBaseDir   = getIndexBaseDir( sitProxyPath )
    # Any.requireIsDir( indexBaseDir )           # dir. might not exist
    Any.requireIsTextNonEmpty( indexBaseDir )


    # find *.pck files shipped with RTMaps
    for rtmapsVersion in rtmapsVersions:
        logging.debug( 'searching for packages shipped with RTMaps %s',
                       rtmapsVersion )

        for platform in platformList:
            searchPath = os.path.join( installBaseDir, rtmapsVersion, platform,
                                       'packages' )

            pckPaths   = FastScript.findFiles( searchPath, ext='.pck' )
            Any.requireIsList( pckPaths )

            for pckPath in pckPaths:
                pckFile = os.path.basename( pckPath )
                Any.requireIsTextNonEmpty( pckFile )

                symlink = os.path.join( indexBaseDir, rtmapsVersion,
                                        platform, pckFile )
                target  = pckPath

                FastScript.link( target, symlink, dryRun )


def getIndexFileName( canonicalPath ):
    """
        Returns the RTMaps index filename for the package.

        Example:  'Horp_ToolBOS_1.0.pck'
    """
    ProjectProperties.requireIsCanonicalPath( canonicalPath )

    tmp    = ProjectProperties.splitPath( canonicalPath )
    result = '%s_%s.pck' % ( tmp[1], tmp[2] )
    Any.requireIsTextNonEmpty( result )

    return result


def getIndexFilePath_relSIT( canonicalPath, rtmapsVersion, platform ):
    """
        Returns a path to the *.pck index filename for the package,
        relative to ${SIT}.

        Example:  package = 'Modules/BBCM/InputOutput/UltimaTest/3.1'

    """
    ProjectProperties.requireIsCanonicalPath( canonicalPath )
    Any.requireIsTextNonEmpty( rtmapsVersion )
    Any.requireIsTextNonEmpty( platform )

    result = os.path.join( 'Modules/Index', rtmapsVersion, platform,
                           getIndexFileName( canonicalPath ) )

    Any.requireIsTextNonEmpty( result )

    return result


# EOF
