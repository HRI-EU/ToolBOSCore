# -*- coding: utf-8 -*-
#
#  Functions to query basic project properties
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
import re
import os

from ToolBOSCore.Storage import SIT
from ToolBOSCore.Util    import Any, FastScript


#----------------------------------------------------------------------------
# Constants, settings
#----------------------------------------------------------------------------


missingPkgMsg            = '[ATTENTION: PACKAGE MISSING OR PERMISSION DENIED]'

_regExpCanonicalPathUnix = None
_regExpCanonicalPathWin  = None

_sitPkgCache             = None


#----------------------------------------------------------------------------
# Assertions
#----------------------------------------------------------------------------


def isCanonicalPath( path ):
    """
        Returns a boolean if 'path' is a canonical path (e.g.
        'Libraries/Spam/42.0' which contains neither the precise SIT
        location nor any placeholder such as ${SIT} etc.).
    """
    Any.requireIsTextNonEmpty( path )

    global _regExpCanonicalPathUnix
    global _regExpCanonicalPathWin

    #if not _regExpCanonicalPathUnix:
    _regExpCanonicalPathUnix = re.compile( r'^\w+\S*/\S+/\d+\.\d+$' )

    #if not _regExpCanonicalPathWin:
    _regExpCanonicalPathWin = re.compile( r'^\w+\S*\\\\\S+\\\\\d+\.\d+$' )

    if _regExpCanonicalPathUnix.match( path ) or \
        _regExpCanonicalPathWin.match( path ):
        return True
    else:
        return False


def requireIsCanonicalPath( path ):
    """
        Throws an AssertionError if 'path' is not a canonical path, e.g.
        'Libraries/Spam/42.0' which contains neither the precise SIT
        location nor any placeholder such as ${SIT} etc.
    """
    Any.requireMsg( isCanonicalPath( path ),
                    '%s: is not a canonical path ("packageCategory/pkgName/pkgVersion")'
                    % path )


def toCanonicalPath( string ):
    """
        Takes a string and attempts to shrink it to a canonical path,
        removing any leading SIT prefix or trailing slash.

           '/hri/sit/latest/DevelopmentTools/ToolBOSCore/3.0/'
           --> 'DevelopmentTools/ToolBOSCore/3.0'
    """
    Any.requireIsTextNonEmpty( string )

    canonicalPath = SIT.strip( string )

    # remove trailing slashes (occurs if user provides a string with trailing slashes)
    while canonicalPath.endswith( '/' ):
        canonicalPath = canonicalPath[0:-1]

    return canonicalPath


def isURL( string ):
    """
        Returns a boolean if 'string' is a package URL, f.i. should start
        with 'sit://' or 'deb://'.
    """
    Any.requireIsText( string )

    return string.startswith( 'sit://' ) or string.startswith( 'deb://' )


def requireIsURL( string ):
    """
        Throws an AssertionError if 'string' is not a package URL.
    """
    Any.requireMsg( isURL( string ),
                    '%s: is not a BST package URL' % string )


#----------------------------------------------------------------------------
# Public functions to query basic project information
#----------------------------------------------------------------------------


def detectTopLevelDir( path = None ):
    """
        From any given path that points *within* a package, this function
        tries to find the package's root directory by searching the current
        and parent directories for a file named 'CMakeLists.txt' or
        'packageVar.cmake'.

        If path is omitted (None), search starts at the current working
        directory.

        If path does not point into a package, thus no 'packageVar.cmake' or
        'CMakeLists.txt' can be found, a RuntimeError will be raised.
    """
    if not path:
        path = os.getcwd()

    for fileName in ( 'CMakeLists.txt', 'packageVar.cmake', 'pkgInfo.py' ):
        filePath = os.path.join( path, fileName )

        if os.path.exists( filePath ):
            return path

    if path == '' or path == '/':
        result = None
    else:
        result = detectTopLevelDir( os.path.split( path )[0] )

    return result


def getPackageCategoryFromPath( projectRootDir ):
    """
        Returns the packageCategory (former known as "project start path") of a
        module, e.g.:

          getPackageCategoryFromPath( '/hri/sit/latest/Modules/BBCM/Food/FeedSnake/42.0' )
          getPackageCategoryFromPath( 'Modules/BBCM/Food/FeedSnake/42.0' )

        return both 'Modules/BBCM/Food'.
    """
    Any.requireIsTextNonEmpty( projectRootDir )

    tmp = projectRootDir

    # first remove trailing project name and version from string
    search  = os.sep + getPackageName( tmp ) + os.sep + getPackageVersion( tmp )
    replace = ''
    tmp     = tmp.replace( search, replace )

    # replace value of ${SIT}
    tmp     = SIT.strip( tmp )

    # remove trailing slashes (occurs if user provides a string with trailing slashes)
    while tmp.endswith( '/' ):
        tmp = tmp[0:-1]

    return tmp


def getPackageName( projectRootDir ):
    """
        Returns the project name of a module, e.g.:

          getPackageName( '/hri/sit/latest/Modules/BBCM/Food/FeedSnake/42.0' )
          getPackageName( 'Modules/BBCM/Food/FeedSnake/42.0' )

        return both 'Modules/BBCM/Food'.

        If projectRootDir does not exist, an OSError will be thrown.
    """
    Any.requireIsTextNonEmpty( projectRootDir )

    absPath     = os.path.abspath( projectRootDir )  # resolve links,...
    Any.requireIsTextNonEmpty( absPath )

    # do not check for directory existence, so we can call the function
    # even on non-existing path names (for doing some path computations)
    #
    # Any.requireIsDir( absPath )

    dirName     = os.path.dirname( absPath )         # cut trailing version
    packageName = os.path.basename( dirName )        # keep only last token

    return packageName


def getPackageVersion( projectRootDir, verbatim = False ):
    """
        Returns the version of a module, e.g.:

          getPackageVersion( '/hri/sit/latest/Modules/BBCM/Food/FeedSnake/42.0' )
          getPackageVersion( 'Modules/BBCM/Food/FeedSnake/42.0' )

        return both '42.0'.

        Note: By convention it is allowed that projects can have versions
              like "42.0-beta" or "42.0_beta". This "-beta" or "_beta" is
              stripped off by this function. If you want to have the
              verbatim version string (e.g. to compute path names), please
              set the 'verbatim' parameter to 'True'.
    """
    Any.requireIsTextNonEmpty( projectRootDir )

    dirName = os.path.basename( os.path.abspath( projectRootDir ) )

    if verbatim:
        return dirName

    # if the directory is called e.g. "2.10_experimental", return only "2.10"
    tmp = re.search( r"^(\d+\.\d+).*$", dirName )

    return tmp.group(1) if tmp else dirName


def getPackageVersions( project, includePatchlevelVersions = False ):
    """
        Returns all installed versions of a project.

        This returns only the versions in the form "Major.Minor".

        Setting 'includePatchlevelVersions=True' will return all, e.g.
        those in the form "Major.Minor.Patchlevel" or "Major.Minor-ExtraTag".
    """
    Any.requireIsDir( project )

    allVersionsList = FastScript.getDirsInDir( project )
    resultList      = []

    if includePatchlevelVersions:
        resultList = allVersionsList
    else:
        for version in allVersionsList:
            if re.match( r"^\d+\.\d+$", version ):
                resultList.append( version )

    return resultList


def splitPath( projectRootDir ):
    """
        Splits the given path and returns a tuple of three elements:
        - the packageCategory, e.g. 'Modules/BBCM/InputOutput'
        - the project name, e.g. 'UltimaTest' and
        - the project version, e.g. '2.2'
    """
    Any.requireIsTextNonEmpty( projectRootDir )

    projectCategory = getPackageCategoryFromPath( projectRootDir )
    packageName     = getPackageName( projectRootDir )
    packageVersion  = getPackageVersion( projectRootDir, True )

    return projectCategory, packageName, packageVersion


def splitURL( packageURL ):
    Any.requireIsTextNonEmpty( packageURL )

    try:
        result = packageURL.split( '://' )
    except ValueError:
        raise ValueError( 'invalid package URL: %s' % packageURL )

    return result


#----------------------------------------------------------------------------
# Advanced project management functions
#----------------------------------------------------------------------------


def getSVNLocationFromFilesystem( package ):
    """
        This reads the 'repositoryUrl' from the pkgInfo.py.

        If the URL cannot be retrieved for any reason, 'None' will be
        returned.

    """
    from ToolBOSCore.Storage.PkgInfo import getPkgInfoContent

    requireIsCanonicalPath( package )

    try:
        url = getPkgInfoContent( package )['repositoryUrl']
    except ( AssertionError, KeyError, IOError ):
        url = None

    return url


def guessSVNLocation( package ):
    """
        If you don't know where a project's SVN repository is located,
        this function may provide a reasonable hint.

        'package' must be a canonical project path.
    """
    from ToolBOSCore.Settings.ToolBOSConf import getConfigOption

    requireIsCanonicalPath( package )

    url = None

    try:
        # first check if we have ground truth information available...
        url = getSVNLocationFromFilesystem( package )
    except ( AssertionError, KeyError, IOError ):
        pass


    if not url:
        # otherwise use default server and path as good guess
        server      = getConfigOption( 'defaultSVNServer' )
        path        = getConfigOption( 'defaultSVNRepositoryPath' )
        url = 'svn+ssh://%s%s/%s' % ( server, path, package )
        logging.debug( 'guessing SVN location: %s' % url )

    Any.requireIsMatching( url, ".*://.*" )
    Any.requireMsg( url[0] != "'", 'invalid URL string' )
    Any.requireMsg( url[0] != '"', 'invalid URL string' )

    return url


def areAllDependenciesInstalled( project, dependencyList = None ):
    """
        Checks and returns a boolean if all dependencies of a project are
        present in the SIT. It will also return 'False' if the dependencies
        could not be queried at all or if there are some errors. So receiving
        a 'True' status is quite reliable.

        'project' must be in canonical form,
        e.g. 'Libraries/Serialize/3.0'.

        If 'dependencyList' (an optionally nested list of dependencies) is
        specified it will be used as a cache instead of querying the
        dependency tree from the slower filesystem.
            If such 'dependencyList' is provided but is an empty list then
        always 'True' will be returned.

    """
    Any.requireIsTextNonEmpty( project )
    #Any.requireIsList( dependencyList )

    if( isinstance( dependencyList, list ) ) and len( dependencyList ) == 0:
        return True

    if not dependencyList:
        try:
            dependencyList = getDependencies( project, True )
        except RuntimeError:    # e.g. unable to retrieve dependencies
            return False

    urlList = FastScript.reduceList( FastScript.flattenList( dependencyList ) )

    for url in urlList:
        try:
            if not isInstalled( url ):
                return False
        except ValueError as details:
            logging.error( details )
            raise ValueError( 'unable to check install status of %s' % project )

    return True


def isInstalled( url, sitPath=None ):
    """
        Checks if the given package is installed. Depending on the URL type
        different checks will be performed, e.g.:

        'sit://Libraries/Serialize/3.0'    # check in current SIT
        'deb://binutils'                   # check for O.S. packages (*.deb)

        You may speed-up this function by providing 'sitPath' so that it
        does not need to be queried internally every time.
    """
    from ToolBOSCore.Platforms import Debian

    Any.requireIsTextNonEmpty( url )


    if ':' not in url:
        # default to SIT packages
        url = 'sit://' + url

    protocol, remainder = splitURL( url )

    if protocol == 'sit':
        if not sitPath:
            sitPath = SIT.getPath()

        status  = isInstalled_sitPackage( remainder, sitPath )
    elif protocol == 'deb':
        try:
            status = Debian.isInstalled( remainder )
        except OSError as details:
            raise OSError( details )
    else:
        raise RuntimeError( 'invalid URL protocol or format' )

    return status


def isInstalled_sitPackage( package, sitPath ):
    """
        Looks for a certain package in the specified SIT and returns whether
        or not it has been found.

        'package' must be in the form e.g. 'Libraries/Serialize/3.0'.

        Returns a boolean status if it is installed.
    """
    global _sitPkgCache

    Any.requireIsTextNonEmpty( package )
    Any.requireIsTextNonEmpty( sitPath )

    if not _sitPkgCache:
        _sitPkgCache = {}

    installRoot = os.path.join( sitPath, package )

    try:
        installed                   = _sitPkgCache[ installRoot ]
    except KeyError:
        installed                   = os.path.isdir( installRoot )
        _sitPkgCache[ installRoot ] = installed

    return installed


def requireIsInstalled( url ):
    """
        Throws an EnvironmentError if the proviced package is not
        installed.
    """
    if url.startswith( 'sit://' ) or ':' not in url:
        msg = '%s: No such package in SIT' % url
    else:
        msg = '%s: Package not installed' % url


    Any.requireMsg( isInstalled( url ), msg )


#----------------------------------------------------------------------------
# Dealing with version numbers
#----------------------------------------------------------------------------


def splitVersion( version ):
    """
        Splits a version string in its individual tokens:
          * major version
          * minor version
          * patchlevel
          * extra tag
    """
    tmp = re.match( r"^(\d+)\.(\d+)\.*(\d*)\.*(.*)$", version )

    if tmp:
        return [ tmp.group(1), tmp.group(2), tmp.group(3), tmp.group(4) ]
    else:
        return [ None, None, None, None ]


#----------------------------------------------------------------------------
# Query information of a pkgInfo.py file
#----------------------------------------------------------------------------


def getMaintainer( project ):
    """
        Returns the username of the maintainer of the project.
    """
    from ToolBOSCore.Storage.PkgInfo import getPkgInfoContent

    requireIsCanonicalPath( project )

    try:
        maintainer = getPkgInfoContent( project )['maintainer']
    except ( IOError, KeyError, AssertionError ):
        maintainer = getMaintainerFromFilesystem( project )

    return maintainer


def getMaintainerFromFilesystem( project ):
    """
        Returns the username of the maintainer by reading the fileowner of
        the project from the current SIT.
    """
    requireIsCanonicalPath( project )

    path  = SIT.getPath() + os.sep + project
    owner = FastScript.getFileOwner( path )

    return owner


#----------------------------------------------------------------------------
# Dependencies (re-use of other packages)
#----------------------------------------------------------------------------


def getDependencies( project, recursive = False, cache = None,
                     ignoreErrors = False, highlightMissing = True,
                     systemPackages = True, sitPath = None ):
    """
        Returns a list containing the direct dependencies of this package.
        If "recursive=True", they will be followed and the list actually
        becomes a nested list / tree. If the package does not have any
        dependencies the list will be empty.

        'project' must be specified in canonical form, e.g.:
           - 'Libraries/Serialize/3.0'
           - 'sit://Libraries/Serialize/3.0'
           - 'deb://gcc'

        If 'recursive=False', the list will contain the pure untreated
        strings stored in the pkgInfo.py file. There is no preprocessing
        done on its semantics. In recursive mode, we need to follow those
        paths and need to resolve 'sit://' etc.

        The 'cache' map is internally used to avoid processing already
        treated packages again. You should not specify this parameter when
        calling this function unless you need to query the dependencies of
        multiple projects in a list. In such case providing a cache-map
        will improve performance a lot.

        If 'systemPackages=False', Non-SIT packages such as *.deb or *.rpm
        packages will be excluded from the result list.

        You may speed-up this function by providing 'sitPath' so that it
        does not need to be queried internally every time.
    """
    from ToolBOSCore.Storage.PkgInfo import getPkgInfoContent

    if project.find( '://' ) > 0:
        projectURL = project
        project    = SIT.strip( project )
    else:
        projectURL = 'sit://' + project  # default protocol


    resultList = []

    if cache is None:
        cache = {}

    if not sitPath:
        sitPath = SIT.getPath()

    try:                                 # first look-up the cache
        depList = cache[ projectURL ]
    except KeyError:                     # if not found read from filesystem
        if projectURL.startswith( 'sit://' ):
            try:
                depList = getPkgInfoContent( project )['depends']
            except ( AssertionError, KeyError ):
                depList = []
        else:
            depList = []  # retrieving *.deb dependencies not implemented


    # store the direct dependencies into the cache map
    cache[ projectURL ] = depList

    for dep in depList:
        if isinstance( dep, str ):

            if systemPackages == False and not dep.startswith( 'sit://' ):
                continue

            resultList.append( dep )

            if recursive:
                # 2012-10-09 reactivated this check for isInstalled() == False,
                # needed by ListDependencies.py + ExportWizard.py

                try:
                    if not isInstalled( dep, sitPath ):
                        if highlightMissing:
                            resultList.append( [ missingPkgMsg ] )

                        if not ignoreErrors:
                            msg = '%s depends on %s which is not installed' \
                                  % ( project, dep )
                            raise RuntimeError( msg )
                except ValueError:
                    raise ValueError( 'invalid dependency "%s" in package %s' %
                                      ( dep, project ) )

                subDepList = getDependencies( dep,
                                              recursive,
                                              cache,
                                              ignoreErrors,
                                              highlightMissing,
                                              systemPackages,
                                              sitPath )

                if len( subDepList ) > 0:
                    resultList.append( subDepList )
        else:
            raise TypeError( 'dependency entry is not of type "str"' )

    return resultList


def getBuildDependencies( project, recursive = False ):
    """
        For now this simply calls getBuildDependenciesFromPkgInfo(),
        ignoring the case that the pkgInfo.py might not be present.

        Note: Unlike getDependencies(), the result of this function
              is a flat (non-nested) list.
    """
    from ToolBOSCore.Storage.PkgInfo import getPkgInfoContent

    Any.requireIsTextNonEmpty( project )

    try:
        resultList = getPkgInfoContent( project )['buildDepends']
    except ( AssertionError, IOError, KeyError ):
        resultList = []

    if recursive:
        depList = getDependencies( project, recursive=True )
        depList = FastScript.flattenList( depList )

        for dep in depList:
            if dep.startswith( 'sit://' ):
                try:
                    buildDepList = getPkgInfoContent( SIT.strip(dep) )['buildDepends']
                except ( AssertionError, IOError, KeyError ):
                    buildDepList = []

                if buildDepList:
                    resultList.append( buildDepList )

        resultList = FastScript.reduceList( resultList )

    return resultList


def getBuildRequirements( projectURL, recursive=False, cache=None, ignoreErrors=False ):
    """
        Returns a list of packages that are necessary to build the
        specified package.

        'projectURL' must be a canonical path starting with the "sit://" prefix.

        If recursive=False, the list will contain the pure untreated strings
        stored in the pkgInfo.py file. There is no preprocessing done on its
        semantics. In recursive mode, we need to follow those paths and
        need to resolve 'sit://' etc.
    """
    Any.requireIsTextNonEmpty( projectURL )
    Any.requireMsg( projectURL.startswith( 'sit://' ) == True,
                       "'project' parameter needs to start with sit:// " + \
                       "'(you passed: %s)" % projectURL )

    # query dependencies of package, don't forget to add package itself
    resultList = []# projectURL ]
    project    = SIT.strip( projectURL )

    if not isinstance( cache, dict ):
        cache = {}

    try:                                 # first look-up the cache
        depList = cache[projectURL]
        #logging.debug( 'CACHE HIT: %s' % projectURL )
    except KeyError:                     # if not found read from filesystem
        #logging.debug( 'CACHE MISS: %s' % projectURL )
        tmpList = getDependencies( project, systemPackages=False ) + \
                  getBuildDependencies( project )
        depList = FastScript.reduceList( tmpList )

    # store the direct dependencies into the cache map
    cache.update( { projectURL: depList } )

    for dep in depList:
        resultList.append( dep )

        if recursive == True and not dep.startswith( 'deb://' ):
            subDepList = getBuildRequirements( dep, recursive, cache, ignoreErrors )

            for subDep in subDepList:
                if subDep not in resultList:
                    resultList.append( subDep )

    return resultList


def getDependenciesFromCurrentPackage( recursive=False, systemPackages=False ):
    """
        Assuming the current working directory to be a source package,
        it queries the dependencies and optionally all the recursive
        dependencies, too.
    """
    from ToolBOSCore.Storage         import CMakeLists
    from ToolBOSCore.Storage.PkgInfo import getPkgInfoContent

    Any.requireIsBool( recursive )
    Any.requireIsBool( systemPackages )

    fileName    = 'CMakeLists.txt'
    Any.requireIsFileNonEmpty( fileName )

    fileContent = FastScript.getFileContent( fileName )
    Any.requireIsTextNonEmpty( fileContent )

    try:
        depList = getPkgInfoContent( dirName='.' )['depends']
    except ( AssertionError, IOError, KeyError ):
        depList = CMakeLists.getDependencies( fileContent )

    Any.requireIsList( depList )

    if recursive:
        result = []
        cache  = {}

        for dep in depList:
            result.append( dep )

            tmp = getDependencies( dep, recursive, cache, systemPackages )

            if tmp:                     # do not add empty lists
                result.append( tmp )
    else:
        result = depList

    return result


def getFlatDependencies( canonicalPaths, cache=None, sitPath=None ):
    """
        Resolves all dependencies recursively and converts them to a flat
        set of overall dependencies.

        This function might be handy to determine all SIT packages that
        need to transferred to another site.
    """
    cache   = {}            if cache   is None else cache
    sitPath = SIT.getPath() if sitPath is None else sitPath

    Any.requireIsIterable( canonicalPaths )
    Any.requireIsDict( cache )
    Any.requireIsTextNonEmpty( sitPath )


    result = set()

    for canonicalPath in canonicalPaths:
        requireIsCanonicalPath( canonicalPath )

        result.add( 'sit://' + canonicalPath )

        deps = getDependencies( canonicalPath, recursive=True, cache=cache,
                                systemPackages=False, sitPath=sitPath )

        flatDeps = FastScript.flattenList( deps )

        for item in flatDeps:
            result.add( item )

    return result


def isDeprecated( canonicalPath ):
    """
        Checks from the filesystem if the specified package (canonical path)
        is flagged as deprecated.

        Returns True if either of these files exists:
               <sitRoot>/Libraries/Spam/42.0/deprecated.txt
               <sitRoot>/Libraries/Spam/deprecated.txt

               or if the canonicalPath is listed in the file
               <sitPath>/Temporary/CIA/1.0/deprecatedOverride.txt.
    """
    requireIsCanonicalPath( canonicalPath )

    filename = 'deprecated.txt'
    sitRoot  = SIT.getRootPath()
    pkgPath  = os.path.join( sitRoot, canonicalPath )
    check1   = os.path.join( sitRoot, os.path.dirname( canonicalPath ), filename )
    check2   = os.path.join( sitRoot, canonicalPath, filename )


    # if package is not present in SIT we can't give reliable information
    # if it is deprecated or not

    if not os.path.exists( pkgPath ):
        raise ValueError( "%s: Package not installed in SIT" % canonicalPath )


    if os.path.exists( check1 ) or os.path.exists( check2 ):
        return True


    # check CIA operator "sudo override"
    overrideFile = os.path.join( SIT.getPath(),
                                 'Temporary/CIA/1.0/deprecatedOverride.txt' )

    if os.path.exists( overrideFile ):
        for line in FastScript.getFileContent( overrideFile,
                                               splitLines=True ):
            if line.strip() == canonicalPath:
                return True

    return False


def isExcludedFromCIA( package ):
    """
        Checks from the filesystem if the specified package (canonical path)
        is flagged as being opted-out from the Continuous Integration
        system.

        The function checks if "excludeFromCIA = True" is specified in
        the pkgInfo.py of the installed package.
    """
    from ToolBOSCore.Storage.PkgInfo import getPkgInfoContent

    status = False

    # temporarily disable verbosity, to prevent flooding CIA log
    oldLevel = Any.getDebugLevel()
    Any.setDebugLevel( 3 )

    try:
        pkgInfo = getPkgInfoContent( package )

        if pkgInfo['excludeFromCIA']:
            status = True

    except ( AssertionError, IOError, KeyError ):
        # if pkgInfo.py not present, the package surely was not opted-out
        pass

    Any.setDebugLevel( oldLevel )

    return status


def setDeprecated( canonicalPath, allVersions=False, message='' ):
    """
        Deprecate a version of a package. canonicalPath is used to
        deprecate the package. If allVersions is True, all versions are
        deprecated.  message will be written into deprecated.txt.
    """
    requireIsCanonicalPath( canonicalPath )
    Any.requireIsText( message )

    if message:
        reason = message + '\n'
    else:
        reason = message

    if allVersions:
        relPath = os.path.dirname( canonicalPath )
    else:
        relPath = canonicalPath

    absPath = os.path.join( SIT.getRootPath(), relPath )
    filePath = os.path.join( absPath, "deprecated.txt" )

    if os.path.exists( absPath ):
        try:
            FastScript.setFileContent( filePath, reason )
            logging.info( '%s deprecated', relPath )
            logging.debug( 'Created file %s', filePath )
        except (IOError, OSError) as e:
            logging.warning( e )
            logging.error( 'Could not deprecate %s', relPath )
            return False
    else:
        logging.warning( '%s is not installed!', relPath )
        return False

    return True

# EOF
