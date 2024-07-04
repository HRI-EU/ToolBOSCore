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

from ToolBOSCore.Util import FastScript

parentLink = 'parentTree'


def getDefaultRootBaseDir():
    """
        Default location where all the Software Installation Tree's builds
        and LTS directories can be found inside.
    """
    return '/hri/sit'


def getDefaultProxyBaseDir():
    """
        Default location where all the Proxy-SIT's are located.
    """
    return os.path.expanduser( '~/.HRI/sit' )


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
                   [ '/hri/sit/latest/Libraries/Example/3.0', ... ]
             False:
                   [ 'Libraries/Example/3.0', ... ]

        You may pass a function callback that will be called upon errors,
        e.g. permission denied. This function needs to take a single
        path parameter. If omitted, an OSError will be raised upon errors.
    """
    FastScript.requireIsDir( path )

    path           = os.path.normpath( path )
    projectList    = []
    excludePattern = re.compile( r"(parentTree|^\d+\.\d+)" )
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
    FastScript.requireIsDir( path )
    FastScript.requireIsList( resultList )

    logging.info( 'scanning %s...', path )

    resultList.extend( getProjects( path, keepPath=False,
                                    onError=FastScript.printPermissionDenied ) )

    FastScript.requireIsListNonEmpty( resultList )


def getCanonicalPaths( sitPath ):
    """
        Returns a sorted list of all installed packages
        (major.minor versions only).
    """
    from ToolBOSCore.Packages.ProjectProperties import isCanonicalPath

    FastScript.requireIsDir( sitPath )

    sitPackages = []
    getProjectsWithErrorHandling( sitPath, sitPackages )

    canonicalPaths = list( filter( isCanonicalPath, sitPackages ) )
    canonicalPaths.sort()

    return canonicalPaths


def getActiveRevision( sitPath, project ):
    """
        This function returns the currently installed patchlevel
        of a project, by resolving the 2-digit symlinks.

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


# EOF
