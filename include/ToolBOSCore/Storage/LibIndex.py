# -*- coding: utf-8 -*-
#
#  LibIndex handling
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


import fnmatch
import logging
import os
import shutil

from ToolBOSCore.Packages.ProjectProperties import getDependencies
from ToolBOSCore.Packages.ProjectProperties import splitPath
from ToolBOSCore.Platforms.Platforms        import getPlatformNames
from ToolBOSCore.Storage.SIT                import getPath
from ToolBOSCore.Storage.SIT                import strip
from ToolBOSCore.Util                       import FastScript
from ToolBOSCore.Util                       import Any


class LibIndex( object ):

    fileDict      = None
    libCheck      = None
    path          = None
    pkgList       = None
    pkgNames      = None            # for symbol-conflict detection
    platforms     = None
    sitPath       = None

    _depCache     = None
    _showProgress = None


    def __init__( self ):
        self.fileDict      = {}
        self.libCheck      = False
        self.path          = 'LibIndex'
        self.pkgList       = []
        self.pkgNames      = []
        self.platforms     = getPlatformNames()
        self.sitPath       = getPath()

        self._depCache     = {}
        self._showProgress = False


    def setOutputDir( self, path ):
        """
            Specifies where the index should be created (default=./LibIndex).
        """
        Any.requireIsTextNonEmpty( path )
        self.path = path


    def addPackage( self, canonicalPath, recursive, filterFunc ):
        """
            Runs 'filterFunc' on the specified package.

            Does the same for all dependent packages if 'recursive=True'.
        """
        Any.requireIsTextNonEmpty( canonicalPath )
        Any.requireIsBool( recursive )
        Any.requireIsCallable( filterFunc )

        canonicalPath = strip( canonicalPath )
        installRoot   = self.sitPath + os.sep + canonicalPath

        if canonicalPath in self.pkgList:      # avoid duplicates
            return

        if canonicalPath.startswith( 'deb://' ):  # ignore Debian packages
            return

        if self._showProgress:
            logging.info( 'processing %s', canonicalPath )

        if os.path.exists( installRoot + os.sep + 'SkipLibIndex' ):
            logging.debug( '%s: SkipLibIndex found' % canonicalPath )
        else:
            filterFunc( self, canonicalPath )

        if recursive:
            deps         = getDependencies( project        = canonicalPath,
                                            recursive      = True,
                                            cache          = self._depCache,
                                            systemPackages = False,
                                            sitPath        = getPath() )

            shortDepList = FastScript.reduceList( deps )

            for package in shortDepList:
                if package not in self.pkgList:
                    self.addPackage( package, False, filterFunc )


    def addPackageList( self, pkgList, recursive, filterFunc ):
        """
            Like addPackage(), but for a list of packages.

            pkgList = ( 'Basics/Any/2.2', 'Basics/Time/1.1' )
            LibIndex.createFromList( pkgList, 'MyLibIndex' )
        """
        Any.requireIsList( pkgList )
        Any.requireIsCallable( filterFunc )

        pkgFileDict     = {}
        for pkg in pkgList:
            deps        = getDependencies( project        = pkg,
                                         recursive      = True,
                                         cache          = self._depCache,
                                         systemPackages = False,
                                         sitPath        = getPath() )
            shortDeps   = FastScript.reduceList( deps )
            if shortDeps:
                pkgFileDict[ strip( splitPath(pkg)[1] ) ] = shortDeps

        #returns the list of conflicting dependencies, if empty there are no conflicts
        conflictDeps = self.confDeps( pkgFileDict )
        textError    = 'ERROR:\n'
        text         = '{} {} used by {} \n is in conflict with \n{} {} used by {}\n\n'

        for dep in conflictDeps:
            textError = textError + text.format( dep[ 1 ], dep[ 2 ], dep[ 0 ], dep[ 1 ], dep[ 4 ], dep[ 3 ] )

        Any.requireMsg( not conflictDeps, '\n %s' % textError )

        for pkg in pkgList:
            self.addPackage( pkg, recursive, filterFunc )


    def confDeps( self, pkgDeps):
        conflict = []

        for key, value in pkgDeps.items():
            for key2, value2 in pkgDeps.items():
                if not key is key2:
                    for v in value:
                        if v not in value2:
                            for v2 in value2:
                                if splitPath( v )[ 1 ] == splitPath( v2 )[ 1 ]:
                                    #check for duplicates
                                    if not ((key2 , key, splitPath( v )[ 1 ]) in
                                            ((cd[ 0 ], cd[ 3 ], cd[ 1 ]) for cd in conflict)):

                                        conflict.append( (key, splitPath( v )[ 1 ], splitPath( v )[ 2 ],
                                                                 key2, splitPath( v2 )[ 2 ]) )
        return conflict


    def addFile( self, srcFile_abs, dstFile_rel ):
        """
            Marks the file "srcFile_abs" (absolute path) to be
            later distributed under the relative (!) path "dstFile_rel".

            The dstFile will be put relative to the output directory of
            the LibIndex.

                addFile( '/path/to/myExecutable', 'bin/myExecutable' )
        """
        self.fileDict.update( { srcFile_abs: dstFile_rel } )


    def remove( self ):
        """
            Deletes the content of the LibIndex directory, f.i. to start
            with a clean new directory.
        """
        FastScript.remove( self.path )


    def run_copy( self ):
        """
            Copies all previously added / detected files to the output
            directory.
        """
        logging.debug( 'copying %d files... (this may take some time)' % \
                       len( self.fileDict.keys() ) )

        for original, target in self.fileDict.items():
            srcFile = original
            dstFile = self.path + os.sep + target

            logging.debug( 'copying %s -> %s' % ( srcFile, dstFile ) )

            FastScript.mkdir( os.path.dirname( dstFile ) )

            if os.path.islink( srcFile ):
                target = os.readlink( srcFile )
                os.symlink( target, dstFile )
            else:
                shutil.copy2( srcFile, dstFile )


    def run_symlink( self ):
        """
            Symlinks all previously added / detected files within the output
            directory.
        """
        logging.debug( 'linking %d files... (this may take some time)' % \
                       len( self.fileDict.keys() ) )

        for original, target in self.fileDict.items():
            srcFile = original
            dstFile = self.path + os.sep + target

            logging.debug( 'linking %s -> %s' % ( dstFile, srcFile ) )

            FastScript.mkdir( os.path.dirname( dstFile ) )
            try:
                os.symlink( srcFile, dstFile )
            except OSError:
                fileName           = os.path.basename( target )
                linkTargetSupposed = srcFile
                linkTargetActual   = os.readlink( dstFile )

                if os.path.realpath( linkTargetActual ) != \
                   os.path.realpath( linkTargetSupposed ):

                    logging.warning( '' )
                    logging.warning( 'library name clash: %s' % fileName )
                    logging.warning( 'symlink exists: %s (pointing to %s)' % ( dstFile, linkTargetActual ) )
                    logging.warning( 'attempting to create link %s pointing to %s' % ( dstFile, linkTargetSupposed ) )
                    logging.warning( '' )


    def setLibraryCheck( self, status ):
        """
            Toggle if LibIndex should detect if multiple versions of the
            same library clash. This may be used to detect incompatible
            components for RTBOS.

            Default: off (False)
        """
        Any.requireIsBool( status )

        self.libCheck = status

        if status:
            logging.debug( 'symbol-clash detection: enabled' )
        else:
            logging.debug( 'symbol-clash detection: disabled' )


    def setPlatforms( self, platformList ):
        """
            Specify the list of platforms to be considered when scanning
            SIT packages for libraries etc.

            Limiting the platform to one or two will speed-up the LibIndex
            generation time and reduce necessary diskspace.
        """
        Any.requireIsListNonEmpty( platformList )

        self.platforms = platformList
        logging.debug( 'limiting platforms to: %s' % ' '.join( self.platforms ) )


    def showProgress( self, boolean ):
        Any.requireIsBool( boolean )

        self._showProgress = boolean


#----------------------------------------------------------------------------
# Popular filter functions
#----------------------------------------------------------------------------


def addLibraries( index, canonicalPath ):
    """
        LibIndex filter function which will generate an RTBOS-compatible
        index directory. It searches for:

          * <canonicalPath>/lib/${MAKEFILE_PLATFORM}
          * <canonicalPath>/${MAKEFILE_PLATFORM}/lib

        If a file <canonicalPath>/SkipLibIndex exists, this package will
        be ignored.

        If a file <canonicalPath>/LinkAllLibraries exists, all libraries
        in the above directories will be indexed. By default it will only
        search for a "libMyPackage.1.0.so" (package name / version).

        It will keep the original directory structure.
    """
    Any.requireIsTextNonEmpty( canonicalPath )
    Any.requireIsList( index.platforms )

    if canonicalPath in index.pkgList:
        logging.debug( 'skipping %s (already added)' % canonicalPath )
        return
    else:
        logging.debug( 'adding %s' % canonicalPath )
        index.pkgList.append( canonicalPath )

    installRoot = index.sitPath + os.sep + canonicalPath

    Any.requireMsg( os.path.exists( installRoot ),
                       "%s: No such package in SIT" % installRoot )

    linkAll_fileName = installRoot + os.sep + 'LinkAllLibraries'
    linkAll          = os.path.exists( linkAll_fileName )

    if linkAll:
        logging.debug( "%s: LinkAllLibraries found" % canonicalPath )


    # standard directory layout (lib/<platform>)

    match = fnmatch.fnmatch

    for platform in index.platforms:
        tail     = 'lib'       + os.sep + platform
        libDir   = installRoot + os.sep + tail
        fileList = FastScript.getFilesInDir( libDir )

        for fileName in fileList:

            filePath = libDir + os.sep + fileName

            if ( linkAll                       == True ) or \
               ( match( fileName, '*.so.*.*' ) == True ) or \
               ( match( fileName, '*.syms'   ) == True ) or \
               ( match( fileName, '*.dll*'   ) == True ) or \
               ( match( fileName, '*.so*'    ) == True and os.path.islink( filePath ) == False ) or \
               ( match( fileName, '*.lib*'   ) == True and os.path.islink( filePath ) == False ):

                srcFile_abs = filePath
                dstFile_rel = tail + os.sep + fileName

                if srcFile_abs not in index.fileDict.keys():
                    index.addFile( srcFile_abs, dstFile_rel )


    # reversed directory layout (<platform>/lib), as in OpenCV or Python

    for platform in index.platforms:
        tail     = platform    + os.sep + 'lib'
        libDir   = installRoot + os.sep + tail
        fileList = FastScript.getFilesInDir( libDir )

        for fileName in fileList:

            filePath = libDir + os.sep + fileName

            # the filename patterns below have been taken 1:1 from original
            # PHP implementation

            if ( linkAll                           == True ) or \
               ( match( fileName, '*.so.*.*'   ) == True ) or \
               ( match( fileName, '*.dll*'     ) == True ) or \
               ( match( fileName, '*.so*'      ) == True and os.path.islink( filePath ) == False ) or \
               ( match( fileName, '*.lib*'     ) == True and os.path.islink( filePath ) == False ):

                srcFile_abs = filePath
                dstFile_rel = tail + os.sep + fileName

                if srcFile_abs not in index.fileDict.keys():
                    index.addFile( srcFile_abs, dstFile_rel )


def fuseIntoSingleDirectory( index, canonicalPath ):
    """
        This LibIndex filter function differs from the RTBOS LibIndex
        filter function in the following way:

        *All* regular files and symlinks from the lib directories
        (in both normal and inverse directory layout style) get fused into
        the same single output directory.

        This implies that Matlab Mexfiles are included, too.
        Note that Python *.egg files are excluded for now (no need).

        The files skipLibIndex and linkAllLibraries are not considered.
    """
    Any.requireIsTextNonEmpty( canonicalPath )
    Any.requireIsList( index.platforms )

    if canonicalPath in index.pkgList:
        logging.debug( 'skipping %s (already added)' % canonicalPath )
        return
    else:
        logging.debug( 'adding %s' % canonicalPath )
        index.pkgList.append( canonicalPath )

    installRoot = index.sitPath + os.sep + canonicalPath

    Any.requireMsg( os.path.exists( installRoot ),
                       "%s: No such package in SIT" % installRoot )


    #--- above this line it is equal to addLibraries(), below is specific ---

    # standard directory layout (lib/<platform>)

    for platform in index.platforms:
        tail     = 'lib'       + os.sep + platform
        libDir   = installRoot + os.sep + tail
        fileList = FastScript.getFilesInDir( libDir )

        for fileName in fileList:
            srcFile_abs = libDir   + os.sep + fileName
            dstFile_rel = platform + os.sep + fileName

            if not fileName.endswith( '.egg-info' )      and \
               not fileName.endswith( '.py' )            and \
               not fileName.endswith( '.pth' )           and \
               srcFile_abs not in index.fileDict.keys():

                index.addFile( srcFile_abs, dstFile_rel )


    # reversed directory layout (<platform>/lib), as in OpenCV or Python

    for platform in index.platforms:
        tail     = platform    + os.sep + 'lib'
        libDir   = installRoot + os.sep + tail
        fileList = FastScript.getFilesInDir( libDir )

        for fileName in fileList:
            srcFile_abs = libDir   + os.sep + fileName
            dstFile_rel = platform + os.sep + fileName

            if not fileName.endswith( '.egg-info' )      and \
               not fileName.endswith( '.py' )            and \
               not fileName.endswith( '.pth' )           and \
               srcFile_abs not in index.fileDict.keys():

                index.addFile( srcFile_abs, dstFile_rel )


    # main programs

    for platform in index.platforms:
        tail     = 'bin'       + os.sep + platform
        libDir   = installRoot + os.sep + tail
        fileList = FastScript.getFilesInDir( libDir )

        for fileName in fileList:
            srcFile_abs = libDir   + os.sep + fileName
            dstFile_rel = platform + os.sep + fileName

            if srcFile_abs not in index.fileDict.keys():
                index.addFile( srcFile_abs, dstFile_rel )


def addMainPackage( index, canonicalPath ):
    """
        LibIndex filter function similar to addLibraries(), but will also
        add the "bin" directory.

        It keeps the original directory structure.
    """
    Any.requireIsTextNonEmpty( canonicalPath )
    Any.requireIsList( index.platforms )

    if canonicalPath in index.pkgList:
        logging.debug( 'skipping %s (already added)' % canonicalPath )
        return
    else:
        logging.debug( 'adding %s' % canonicalPath )
        index.pkgList.append( canonicalPath )

    installRoot = index.sitPath + os.sep + canonicalPath

    Any.requireMsg( os.path.exists( installRoot ),
                       "%s: No such package in SIT" % installRoot )

    linkAll_fileName = installRoot + os.sep + 'LinkAllLibraries'
    linkAll          = os.path.exists( linkAll_fileName )
    match            = fnmatch.fnmatch

    if linkAll:
        logging.debug( "%s: LinkAllLibraries found" % canonicalPath )

    for platform in index.platforms:
        tail     = 'lib'       + os.sep + platform
        libDir   = installRoot + os.sep + tail
        fileList = FastScript.getFilesInDir( libDir )

        for fileName in fileList:

            filePath = libDir + os.sep + fileName

            if ( linkAll                           == True ) or \
               ( match( fileName, '*.so.*.*'   ) == True ) or \
               ( match( fileName, '*.dll*' ) == True ) or \
               ( match( fileName, '*.so*'      ) == True and os.path.islink( filePath ) == False ) or \
               ( match( fileName, '*.lib*'     ) == True and os.path.islink( filePath ) == False ):

                srcFile_abs = filePath
                dstFile_rel = tail + os.sep + fileName

                if srcFile_abs not in index.fileDict.keys():
                    index.addFile( srcFile_abs, dstFile_rel )


        tail     = 'bin'       + os.sep + platform
        binDir   = installRoot + os.sep + tail
        fileList = FastScript.getFilesInDir( binDir )

        for fileName in fileList:

            srcFile_abs = binDir + os.sep + fileName
            dstFile_rel = tail   + os.sep + fileName

            if srcFile_abs not in index.fileDict.keys():
                index.addFile( srcFile_abs, dstFile_rel )


def exportLibraryPath( LibIndexDir, platformName ):
    """
        Adds the two directories within <LibIndexDir> to LD_LIBRARY_PATH:

           * LibIndexDir/<platform>/lib
           * LibIndexDir/lib/<platform>
    """
    Any.requireIsDir( LibIndexDir )

    oldLDPath  = FastScript.getEnv( 'LD_LIBRARY_PATH' )
    newLDPath  = oldLDPath

    candidates = [ os.path.join( LibIndexDir, platformName, 'lib' ),
                   os.path.join( LibIndexDir, 'lib', platformName ) ]


    for dirPath in candidates:

        if os.path.exists( dirPath ):
            newLDPath = '%s:%s' % ( dirPath, newLDPath )


    FastScript.setEnv( 'LD_LIBRARY_PATH', newLDPath )


# EOF
