# -*- coding: utf-8 -*-
#
#  functions to create, scan and query the Software Installation Tree (SIT)
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
import re
import shutil

from ToolBOSCore.Util import FastScript
from ToolBOSCore.Util import Any

parentLink = 'parentTree'


def getDefaultRootBaseDir():
    """
        Default location where all the Software Installation Tree's builds
        and LTS directories can be found inside.
    """
    return '/hri/sit'


def getDefaultLTSPath():
    """
        Default location of the Long-term stable/supported SIT part.
    """
    return os.path.join( getDefaultRootBaseDir(), 'LTS' )


def getDefaultProxyBaseDir():
    """
        Default location where all the Proxy-SIT's are located.
    """
    return os.path.expanduser( '~/.HRI/sit' )


#----------------------------------------------------------------------------
# Bootstrapping a new software installation tree
#----------------------------------------------------------------------------


def getMinRequirements():
    """
        Returns a list of essential packages needed for a minimalistic
        software installation tree (SIT).

        Opposed to getBuildRequirements() this only contains the minimal
        requirements for executing / distributing software.
    """
    from ToolBOSCore.Settings.ToolBOSConf import getConfigOption

    result = getConfigOption( 'SIT_bootstrapMin' )

    Any.requireIsListNonEmpty( result )
    return result


def getBuildRequirements():
    """
        Returns a list of essential packages needed for a minimalistic
        software installation tree (SIT).

        Opposed to getMinRequirements() this contains everything needed to
        build software packages.
    """
    from ToolBOSCore.Settings.ToolBOSConf import getConfigOption

    result = getConfigOption( 'SIT_bootstrapFull' )

    Any.requireIsListNonEmpty( result )
    return result


def copyBasePackages( srcRoot, dstRoot, packageList, verbose = True,
                      ignore = None, resolveLTS = False, cacheDir = None ):
    """
        Copies all packages in the 'packageList' from the current srcRoot
        into dstRoot.

        Use the 'verbose' parameter to see/suppress a little progress
        information.

        'ignore' might be a callable that will be given to shutil.copytree()
        for filtering-out undesired content.

        'resolveLTS' indicates whether symlinks to LTS packages
        shall be resolved:
            True  = copy content of LTS packages (resolve symlinks)
            False = keep LTS symlinks as they are

        If 'cacheDir' points to a SIT-like directory, packages aren't
        copied but instead linked there to speed-up, e.g. while debugging.
    """
    Any.requireIsDir( srcRoot )
    Any.requireIsDir( dstRoot )
    Any.requireIsBool( verbose )
    Any.requireIsBool( resolveLTS )

    if ignore is not None:
        Any.requireIsCallable( ignore )

    if cacheDir is not None:
        Any.requireIsDirNonEmpty( cacheDir )

    for package in packageList:

        if cacheDir:
            symlink = os.path.join( dstRoot, package )
            target  = os.path.join( cacheDir, package )

            FastScript.link( target, symlink )

        else:
            src = os.path.join( srcRoot, package )
            dst = os.path.join( dstRoot, package )

            try:
                _copyBasePackage( src, dst, verbose, ignore, resolveLTS )
            except FileNotFoundError as e:
                logging.error( e )
                logging.error( f'Error copying package {package}' )


def _copyBasePackage( src, dst, verbose, ignore = None, resolveLTS = None ):
    """
        Worker function which copies a particular package, passing the
        'ignore'-callback to the underlying shutil.copytree() function.
    """
    if verbose:
        logging.info( 'copying %s', strip( src ) )

    if os.path.islink( src ):

        # make packageName directory
        try:
            FastScript.mkdir( os.path.dirname( dst ) )
        except OSError:     # may happen upon multi-thread race condition
            pass

        # distinguish if the link points to a patchlevel or into LTS
        target = os.readlink( src )

        if target.find( os.sep + 'LTS' + os.sep ) > 0:
            _copyBasePackage_linkToLTS( src, dst, ignore, resolveLTS )
        else:
            _copyBasePackage_linkToPatchlevel( src, dst, ignore )

    elif os.path.isdir( src ):
        # don't follow symlinks, keep them as they are
        shutil.copytree( src, dst, True, ignore )
    else:
        shutil.copy( src, dst )


def _copyBasePackage_linkToLTS( src, dst, ignore, resolveLTS ):
    target = os.readlink( src )

    if resolveLTS:
        shutil.copytree( target, dst, True, ignore )
    else:
        # copy just the link
        linkname = dst

        try:
            os.symlink( target, linkname )
        except OSError as details:
            if details.errno != 17:         # 17 == "File exists" --> ignore
                raise


def _copyBasePackage_linkToPatchlevel( src, dst, ignore ):
    # first copy the link
    target   = os.readlink( src )
    linkname = dst

    try:
        os.symlink( target, linkname )
    except OSError as details:
        if details.errno != 17:         # 17 == "File exists" --> ignore
            raise

    # then copy the linked content
    realSrc = os.path.realpath( src )
    realDst = os.path.join( os.path.dirname( dst ), os.path.basename( realSrc ) )

    try:
        # don't follow symlinks, keep them as they are
        shutil.copytree( realSrc, realDst, True, ignore )
    except OSError as details:
        if details.errno != 17:         # 17 == "File exists" --> ignore
            logging.warning( details )


def copyModuleIndex( srcRoot, dstRoot ):
    """
        Copies all <srcDIT>/Modules/Index/*.def and <srcDIT>/Modules/Index/*.py files to
                   <dstSIT>/Modules/Index/
    """
    Any.requireIsDir( srcRoot )
    Any.requireIsDir( dstRoot )

    srcDir = os.path.join( srcRoot, 'Modules', 'Index' )
    dstDir = os.path.join( dstRoot, 'Modules', 'Index' )

    # For the case that srcRoot is an SIT proxy: Some people do not have
    # any files in their Index directory, furthermore the directory could
    # be entirely missing if never a BBCM had been installed into the
    # user's proxy
    #
    # Any.requireIsDirNonEmpty( srcDir )
    FastScript.mkdir( dstDir )

    for srcFile in FastScript.getFilesInDir( srcDir ):
        if srcFile.endswith( ".def" ) or srcFile.endswith( ".py" ):

            fileName = os.path.basename( srcFile )
            srcPath  = os.path.join( srcDir, fileName )
            dstPath  = os.path.join( dstDir, fileName )

            FastScript.copy( srcPath, dstPath )


def bootstrap( dstPath, buildSDK = False, verbose = True, ignore = None,
               resolveLTS = False, cacheDir = None ):
    """
        Creates a new software installation tree by copying the most basic
        packages from the current tree. This will be sufficient to execute
        ToolBOS applications.

        If 'buildSDK' is set to True, also packages for compiling / building
        software will be copied into the dstPath.

        'ignore' might be a callable that will be given to shutil.copytree()
        for filtering-out undesired content.

        'resolveLTS' indicates whether symlinks to LTS packages
        shall be resolved:
            True  = copy content of LTS packages (resolve symlinks)
            False = keep LTS symlinks as they are
    """
    Any.requireIsTextNonEmpty( dstPath )
    Any.requireIsBool( buildSDK )
    Any.requireIsBool( verbose )
    Any.requireIsBool( resolveLTS )

    if ignore is not None:
        Any.requireIsCallable( ignore )

    if cacheDir is not None:
        Any.requireIsDirNonEmpty( cacheDir )

    srcRoot = getRootPath()
    dstRoot = dstPath

    # Any.RequireIsDir( srcRoot )  # not useful error reporting
    if not os.path.isdir( srcRoot ):
        msg = "%s: Source SIT path does not exist (can't bootstrap from there)" % srcRoot
        raise RuntimeError( msg )

    FastScript.mkdir( dstRoot )       # create if it does not exist, yet

    if buildSDK:
        packageList = getBuildRequirements()
    else:
        packageList = getMinRequirements()

    Any.requireIsListNonEmpty( packageList )
    copyBasePackages( srcRoot, dstRoot, packageList, verbose, ignore,
                      resolveLTS, cacheDir )

    # make directory for component description files (*.def)
    modulesDir = os.path.join( dstRoot, 'Modules' )
    indexDir   = os.path.join( dstRoot, 'Modules', 'Index' )
    FastScript.mkdir( indexDir )  # will implicitely create the modulesDir

    os.chmod( modulesDir, 0o0777 )
    os.chmod( indexDir,   0o0777 )


def switch( dstPath ):
    """
        This function internally resets all variables etc. so that further
        calls to SIT.getPath() or so return the correct directory name.
    """
    FastScript.setEnv( 'SIT',             dstPath )
    FastScript.setEnv( 'SIT_VERSION',     os.path.basename( dstPath ) )


#----------------------------------------------------------------------------
# get SIT paths
#----------------------------------------------------------------------------


def getVersion():
    """
        Returns the "version" of the Software Installation Tree, which
        typically has a temporal relation e.g. "oldstable", "latest" or
        "testing".
    """
    version = FastScript.getEnv( 'SIT_VERSION' )

    # fallback to default if none is set
    if not version:
        version = 'latest'

    return version


def getDefaultRootPath():
    """
        Returns the fallback location where the Root-SIT is typically
        located unless specified differently.
    """
    return os.path.join( getDefaultRootBaseDir(), getVersion() )


def getDefaultProxyPath():
    """
        Returns the default location for the user's SIT sandbox,
        which is typically under ${HOME}/.HRI/something
    """
    return os.path.join( getDefaultProxyBaseDir(), getVersion() )


def getPath():
    """
        Returns the software installation tree path, with several
        fall-back tiers:

        1)  use what the environment variable 'SIT' points to
            (without check if this really exists and/or is a valid SIT)

        2)  check if we find a sandbox ("Proxy SIT")

        3)  fallback to <baseDir>/<version> regardless if it exists
    """
    envPath = FastScript.getEnv( 'SIT' )

    if envPath:
        return envPath

    proxyPath = getDefaultProxyPath()

    if os.path.isdir( proxyPath ):
        return proxyPath

    return getDefaultRootPath()


def getParentPath( sitPath = '' ):
    """
        In case of cascaded proxies returns the 'parent' directory of the
        current SIT, if SIT points to a sandbox ("proxy directory").

        To find the top-most "root" SIT use SIT.getRootPath() instead.
    """
    if sitPath == '':
        sitPath = getPath()

    linkName = os.path.join( sitPath, parentLink )

    if os.path.islink( linkName ):
        return os.readlink( linkName )
    else:
        return sitPath


# Attention: Do not set sitPath=getPath() here because this would be only
#            executed once at module load time and not be updated upon an
#            SIT.switch().
def getRootPath( sitPath = '' ):
    """
        Returns the 'parent' directory of the current SIT, if SIT points
        to a sandbox ("proxy directory").

        If SIT is not a proxy directory (e.g. already a "root SIT"), the
        return value will be 'sitPath' for convenience.
    """
    if sitPath == '':
        sitPath = getPath()

    linkName = os.path.join( sitPath, parentLink )

    if os.path.islink( linkName ):
        return os.path.realpath( linkName )
    else:
        return sitPath


def getBaseDir( sitRootPath = '' ):
    """
        Returns the location where all the Software Installation Trees
        are located.

        If you pass an existing SIT root path, its dirname will be returned,
        otherwise the default SIT location.
    """
    if sitRootPath == '':
        sitRootPath = getRootPath()

    return os.path.dirname( sitRootPath )


def getIdentifier( sitRootPath = getDefaultRootPath() ):
    """
        Returns the SIT build identifier in the form 'YYYY-MM-DD_HH-MM-SS'
        which corresponds to the last part of the resolved SIT path, e.g.:

          getIdentifier( '/hri/sit/latest' )

        at the time of this writing returned '2012-01-05_16-06-39'.
    """
    Any.requireIsTextNonEmpty( sitRootPath )

    return os.path.basename( os.path.realpath( sitRootPath ) )


def expandSIT( string ):
    """
        Tries to replace all known SIT placeholders with the actual SIT path.
    """
    string = string.replace( 'sit://', getPath() + '/' )
    return FastScript.expandVar( string, 'SIT' )


def collapseSIT( string ):
    """
        Returns all computable values of SIT with an ${SIT} placeholder.
    """
    # if existing, replace the path where ${SIT}/parentTree points to
    envValue = FastScript.getEnv( 'SIT' )
    linkName = os.path.join( envValue, parentLink )

    try:
        linkTarget = os.readlink( linkName )
        tmp = string.replace( linkTarget + '/', '' )
    except( OSError,               # probably has no such link
            AttributeError ):      # os.readlink not available on Windows
        tmp = string

    tmp = FastScript.collapseVar( tmp, 'SIT' )

    return tmp


def strip( string ):
    """
        Removes all known placeholders or computable values of SIT
        from the string, so useful to get "canonical" path names.

        Supporting both forward-slashes (Linux/POSIX) and
        backslashes (Windows)
    """
    sitPath     = getPath()          # those two are equal if user has
    sitRootPath = getRootPath()      # no Proxy-SIT configured

    tmp = collapseSIT( string )

    tmp = tmp.replace( '${SIT}/',          '' )
    tmp = tmp.replace( '${SIT}\\',         '' )
    tmp = tmp.replace( '${SIT}',           '' )
    tmp = tmp.replace( '%SIT%/',           '' )
    tmp = tmp.replace( '%SIT%\\',          '' )
    tmp = tmp.replace( '%SIT%',            '' )
    tmp = tmp.replace( 'sit://',           '' )
    tmp = tmp.replace( sitPath + '/',      '' )
    tmp = tmp.replace( sitPath + '\\',     '' )
    tmp = tmp.replace( sitRootPath + '/',  '' )
    tmp = tmp.replace( sitRootPath + '\\', '' )

    return tmp


#----------------------------------------------------------------------------
# Browse and query the Software Installation Tree
#----------------------------------------------------------------------------


def getProjects( path, keepPath = True, onError = None ):
    """
        Recursively searches for projects installed in the specified
        directory.

        If 'keepPath' is True, the specified "path" will be part of the
        strings returned. If False, only the part of the path behind 'path'
        will be returned, e.g.:

             getProjects( '/hri/sit/latest' )

             True:
                   [ '/hri/sit/latest/Libraries/Serialize/3.0', ... ]
             False:
                   [ 'Libraries/Serialize/3.0', ... ]

        You may pass a function callback that will be called upon errors,
        e.g. permission denied. This function needs to take a single
        path parameter. If omitted, an OSError will be raised upon errors.
    """
    Any.requireIsDir( path )

    path           = os.path.normpath( path )
    projectList    = []
    excludePattern = re.compile( r"(parentTree|^\d+\.\d+)|.svn" )
    criteria       = re.compile( r"^(\d+)\.(\d+)(.*)" )

    for directory in FastScript.getDirsInDirRecursive( path, excludePattern,
                                                       onError=onError ):
        for subDir in FastScript.getDirsInDir( directory, onError=FastScript.ignore ):

            if keepPath:
                pathToAdd = os.path.join( directory, subDir )
            else:
                pathToAdd = os.path.join( directory.replace( path + '/', '' ), subDir )

            if criteria.search( subDir ):
                projectList.append( pathToAdd )

    return projectList


def getProjectsWithErrorHandling( path, resultList ):
    """
        This is a tiny wrapper of 'getProjects()' which also prints some
        logging info and handles errors such as permission denied.

        The data will be appended to the provided resultList instead of
        using a return value. This allows using this function in a thread.
    """
    Any.requireIsDir( path )
    Any.requireIsList( resultList )

    logging.info( 'scanning %s...', path )

    resultList.extend( getProjects( path, keepPath=False,
                                    onError=FastScript.printPermissionDenied ) )

    Any.requireIsListNonEmpty( resultList )


def getCanonicalPaths( sitPath ):
    """
        Returns a sorted list of all installed packages
        (major.minor versions only).
    """
    from ToolBOSCore.Packages.ProjectProperties import isCanonicalPath

    Any.requireIsDir( sitPath )

    sitPackages = []
    getProjectsWithErrorHandling( sitPath, sitPackages )

    canonicalPaths = list( filter( isCanonicalPath, sitPackages ) )
    canonicalPaths.sort()

    return canonicalPaths


def getActiveRevision( sitPath, project ):
    """
        This function returns the currently installed patchlevel (SVN
        revision) of a project, by resolving the 2-digit symlinks.

            in root SIT:
            2.2 --> 2.2.500

            in proxy SIT:
            2.2 --> 2.2.501

        By providing a 'sitPath' URL you can query the SIT root directory
        or any SIT proxy directory, e.g.:

            globalRevision = getActiveRevision( sitRootPath, 'Libraries/Foo/1.0' )
            proxyRevision  = getActiveRevision( sitProxyPath, 'Libraries/Foo/1.0' )

            if proxyRevision != globalRevision:
                # inform user

        The function will return 'None' if the patchlevel number can't
        reliably be detected.
    """
    realpath   = os.path.realpath( os.path.join( sitPath, project ) )
    regexp     = re.compile( r"^(\d+)\.(\d+)\.(\d+)" )
    tmp        = regexp.search( os.path.basename( realpath ) )

    if tmp:
        return int( tmp.group( 3 ) )


#----------------------------------------------------------------------------
# Misc functions
#----------------------------------------------------------------------------


def makeCategoryWriteable( sitPath, project, groupName='hriall', mode=0o0775 ):
    """
        Changes the group and permissions of all directories between
        'sitPath' up to the project version. The project's main directory
        will also be group-writeable so that different developers could
        install different versions.

        Mind to provide an octal number 'mode'!
    """
    from ToolBOSCore.Packages import ProjectProperties

    Any.requireIsDir( sitPath )
    Any.requireIsTextNonEmpty( project )
    Any.requireIsTextNonEmpty( groupName )
    Any.requireIsIntNotZero( mode )  # <mode> must be an octal number
    ProjectProperties.requireIsCanonicalPath( project )


    # The current HRI-EU install procedure is implemented in a way that it always
    # attempts to change ownership of the category INCLUDING the SIT root
    # directory. Instead of fixing this there (time-consuming, error-prone) we
    # always set it here as a shortcut.
    FastScript.setGroupPermission( sitPath, groupName, mode )


    # cut off the project version
    tmp     = ProjectProperties.splitPath( project )
    mainDir = os.path.join( tmp[0], tmp[1] )
    tokens  = mainDir.split( os.sep )

    # the current path we are operating on with chmod+chgrp, starting from
    # sitPath
    curPath = sitPath

    # for each token in category do a chmod+chgrp
    for token in tokens:
        curPath = os.path.join( curPath, token )
        FastScript.setGroupPermission( curPath, groupName, mode )


def showStatistics():
    """
        Shows few numbers on current SIT such as number of packages.
    """
    from ToolBOSCore.Packages import ProjectProperties

    path        = getRootPath()
    total       = []
    pkgRoots    = []
    pkgVersions = 0
    regexp      = re.compile( r"^(\d+)\.(\d+)$" )

    Any.requireMsg( regexp, 'internal script error: empty regexp' )

    getProjectsWithErrorHandling( path, total )

    for package in total:
        pkgRoot = os.path.dirname( package )
        version = ProjectProperties.getPackageVersion( package, True )

        if pkgRoot not in pkgRoots:
            pkgRoots.append( pkgRoot )

        # if this package is one with a 2-digit version, add it to the
        # number of 2-digit-packages
        if regexp.match( version ):
            pkgVersions += 1

    logging.info( 'path:                                  %s', path )
    logging.info( 'number of distinct packages:           %d', len(pkgRoots) )
    logging.info( 'number of 2-digit-versions:            %d', pkgVersions )
    logging.info( 'number of 3-digit-versions (= total):  %d', len(total) )


# EOF
