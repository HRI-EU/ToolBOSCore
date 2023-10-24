# -*- coding: utf-8 -*-
#
#  functions to manage an SIT sandbox ("Proxy-SIT")
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


import glob
import logging
import os
import os.path
import re
import stat

from ToolBOSCore.Storage import SIT
from ToolBOSCore.Util    import Any, FastScript, ThreadPool


#----------------------------------------------------------------------------
# Public functions
#----------------------------------------------------------------------------


def isProxyDir( path ):
    """
        Returns a boolean if the given path points to a valid SIT sandbox
        ("proxy directory").
    """
    return os.path.islink( os.path.join( path, SIT.parentLink ) )


def requireIsProxyDir( path ):
    """
        Raises an AssertionError if the given path does not point to a valid
        SIT sandbox ("proxy directory").
    """
    if not isProxyDir( path ):
        raise AssertionError( "%s: Is not a valid SIT proxy directory" % path )


def findProxyInstallations( checkLinks = False ):
    """
        Returns a list of packages installed within the proxy SIT.

        A ValueError will be raised if the current SIT is not a proxy.

        If 'checkLinks' == True, each version symlink will also be tested
        if it really points into the root SIT. For example, it might be
        difficult to localize a manually changed link that points e.g. in
        another group proxy or so.
    """
    resultList     = []
    sit            = SIT.getPath()
    sitParent      = SIT.getParentPath()    # support cascaded proxies
    excludePattern = re.compile( r'^(parentTree|\d+\.\d+.*)$' )
    criteria       = re.compile( r"^(\d+)\.(\d+)(.*)" )

    Any.requireIsDir( sit )
    Any.requireIsDir( sitParent )
    requireIsProxyDir( sit )

    # find all entries within the proxy that seem to be a version number
    dirList = FastScript.getDirsInDirRecursive( sit,
                                     excludePattern=excludePattern,
                                     onError=FastScript.printPermissionDenied )

    # check each found entry if it is a version directory, if so we
    # can expect that this is a local project installation
    for project in dirList:
        for entry in os.listdir( project ):
            joinedPath = os.path.join( project, entry )

            # only perform test on version numbers
            if criteria.search( entry ):

                # don't use os.path.isdir() as it follows symlinks!
                fileType = os.lstat( joinedPath ).st_mode

                if checkLinks == True and stat.S_ISLNK( fileType ) == True:
                    # test if symlink points into root SIT
                    target = os.readlink( joinedPath )

                    if target[0] == '/' and not target.startswith( sitParent ):
                        logging.warning( joinedPath + ': points to ' + target )

                elif stat.S_ISDIR( fileType ):
                    # we found a proxy installation
                    resultList.append( joinedPath )

    return resultList


def createProxyDir( sitRoot, sitProxy, verbose=True ):
    """
        Creates an SIT proxy directory for the current user in the
        directory <sitProxy> with symlinks pointing into <sitRoot>.
    """
    sitRootPkgList = []

    if not os.path.isdir( sitRoot ):
        msg = '%s: No such directory (please check $SIT)' % sitRoot
        raise AssertionError( msg )

    if os.path.exists( sitProxy ):
        msg = '%s: Directory exists' % sitProxy
        raise AssertionError( msg )

    if os.path.exists( os.path.join( sitRoot, SIT.parentLink ) ):
        msg = '$SIT=%s already points to a proxy ' % sitRoot + \
              'directory (cascades are not allowed)'
        raise AssertionError( msg )

    if os.path.realpath( sitRoot ) == os.path.realpath( sitProxy ):
        msg = 'SIT proxy path must be different from parent SIT!'
        raise AssertionError( msg )


    SIT.getProjectsWithErrorHandling( sitRoot, sitRootPkgList )

    for package in sitRootPkgList:
        linkName = os.path.join( sitProxy, package )
        target   = os.path.join( sitRoot, package )

        if verbose:
            logging.info( 'linking %s', package )

        # create directory where the link shall be created
        FastScript.mkdir( os.path.dirname( linkName ) )

        logging.debug( 'linking %s --> %s', linkName, target )
        os.symlink( target, linkName )


    # create a symlink inside the proxy that points to the parent
    linkName = os.path.join( sitProxy, SIT.parentLink )
    os.symlink( sitRoot, linkName )


    logging.info( '' )
    logging.info( 'Proxy created in %s', sitProxy )


def updateProxyDir( removeBrokenSymlinks     = True,
                    removeEmptyCategories    = True,
                    linkNewPackagesIntoProxy = True,
                    checkProxyLinkTarget     = True,
                    checkProxyLinkedVersion  = True,
                    removeProxyInstallations = False,
                    cleanHomeDirectory       = True,
                    updateRTMapsIndex        = True,
                    dryRun                   = False ):
    """
        Updates the SIT proxy directory of the current user.

        The user may influence which worker functions shall be called
        (default: all)

          removeBrokenSymlinks:     remove broken symlinks to uninstalled
                                    packages

          removeEmptyCategories:    remove SIT categories that became empty,
                                    or packages without any version

          linkNewPackagesIntoProxy: if there are new packages in the global
                                    SIT, add a link to them into the proxy

          checkProxyLinkTarget:     verify that links are valid

          checkProxyLinkedVersion:  if there is a higher revision globally
                                    installed (e.g. 1.0.100) and the user
                                    has a link 1.0 pointing to 1.0.99 in the
                                    proxy, the 1.0 link will get updated to
                                    1.0.100 in order not to use an outdated
                                    revision

          removeProxyInstallations: DELETE ALL PACKAGES installed in the
                                    proxy (if any)

          cleanHomeDirectory:       clean-up unused files under ~/.HRI

          updateRTMapsIndex:        update *.pck symlinks in ~/.HRI/RTMaps

        If dryRun=True, nothing will actually be done.
    """
    from ToolBOSCore.Tools import RTMaps

    sitRoot         = SIT.getParentPath()
    sitProxy        = SIT.getPath()
    proxyChanged    = False
    sitRootPkgList  = []
    sitProxyPkgList = []
    pluginsEnabled  = []

    Any.requireIsBool( removeBrokenSymlinks     )
    Any.requireIsBool( removeEmptyCategories    )
    Any.requireIsBool( linkNewPackagesIntoProxy )
    Any.requireIsBool( checkProxyLinkTarget     )
    Any.requireIsBool( checkProxyLinkedVersion  )
    Any.requireIsBool( removeProxyInstallations )
    Any.requireIsBool( cleanHomeDirectory       )
    Any.requireIsBool( updateRTMapsIndex        )
    Any.requireIsBool( dryRun )

    Any.requireMsg( sitRoot != sitProxy,
                       '%s: Is not a proxy directory' % sitProxy )


    # TBCORE-466: user should be able to disable particular plugins

    #if removeProxyInstallations:               # added later, see below
        #pluginsEnabled.append( _removeProxyInstallations )

    if removeBrokenSymlinks:
        pluginsEnabled.append( _removeBrokenSymlinks )

    if removeEmptyCategories:
        pluginsEnabled.append( _removeEmptyCategories )

    if linkNewPackagesIntoProxy:
        pluginsEnabled.append( _linkNewPackagesIntoProxy )

    if checkProxyLinkTarget:
        pluginsEnabled.append( _checkProxyLinkTarget )

    if checkProxyLinkedVersion:
        pluginsEnabled.append( _checkProxyLinkedVersion )

    if cleanHomeDirectory:
        pluginsEnabled.append( _cleanHomeDirectory )

    if not pluginsEnabled:
        raise ValueError( 'Nothing to do. Please check your parameters.' )


    # in any case, after updating the proxy verify that there are no legacy
    # *.def files laying around
    pluginsEnabled.append( _checkDefFiles )

    tp = ThreadPool.ThreadPool()

    tp.add( SIT.getProjectsWithErrorHandling, sitRoot, sitRootPkgList )
    tp.add( SIT.getProjectsWithErrorHandling, sitProxy, sitProxyPkgList )

    tp.run()


    if removeProxyInstallations:
        changed = _removeProxyInstallations( sitRootPkgList, sitProxyPkgList,
                                             sitRoot, sitProxy, dryRun )

        if changed > 0:
            sitProxyPkgList = []
            SIT.getProjectsWithErrorHandling( sitProxy, sitProxyPkgList )


    for func in pluginsEnabled:
        proxyChanged |= func( sitRootPkgList, sitProxyPkgList,
                              sitRoot, sitProxy, dryRun )


    if updateRTMapsIndex:
        if RTMaps.isInstalled( sitRoot ):
            RTMaps.updateComponentIndex( sitRoot, sitProxy, dryRun )
        else:
            logging.debug( 'RTMaps not installed' )

    msg = 'Your proxy is up-to-date%s.' % ( ' now' if proxyChanged == True else '' )
    logging.info( '' )
    logging.info( msg )


#----------------------------------------------------------------------------
# Private functions
#----------------------------------------------------------------------------


def _getTreeDifferences( sitRootPkgList, sitProxyPkgList ):
    """
        Returns a list of packages that are installed in the global SIT
        but do not appear in the user's SIT proxy directory.
    """
    return list( set( sitRootPkgList) - set( sitProxyPkgList ) )


def _removeProxyInstallations( sitRootPkgList, sitProxyPkgList,
                               sitRoot, sitProxy, dryRun ):
    """
        ATTENTION: Unless dryRun=True, this function removes all packages
                   that have been installed locally to your proxy!
                   Use with caution!
    """
    requireIsProxyDir( sitProxy )

    toDelete = findProxyInstallations()  # list of absolute paths into proxy
    Any.requireIsList( toDelete )

    if len(toDelete) == 0:
        logging.info( 'no proxy installations to be deleted' )
        result = 0
    else:
        if dryRun:
            logging.info( '-- DRY RUN --   not deleting anything' )
            result = 0
        else:
            logging.info( 'deleting all proxy-installations as requested:' )
            result = len(toDelete)

        for installRoot in toDelete:
            if dryRun:
                logging.info( '-- DRY RUN --   normally would now delete %s', installRoot )
            else:
                logging.info( 'deleting %s', installRoot )
                FastScript.remove( installRoot )

    return result


def _removeBrokenSymlinks( sitRootPkgList, sitProxyPkgList,
                           sitRoot, sitProxy, dryRun ):
    """
        If 'dryRun' is True, it won't actually do anything to your proxy.

        Returns the number of broken links that have been removed
        (or that would have been removed, in case of dry run).
    """
    requireIsProxyDir( sitProxy )

    logging.info( 'searching for broken symlinks...' )
    brokenLinks = _findBrokenLinks( sitProxy )

    for path in brokenLinks:
        if dryRun:
            logging.info( '-- DRY RUN --   found broken symlink %s', path )
        else:
            if path.endswith( '.py' ):
                logging.info( 'deleting %s', path )
            else:
                logging.info( 'package was uninstalled: %s', SIT.strip( path ) )

            os.remove( path )

    return len(brokenLinks)


def _removeEmptyCategories( sitRootPkgList, sitProxyPkgList,
                            sitRoot, sitProxy, dryRun ):
    """
        If 'dryRun' is True, it won't actually do anything to your proxy.

        Returns the number of empty directories (unused SIT categories,
        packages without any version) that have been removed (or that would
        have been removed, in case of dry run).

        All parameters except 'sitProxy' path will be ignored and only
        kept for compatibility.
    """
    requireIsProxyDir( sitProxy )

    candidates = set()
    whitelist  = ( os.path.join( sitProxy, 'Modules', 'Index' ), )

    for root, dirs, files in os.walk( sitProxy, followlinks=False ):
        for entry in dirs:
            candidate = os.path.join( root, entry )

            if candidate not in whitelist:
                candidates.add( candidate )

    # path must not contain anything like a version string
    expr       = re.compile( r'/\d+\.\d+' )
    noMatch    = lambda p: not( expr.search( p ) )
    candidates = filter( noMatch, candidates )

    # only keep really empty directories
    isEmptyDir = lambda p: os.listdir( p ) == []
    emptyDirs  = list( filter( isEmptyDir, candidates ) )
    emptyDirs.sort()

    for path in emptyDirs:
        if dryRun:
            logging.info( '-- DRY RUN --   found empty dir. %s', path )
        else:
            logging.info( 'rmdir %s', SIT.strip( path ) )
            os.rmdir( path )

    return len(emptyDirs)


def _linkNewPackagesIntoProxy( sitRootPkgList, sitProxyPkgList,
                               sitRoot, sitProxy, dryRun ):
    """
        Creates a symlink in the proxy for each newly globally installed
        package.
    """
    Any.requireIsListNonEmpty( sitRootPkgList )
    Any.requireIsListNonEmpty( sitProxyPkgList )
    Any.requireIsDir( sitRoot )
    Any.requireIsDir( sitProxy )

    proxyChanged = False
    diffList     = _getTreeDifferences( sitRootPkgList, sitProxyPkgList )
    diffList.sort()

    for project in diffList:
        pkgRootPath  = os.path.join( sitRoot,  project )
        pkgProxyPath = os.path.join( sitProxy, project )
        pkgBaseDir   = os.path.dirname( pkgProxyPath )

        # make directory if it does not exist
        if not os.path.exists( pkgBaseDir ):
            FastScript.mkdir( pkgBaseDir )

        try:
            os.symlink( pkgRootPath, pkgProxyPath )
            logging.info( 'linking %s', project )
            proxyChanged = True
        except OSError:
            pass      # after linking one path, the other one might be inside

    return proxyChanged


def _checkDefFiles( sitRootPkgList, sitProxyPkgList,
                    sitRoot, sitProxy, dryRun ):
    """
        Checks that there are no orphaned *.def files in the proxy,
        f.i. leftovers from previous proxy-installations that have been
        deleted in the meanwhile.

        Superfluous *.def files might be a really hard-to-track source of
        errors: In case they don't match the actual interface of the
        (globally) installed component, it might be very difficult to find
        out why certain inputs/outputs/references do / don't appear in DTBOS.
    """
    from ToolBOSCore.Packages.ProjectProperties import isCanonicalPath
    from ToolBOSCore.Packages.ProjectProperties import splitPath

    Any.requireIsListNonEmpty( sitRootPkgList )
    Any.requireIsListNonEmpty( sitProxyPkgList )
    Any.requireIsDir( sitRoot )
    Any.requireIsDir( sitProxy )


    proxyPackages = findProxyInstallations()  # list of absolute paths
    Any.requireIsList( proxyPackages )
    proxyPackages = map( SIT.strip, proxyPackages )

    # filter-out 3-digit version numbers, as *.def files by convention
    # are for 2-digit versions only
    proxyPackages = filter( isCanonicalPath, proxyPackages )

    # create a corresponding fake-index for each proxy installation, for easy
    # string-based matching later
    #
    fakeDefs      = []

    for package in proxyPackages:
        ( category, packageName, packageVersion ) = splitPath( package )
        fakeDefs.append( '%s_%s.def' % ( packageName, packageVersion ) )

    indexDir      = os.path.join( sitProxy, 'Modules/Index' )
    defPathList   = glob.glob( os.path.join( indexDir, '*.def' ) )
    proxyChanged  = False

    for defPath in defPathList:
        defFile = os.path.basename( defPath )

        # delete superfluous *.def files
        if defFile not in fakeDefs:
            collapsed = SIT.collapseSIT( defPath )

            if dryRun:
                logging.info( '-- DRY RUN --   found superfluous %s', collapsed )
            else:
                logging.info( 'deleting %s', defPath )
                FastScript.remove( defPath )

    return proxyChanged


def _checkProxyLinkTarget( sitRootPkgList, sitProxyPkgList,
                           sitRoot, sitProxy, dryRun ):
    """
        Checks for each package in the list if the equivalent proxy symlink
        points into the SIT root directory or outside (e.g. group proxy)

        'projectList' must be a list containing canonical path names such
        as ['Libraries/Serialize/3.0'].
    """
    Any.requireIsListNonEmpty( sitRootPkgList )
    Any.requireIsListNonEmpty( sitProxyPkgList )
    Any.requireIsDir( sitRoot )
    Any.requireIsDir( sitProxy )

    for project in sitProxyPkgList:
        pkgProxyPath = os.path.join( sitProxy, project )

        if os.path.islink( pkgProxyPath ):
            # check if version symlink points into root SIT
            try:
                proxyLinkTarget = os.readlink( pkgProxyPath )

                if proxyLinkTarget[0] == '/' and \
                   not proxyLinkTarget.startswith( sitRoot ):
                    logging.warning( '%s: points to %s', pkgProxyPath, proxyLinkTarget )
            except OSError:
                logging.warning( 'invalid symlink: please check %s', pkgProxyPath )

    return False        # proxy was not altered by this


def _checkProxyLinkedVersion( sitRootPkgList, sitProxyPkgList,
                              sitRoot, sitProxy, dryRun ):
    """
        Checks if the two-digit version in the proxy points to the most
        recent version. Otherwise this can happen:

          * Developer A installs "Serialize/3.0.100" into his proxy, the
            2-digit link "3.0" points into the proxy to version 3.0.100.

          * Developer B installs "Serialize/3.0.101" globally.

          * Now the 3.0-symlink of developer A is outdated.
    """
    Any.requireIsListNonEmpty( sitRootPkgList )
    Any.requireIsListNonEmpty( sitProxyPkgList )
    Any.requireIsDir( sitRoot )
    Any.requireIsDir( sitProxy )

    proxyChanged = False

    for project in sitProxyPkgList:
        localPatchlevel  = SIT.getActiveRevision( sitProxy, project )
        globalPatchlevel = SIT.getActiveRevision( sitRoot, project )

        if localPatchlevel is None or globalPatchlevel is None:
            continue

        if localPatchlevel < globalPatchlevel:
            logging.info( 'updating %s', project )

            pkgProxyPath = os.path.join( sitProxy, project )
            pkgRootPath  = os.path.join( sitRoot,  project )

            FastScript.remove( pkgProxyPath )
            os.symlink( pkgRootPath, pkgProxyPath )
            proxyChanged = True

    return proxyChanged


def _cleanHomeDirectory( sitRootPkgList, sitProxyPkgList,
                         sitRoot, sitProxy, dryRun ):
    """
        Clean-up really old / unused files under ~/.HRI
    """
    configDir = os.path.expanduser( '~/.HRI' )

    if not os.path.isdir( configDir ):
        logging.debug( '%s: No such directory', configDir )
    else:
        logging.debug( 'cleaning up %s', configDir )

        for item in ( 'CMBOS', 'HappyPorting2009', 'HRI',
                      'ToolBOS/PythonConsole', 'ToolBOS/VFSTelnet.conf' ):
            FastScript.remove( os.path.join( configDir, item ) )

    return False


def _findBrokenLinks( sitProxy ):
    """
        Returns a list of broken symlinks below 'sitProxy'.
    """
    resultList = []

    for root, dirs, files in os.walk( sitProxy ):
        for fileName in files:
            path = os.path.join( root, fileName )

            if os.path.islink( path ):
                try:

                    target = os.path.realpath( path )

                    if not os.path.exists( target ):
                        resultList.append( path )

                except OSError as details:

                    # Symlink cannot be read e.g. due to I/O error
                    #
                    # We experienced this when sbd. by chance was installing
                    # a BBCM component and the corresponding index file link
                    # has not been written, yet. Indeed a cornercase ;-)

                    logging.debug( 'unable to read symlink: %s', details )

    return resultList


# EOF
