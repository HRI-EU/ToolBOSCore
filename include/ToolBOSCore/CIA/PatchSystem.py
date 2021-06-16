# -*- coding: utf-8 -*-
#
#  Continuous Integration & Automation (CIA) framework
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
import io
import logging
import re
import os
import shutil
import subprocess

from ToolBOSCore.Packages                 import PackageCreator
from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.Storage                  import CMakeLists
from ToolBOSCore.Storage.PkgInfoInterface import PkgInfoInterface
from ToolBOSCore.Storage                  import VersionControl
from ToolBOSCore.Util                     import Any, FastScript


class PatchSystem( object ):
    """
        Generic container for frequently changing statistics and patches
        that shall be executed within the Continuous Integration system.
    """
    def __init__( self, topLevelDir=None ):
        if topLevelDir is None:
            topLevelDir = os.getcwd()

        self.details = PackageDetector( topLevelDir )
        self.details.retrieveMakefileInfo()

    def _patchCIA681( self, dryRun=False ):
        """
            Replaces "make unpack" in pre-configure.sh by direct call to
            "UnpackSources.sh".
        """
        fileName = 'pre-configure.sh'
        old      = "make unpack"
        new      = "${TOOLBOSCORE_ROOT}/include/UnpackSources.sh"
        status   = self._replace( fileName, old, old, new, 'CIA-680', dryRun )

        if status:
            return [ fileName ]


    def _patchCIA727( self, dryRun=False ):
        """
            Upgrade XIF packages to SplitterBBCMMaker 1.3
        """
        # Part 1: update SplitterBBCMMaker version in pre-configure.sh

        fileName1 = 'pre-configure.sh'
        old       = 'SplitterBBCMMaker/1.2/bin/MakeDataWrapper.sh'
        new       = 'SplitterBBCMMaker/1.3/bin/MakeDataWrapper.sh'
        status    = self._replace( fileName1, old, old, new, 'CIA-727a', dryRun )


        # Part 2: update SplitterBBCMMaker version in post-install.sh

        if status:
            # Note: The old post-install.sh files contain a lot of
            # additional code. We agreed to completely replace such scripts
            # with a one-liner script

            fileName2 = 'post-install.sh'
            old       = 'SplitterBBCMMaker/1.2/bin/MakeSplitterBBCM.sh'
            new       = '#!/bin/bash\n' + \
                        '$SIT/DevelopmentTools/SplitterBBCMMaker/1.3/bin/MakeSplitterBBCM.sh ' + \
                        '%s . %s\n\n' % ( self.details.packageName,
                                          self.details.packageVersion )

            # this does a replacement within the file, which is undesired...
            status2 = self._replace( fileName2, old, old, new, 'CIA-727b', dryRun )

            if status2 == True and dryRun == False:
                # ...instead we want to get rid of extra code and reset
                # the entire file content, effectively shortening the file
                FastScript.setFileContent( fileName2, new )

            return [ fileName1, fileName2 ]

        else:
            return False


    def _patchCIA765( self, dryRun=False ):
        """
            Upgrades the XIF package versions.
        """
        return self._dependencyUpgrade( dryRun, _getReplacementMap_XIF(), 'CIA-765' )


    def _patchCIA866( self, dryRun=False ):
        """
            Remove invalid pkgInfo.py from BBCMs / BBDMs / VMs that were
            erronously added at a very early time when pkgInfo.py was
            introduced.
        """
        fileName = 'pkgInfo.py'
        modified = []

        if not self.details.packageCategory:
            logging.error( 'CMakeLists.txt: No such file' )
            return []

        if self.details.packageCategory.startswith( 'Modules' ) and \
           os.path.exists( fileName ):

            output = io.StringIO()
            modified.append( fileName )

            try:
                if not dryRun:
                    vcs = VersionControl.auto()
                    vcs.remove( fileName, output=output )
            except subprocess.CalledProcessError:
                pass        # maybe using git

        return modified


    # def _patchCIA868( self, dryRun=False ):
    #     """
    #         Replace old CMakeLists.txt files by new ones from the package
    #         templates in order to spread the new CMake build rules for Matlab
    #         wrapper generation.
    #     """
    #     fileName = 'wrapper/CMakeLists.txt'
    #     template = os.path.join( PackageCreator.templateDir,
    #                              'HDot_Component_Evaluation',
    #                              'CMakeLists.txt' )
    #
    #     Any.requireIsFileNonEmpty( template )
    #
    #     try:
    #         oldContent = FastScript.getFileContent( fileName )
    #     except IOError:
    #         # package is not affected (has no wrapper code)
    #         return False
    #
    #     if oldContent.find( 'bst_build_wrapper' ) == -1:
    #         shutil.copyfile( template, fileName )
    #         return [ fileName ]
    #     else:
    #         return False


    def _patchCIA923( self, dryRun=False ):
        """
            Updates the script path in pre-configure.sh from:
                ${TOOLBOSCORE_ROOT}/make/UnpackSources.sh
            to:
                ${TOOLBOSCORE_ROOT}/include/UnpackSources.sh

        """
        fileName = 'pre-configure.sh'
        old      = '${TOOLBOSCORE_ROOT}/make/UnpackSources.sh'
        new      = '${TOOLBOSCORE_ROOT}/include/UnpackSources.sh'
        status   = self._replace( fileName, old, old, new, 'CIA-923', dryRun )

        if status:
            return [ fileName ]


    def _patchCIA955( self, dryRun=False ):
        """
            BST.py requires CMake 2.8.8 for building library packages.

            However the CMakeLists.txt template stated a minimum required
            version of "2.6" which should be replaced by "2.8.8" accordingly.

            Otherwise the user will receive strange error messages when trying
            to compile with an older version than 2.8.8.
        """
        fileName = 'CMakeLists.txt'
        old      = 'cmake_minimum_required(VERSION 2.6)'
        new      = 'cmake_minimum_required(VERSION 2.8.8)'
        status   = False

        # This patch is only necessary if the package is about building
        # libraries

        try:
            content = FastScript.getFileContent( fileName )
        except IOError:
            logging.debug( '%s: No such file', fileName )
            return False


        if 'bst_build_libraries' in content or 'add_library' in content:
            status = self._replace( fileName, old, old, new, 'CIA-955', dryRun )
        else:
            logging.debug( 'neither bst_build_libraries() nor add_library() found' )

        if status:
            return [ fileName ]


    def _patchCIA977( self, dryRun=False ):
        """
            Updates the Makefile of a BBCM component to call "MakeBBCM.py"
            instead of "RunTemplate.php".
        """
        if not self.details.isBBCM():
            logging.debug( 'package is not a BBCM' )
            return False

        srcFile    = os.path.join( PackageCreator.templateDir, 'C_BBCM', 'Makefile' )
        dstFile    = 'Makefile'

        if not os.path.exists( dstFile ):
            logging.debug( 'package has no Makefile, patch does not apply' )
            return False

        srcContent = FastScript.getFileContent( srcFile )
        dstContent = FastScript.getFileContent( dstFile )

        if srcContent != dstContent:
            if not dryRun:
                FastScript.copy( srcFile, dstFile )
            else:
                logging.debug( '[DRY-RUN] cp %s %s', srcFile, dstFile )

            return [ dstFile ]
        else:
            return False


    def _patchCIA982( self, dryRun=False ):
        """
            Check (and evtl. set) a build-dependency if ToolBOSPluginMatlab
            is included within a separate CMakeLists.txt.
        """
        cmakeFile = 'wrapper/CMakeLists.txt'

        if not os.path.exists( cmakeFile ):
            logging.debug( '%s: No such file', cmakeFile )
            return False

        cmakeContent = FastScript.getFileContent( cmakeFile )
        Any.requireIsTextNonEmpty( cmakeContent )

        # check if dependencies included in the wrapper/CMakeLists.txt
        # appear in the normally detected depends/buildDepends sections
        #
        # if not, then add it at least as a build-dependency

        newBuildDeps = copy.copy( self.details.buildDependencies )

        for package in CMakeLists.getDependencies( cmakeContent ):
            Any.requireIsTextNonEmpty( package )

            if package not in self.details.dependencies and \
               package not in self.details.buildDependencies:
                logging.info( 'adding build-dependency: %s', package )

                newBuildDeps.append( package )


        # if some additional build-dependencies have been found then store
        # them into pkgInfo.py
        if self.details.buildDependencies != newBuildDeps:
            p = PkgInfoInterface( self.details )
            p.set( 'buildDepends', newBuildDeps )

            if not dryRun:
                p.write()

            return [ 'pkgInfo.py' ]
        else:
            return False


    def _patchCIA988( self, dryRun=False ):
        """
            Removes legacy PHP files from repository.
        """
        candidates = ( 'packageVar.php',
                       self.details.packageName + '.php' )  # in old BBCMs

        result     = []

        for fileName in candidates:
            if os.path.exists( fileName ):

                if not dryRun:
                    try:
                        vcs = VersionControl.auto()
                        vcs.remove( fileName )
                    except subprocess.CalledProcessError:
                        # maybe using git
                        FastScript.remove( fileName )

                result.append( fileName )

        return result


    def _patchCIA989( self, dryRun=False ):
        """
            Removes legacy ANY_DEF_*_TAG macros.
        """
        if self.details.canonicalPath.find( 'DevelopmentTools/ToolBOS' ) == -1 and \
           self.details.canonicalPath.find( 'Libraries/ToolBOSLib'     ) == -1 and \
           self.details.canonicalPath.find( 'Applications/ToolBOS'     ) == -1:

            result = []
            ticket = 'CIA-989'

            pkgNameUpper  = self.details.packageName.upper()
            srcTagPattern = re.compile( '(ANY_DEF_SRCTAG\s?\(.*?\);)', re.DOTALL )

            for fileName in FastScript.getFilesInDir( 'src' ):
                fileName = os.path.join( 'src', fileName )
                modified = False
                new      = ''

                old = 'ANY_DEF_BINTAG;\n'
                if self._replace( fileName, old, old, new, ticket, dryRun ):
                    modified |= True


                old = '/* File tag */\n'
                if self._replace( fileName, old, old, new, ticket, dryRun ):
                    modified |= True


                old = '/*---------------------------------------------*/\n' + \
                      '/* File tag                                    */\n' + \
                      '/*---------------------------------------------*/\n'
                if self._replace( fileName, old, old, new, ticket, dryRun ):
                    modified |= True


                old = '#define %s_C_SRCTAG\n' % pkgNameUpper
                if self._replace( fileName, old, old, new, ticket, dryRun ):
                    modified |= True


                old = '#undef %s_C_SRCTAG\n' % pkgNameUpper
                if self._replace( fileName, old, old, new, ticket, dryRun ):
                    modified |= True


                content = FastScript.getFileContent( fileName )

                tmp = srcTagPattern.search( content )

                if tmp:
                    old = tmp.group(1)
                    if self._replace( fileName, old, old, new, ticket, dryRun ):
                        modified |= True


                # use the occasion and replace some more clutter
                old = '/* Temporary solution for a local debug level */\n'
                if self._replace( fileName, old, old, new, ticket, dryRun ):
                    modified |= True


                # remove too many empty lines left-over from previous replacements
                if modified:
                    old = '\n\n\n\n\n'
                    new = '\n\n'
                    self._replace( fileName, old, old, new, ticket, dryRun )

                    result.append( fileName )

        else:

            logging.debug( 'skipping ToolBOS packages to not patch backward-compatibility layers' )

            return []


    def _patchCIA1094( self, dryRun=False ):
        """
            Replace fixed values of valid-flags by randomized value to
            discover memory problems.
        """
        old1      = '0x900db00f'
        old2      = '0xdeadb00f'
        result    = []
        ticket    = 'CIA-1094'
        whitelist = [ '.c', '.h', '.cpp', '.hpp', '.inc' ]


        def check( fileName ):
            Any.requireIsFile( fileName )

            content = FastScript.getFileContent( fileName )

            return content.find( old1 ) != -1 or \
                   content.find( old2 ) != -1



        for fileName in FastScript.findFiles( 'src', ext=whitelist ):
            modified = False


            while check( fileName ):
                new1, new2 = PackageCreator.randomizeValidityFlags()

                # search for boilerplate valid-flag
                if self._replace( fileName, old1, old1, new1, ticket, dryRun, 1 ):
                    modified |= True

                # search for boilerplate invalid-flag
                if self._replace( fileName, old2, old2, new2, ticket, dryRun, 1 ):
                    modified |= True


            if modified:
                result.append( fileName )


        return result


    def _patchCIA1112( self, dryRun=False ):
        """
            Replace legacy HRI_GLOBAL_ROOT variable by SIT, except for
            BBML graph files where this is part of the specification.
        """
        old       = 'HRI_GLOBAL_ROOT'
        new       = 'SIT'
        result    = []
        ticket    = 'CIA-1112'
        whitelist = [ '.bat', '.c', '.h', '.cpp', '.hpp', '.inc', '.py',
                      '.sh',
                      '.cmake',             # e.g. packageVar.cmake
                      ''                    # e.g. BashSrc (no extension)
                      ]


        # do not patch the ToolBOS package itself, otherwise this function
        # would be patched to replace "SIT" by "SIT" ;-)
        #
        # We generally assume that the ToolBOS packages themselves are
        # clean from legacy occurrences.

        if self.details.canonicalPath.find( 'DevelopmentTools/ToolBOS' ) == -1 and \
           self.details.canonicalPath.find( 'Applications/ToolBOS'     ) == -1:

            for fileName in FastScript.findFiles( '.', ext=whitelist ):
                modified = self._replace( fileName, old, old, new, ticket, dryRun )

                if modified:
                    result.append( fileName )

            return result

        else:

            logging.debug( 'skipping ToolBOS packages to not patch backward-compatibility layers' )

            return []


    def _patchCIA1143( self, dryRun=False ):
        """
            Replace legacy C macro ANY_TNALLOC by ANY_NTALLOC for
            consistency reasons with the order of the parameters.
        """
        old       = 'ANY_TNALLOC'
        new       = 'ANY_NTALLOC'
        result    = []
        ticket    = 'CIA-1143'
        whitelist = [ '.c', '.h', '.cpp', '.hpp', '.inc' ]


        # do not patch the ToolBOS package itself, otherwise this function
        # would patch the deprecated ANY_TNALLOC macro itself, which is
        # kept for compatibility reasons.
        #
        # We generally assume that the ToolBOS packages themselves are
        # clean from legacy occurrences.

        if self.details.canonicalPath.find( 'DevelopmentTools/ToolBOS' ) == -1 and \
           self.details.canonicalPath.find( 'Libraries/ToolBOSLib'     ) == -1:

            for fileName in FastScript.findFiles( '.', ext=whitelist ):
                modified = self._replace( fileName, old, old, new, ticket, dryRun )

                if modified:
                    result.append( fileName )

            return result

        else:

            logging.debug( 'skipping ToolBOS packages to not patch backward-compatibility layers' )

            return []


    def _patchCIA1147( self, dryRun=False ):
        """
            Remove obsolete BBCM_INFO_CATEGORY.
        """
        if not self.details.isBBCM():
            logging.debug( 'package is not a BBCM' )
            return False

        fileName = 'src/%s_info.c' % self.details.packageName

        if not os.path.exists( fileName ):
            return False


        lines      = FastScript.getFileContent( fileName, splitLines=True )
        modified   = []
        newContent = ''

        for line in lines:
            if line.startswith( 'BBCM_INFO_CATEGORY' ):
                modified.append( fileName )
            else:
                newContent += line

        if modified and dryRun is False:
            FastScript.setFileContent( fileName, newContent )


        return modified


    def _patchCIA1185( self, dryRun=False ):
        """
            Upgrades the ToolBOS SDK dependency.

            So far packages included "DevelopmentTools/ToolBOSCore/2.0" but
            we don't know if actually the build system related part or the
            core library was used from it.

            Updating to ToolBOSLib/3.0 to be on the safe side, and it has
            ToolBOSCore/3.0 as dependency. If we include more than needed
            people can manually reduce the dependency to ToolBOSCore/3.0
            only, otherwise it typically won't harm anyways.
        """
        if self.details.canonicalPath.find( 'DevelopmentTools/ToolBOSCore' ) == -1:
            # other ToolBOS packages like ToolBOSLib etc. should not have a
            # problem if we attempt to patch them (although no patch needed)

            return self._dependencyUpgrade( dryRun, _getReplacementMap_ToolBOS(), 'CIA-1185' )

        else:

            logging.debug( 'skipping ToolBOS packages to not patch backward-compatibility layers' )

            return []


    def _patchCIA1191( self, dryRun=False ):
        """
            Replaces the dependency to AllPython 2.7 by Anaconda2 5.2
        """
        return self._dependencyUpgrade( dryRun, _getReplacementMap_Anaconda2(), 'CIA-1191' )


    def _patchCIA1216( self, dryRun=False ):
        """
            Upgrades all Matlab versions in use to latest release by today (9.4).
        """
        return self._dependencyUpgrade( dryRun, _getReplacementMap_Matlab94(), 'CIA-1216' )


    def _patchCIA1226( self, dryRun=False ):
        """
            Upgrades all the BPL libraries from 7.1 --> 7.2.
        """
        return self._dependencyUpgrade( dryRun, _getReplacementMap_BPL72(), 'CIA-1226' )


    def _patchCIA1237( self, dryRun=False ):
        """
            Upgrades ToolBOSLib from 3.0 --> 3.1.
        """
        if self.details.packageName == 'ToolBOSLib':
            logging.debug( 'skipping ToolBOS packages to not patch backward-compatibility layers' )
            return []

        else:

            return self._dependencyUpgrade( dryRun, _getReplacementMap_ToolBOSLib31(), 'CIA-1237' )


    def _patchCIA1238( self, dryRun=False ):
        """
            Upgrades all the BBDMs from 1.7 --> 1.8.
        """
        return self._dependencyUpgrade( dryRun, _getReplacementMap_BBDM18(), 'CIA-1238' )



    def _patchCIA1239( self, dryRun=False ):
        """
            Upgrades all RTMaps versions in use to latest release by today (4.5.6).
        """
        return self._dependencyUpgrade( dryRun, _getReplacementMap_RTMaps456(), 'CIA-1239' )


    def _patchCIA1251( self, dryRun=False ):
        """
            Upgrades components from ToolBOS Middleware from 3.0 --> 3.3.
        """
        if self.details.isComponent():
            return self._dependencyUpgrade( dryRun, _getReplacementMap_Middleware33(), 'CIA-1251' )

        else:
            return False


    def _patchCIA1265( self, dryRun=False ):
        """
            Checks BBCM package for included outdated headerfiles and
            replaces them with the nowadays version.
            Duplicates will be deleted.
        """
        if not self.details.isBBCM():
            return False

        # Get a list of all files to check
        files    = FastScript.getFilesInDirRecursive( 'src' )
        modified = []

        # Check every file
        for filePath in files:
            logging.debug( 'processing %s', filePath )

            # Only rewrite line if changed
            rewrite = False
            # Get file content
            fileContent = FastScript.getFileContent( filename=filePath,
                                                     splitLines=True )
            # Check every line
            for line in fileContent:
                item = line.split()

                # Check for include statement
                if line.find( '#include <BBDM' ) != -1:
                    # Replace old package names with the nowadays form
                    match = re.search( r"-A|-CID|-S", item[ 1 ] )
                    if match:
                        fileContent[ fileContent.index( line ) ] = re.sub(
                            r"-A|-CID|-S", "", line )
                        rewrite = True

            includes = []

            # Check file backwards
            for line in reversed( fileContent ):
                item = line.split()

                if line.find( '#include <BBDM' ) != -1:
                    # Check for duplicates and remove existing ones
                    if line in includes:
                        rewrite = True
                        fileContent.remove( line )

                    # add to list of known includes
                    else:
                        includes.append( line )

            # Overwrite file with new content
            try:
                if rewrite:
                    if dryRun:
                        logging.info( '[DRY-RUN] patching %s', filePath )
                    else:
                        logging.info( 'patching %s', filePath )
                        newContent = ''.join( fileContent )
                        FastScript.setFileContent( filePath, newContent )

                    modified.append( filePath )

            except IOError as e:
                logging.error( e )

        return modified


    def _patchCIA1267( self, dryRun=False ):
        """
            Check files for outdated CSV keywords and remove
            these keywords and expanded information from the source code
        """
        files    = FastScript.getFilesInDirRecursive( 'bin' ) | \
                   FastScript.getFilesInDirRecursive( 'examples' ) | \
                   FastScript.getFilesInDirRecursive( 'src' ) | \
                   FastScript.getFilesInDirRecursive( 'test' )

        modified = []

        # CSV keywords
        keywords = frozenset( [ '$Author', '$Date', '$Header', '$Id', '$Log',
                                '$Locker', '$Name', '$RCSfile', '$Revision',
                                '$Source', '$State' ] )

        for filePath in files:
            rewrite     = False

            try:
                fileContent = FastScript.getFileContent( filename=filePath,
                                                         splitLines=True )
            except UnicodeDecodeError:
                # most probably we attempt to read a binary file,
                # e.g. a compiled executable under bin/ or the like
                continue

            # check each line for CSV keyword and remove line if found
            for line in fileContent:
                if any( key in line for key in keywords):
                    rewrite = True
                    fileContent.remove( line )

            if rewrite:
                if dryRun:
                    logging.info( '[DRY-RUN] patching %s', filePath )
                else:
                    logging.info( 'patching %s', filePath )
                    newContent = ''.join( fileContent )
                    FastScript.setFileContent( filePath, newContent )

                modified.append( filePath )

        return modified


    def _patchCIA1301( self, dryRun=False ):
        """
            Check files for outdated CSV keywords and remove
            these keywords and expanded information from the source code
        """
        cmakeFile = 'CMakeLists.txt'

        if not os.path.exists( cmakeFile ):
            logging.debug( 'package has no %s, patch does not apply', cmakeFile )
            return False

        oldContent = FastScript.getFileContent( cmakeFile )

        if 'cmake_minimum_required' not in oldContent:
            logging.debug( '\'cmake_minimum_required()\' not found' )
            logging.debug( 'package seems to not need compilation, patch does not apply' )
            return False

        found = re.search( r'(project\s*\(.+\))', oldContent )

        if found:
            logging.debug( 'found: %s', found.group(1) )
            modified = []
        else:
            logging.debug( '\'project(Name)\' not found')

            packageName = self.details.packageName
            newContent = re.sub( r'(cmake_minimum_required\s*?\(.*?\)\n)',
                                 r'\g<1>\nproject(%s)\n' % packageName,
                                 oldContent )

            Any.requireIsTextNonEmpty( newContent )
            FastScript.setFileContent( cmakeFile, newContent )

            modified = [ cmakeFile ]

        return modified


    def getPatchesAvailable( self ):
        """
            Returns a list of available patches, each item in the list
            belongs to one patch.

            Each item in the list is a tuple of three elements:
               * description
               * function pointer
               * meaningful SVN commit message as specified by the patch
                 author, could be used if patches are applied in batch mode
        """
        result = [ ( '"make unpack" does not work in CMake-only packages (CIA-689)',
                     self._patchCIA681,
                     "pre-configure.sh: replaced 'make unpack' by call to 'UnpackSources.sh'" ),

                   ( 'upgrade SplitterBBCMMaker version to 1.3 (CIA-727)',
                     self._patchCIA727,
                     'upgraded SplitterBBCMMaker version to 1.3 (CIA-727)' ),

                   ( 'upgrade XIF package versions (CIA-765)',
                     self._patchCIA765,
                     'upgraded XIF package versions (CIA-765)' ),

                   # ( 'update MEX building rules in H.Dot packages (CIA-868)',
                   #   self._patchCIA868,
                   #   'updated Matlab wrapper build rules (CIA-868)' ),

                   ( 'pre-configure.sh update (CIA-923)',
                      self._patchCIA923,
                     'updated path of UnpackSources.sh script (CIA-923)' ),

                   ( 'bst_build_libraries() requires CMake 2.8.8 (CIA-955)',
                     self._patchCIA955,
                     'CMakeLists.txt: updated min. CMake version to 2.8.8' ),

                   ( "run 'MakeBBCM.py' instead of 'make BBCM' (CIA-977)",
                     self._patchCIA977,
                     'Makefile: replaced call to RunTemplate.php by MakeBBCM.py (CIA-977)' ),

                   ( 'add dependency to ToolBOSPluginMatlab (CIA-982)',
                     self._patchCIA982,
                     'pkgInfo.py: added build-dependencies (CIA-982)' ),

                   ( 'repository clean-up (CIA-988)',
                     self._patchCIA988,
                     'removed legacy / unused PHP files (CIA-988)' ),

                   ( 'remove legacy ANY_DEF_*_TAG macros (CIA-989)',
                     self._patchCIA989,
                     'removed legacy ANY_DEF_*_TAG and related macros (CIA-989)' ),

                   ( 'update valid-flags to detect memory problems (CIA-1094)',
                     self._patchCIA1094,
                     'replaced boilerplate valid-flags to better detect memory problems (CIA-1094)' ),

                   ( 'replace $HRI_GLOBAL_ROOT by $SIT (CIA-1112)',
                     self._patchCIA1112,
                     'replaced $HRI_GLOBAL_ROOT by $SIT (CIA-1112)' ),

                   ( 'replace ANY_TNALLOC by ANY_NTALLOC (CIA-1143)',
                     self._patchCIA1143,
                     'replaced ANY_TNALLOC by ANY_NTALLOC (CIA-1143)' ),

                   ( 'remove obsolete BBCM_INFO_CATEGORY (CIA-1147)',
                     self._patchCIA1147,
                     'removed obsolete BBCM_INFO_CATEGORY (CIA-1147)' ),

                   ( 'upgrading ToolBOS dependency (CIA-1185)',
                     self._patchCIA1185,
                     'upgraded ToolBOS dependency 2.0 --> 3.0 (CIA-1185)' ),

                   ( 'replacing dependency to AllPython by Anaconda (CIA-1191)',
                     self._patchCIA1191,
                     'replaced dependency to AllPython by Anaconda (CIA-1191)' ),

                   ( 'upgrading Matlab dependency (CIA-1216',
                     self._patchCIA1216,
                     'upgraded Matlab dependency (CIA-1216)' ),

                   ( 'upgrading BPL dependency (CIA-1226)',
                     self._patchCIA1226,
                     'upgraded BPL dependency 7.1 --> 7.2 (CIA-1226)' ),

                   ( 'upgrading ToolBOSLib dependency (CIA-1237)',
                     self._patchCIA1237,
                     'upgraded ToolBOSLib dependency 3.0 --> 3.1 (CIA-1237)' ),

                   ( 'upgrading BBDM dependency (CIA-1238)',
                     self._patchCIA1238,
                     'upgraded BBDM dependency 1.7 --> 1.8 (CIA-1238)' ),

                   ( 'upgrading RTMaps dependency (CIA-1239)',
                     self._patchCIA1239,
                     'upgraded RTMaps dependency to 4.56 (CIA-1239)' ),

                   ( 'replacing outdated BBDM filenames (CIA-1265)',
                     self._patchCIA1265,
                     'replaced BBDM headerfile names (CIA-1265)' ),

                   ( 'removing outdated CVS keywords (CIA-1267)',
                     self._patchCIA1267,
                     'removed outdated CVS keywords and related code (CIA-1267)' ),

                   ( 'adding \'project(Name)\' to CMakeLists.txt (CIA-1301)',
                     self._patchCIA1301,
                     'added \'project(Name)\' to CMakeLists.txt (CIA-1301)' ) ]

        return result


    def run( self, dryRun=False ):
        """
            Performs all patching routines, if dryRun=True all operations
            are fake (your project won't be altered).
        """
        available = self.getPatchesAvailable()
        descrLen  = 0
        applied   = []

        # determine the longest description to compute number of dashes
        for patch in available:
            descrLen = max( len(patch[0]), descrLen )
            descrLen = max( len(patch[2]), descrLen )


        logging.info( descrLen * '-' )

        for patch in available:
            logging.info( 'EXECUTING PATCH: %s', patch[0] )
            result = patch[1]( dryRun )

            if result:
                Any.requireIsList( result )
                fileList = FastScript.reduceList( result )
                fileList.sort()

                for item in fileList:
                    logging.info( 'patching %s', item )

                logging.info( patch[2] )

                applied.append( patch )
            else:
                logging.info( 'no need to patch' )

            logging.info( descrLen * '-' )

        logging.info( '' )

        return applied


    def runPatches_dependencyUpgrade( self ):
        """
            Executes all patches related to dependency upgrades, f.i.
            modify the CMakeLists.txt / packageVar.cmake / ... files.
        """
        self._patchCIA765()    # upgrade XIF


    def _replace( self, fileName, check, old, new, ticketID, dryRun, count=None ):
        """
            Checks if <fileName> contains <check>, and if so it replaces
            the string <old> by <new>.

            If dryRun=True the check for patch necessity will be executed
            normally, but then no files will be altered.

            Returns a boolean if the file was affected or not.
            Returns 'None' if the specified file was not found thus the
            patch might not be applicable.

            If the argument 'count' is given, only the first n occurrences
            will be replaced.
        """
        try:
            content = FastScript.getFileContent( fileName )

        except ( IOError, UnicodeDecodeError ):
            # UnicodeDecodeError may happen when attempting to read a binary
            # file (e.g. executable), skip those as they shall not be patched

            return False

        logging.debug( '%s: searching for "%s"', fileName, check.strip() )
        needed = content.find( check ) > 0
        logging.debug( 'patch "%s" --> "%s" needed: %s', \
                       old.strip(), new.strip(), str(needed) )

        if needed and not dryRun:

            if count is None:
                content = content.replace( old, new )
            else:
                content = content.replace( old, new, count )


            FastScript.setFileContent( fileName, content )

        return needed


    def _dependencyUpgrade( self, dryRun, replacementMap, ticketID ):
        """
            Patches the CMakeLists.txt / packageVar.cmake / ...
            files (if necessary) to include different packages.
        """
        Any.requireIsBool( dryRun )
        Any.requireIsDict( replacementMap )
        Any.requireIsTextNonEmpty( ticketID )

        status1  = False
        status2  = False
        status3  = False
        modified = []

        for old, new in replacementMap.items():
            status1 |= self._replace( 'CMakeLists.txt',   old, old, new, ticketID, dryRun )
            status2 |= self._replace( 'packageVar.cmake', old, old, new, ticketID, dryRun )
            status3 |= self._replace( 'pkgInfo.py',       old, old, new, ticketID, dryRun )

        if status1:
            modified.append( 'CMakeLists.txt' )

        if status2:
            modified.append( 'packageVar.cmake' )

        if status3:
            modified.append( 'pkgInfo.py' )

        return modified


#----------------------------------------------------------------------------
# Private functions
#----------------------------------------------------------------------------


def _getReplacementMap_Anaconda2():
    return { 'External/AllPython/2.7'              : 'External/anaconda2/5.2' }


def _getReplacementMap_BBDM18():
    return {
        'Modules/BBDM/BBDMAll/1.7'                 : 'Modules/BBDM/BBDMAll/1.8',
        'Modules/BBDM/BBDMArray2DPoint/1.7'        : 'Modules/BBDM/BBDMArray2DPoint/1.8',
        'Modules/BBDM/BBDMArray2DRect/1.7'         : 'Modules/BBDM/BBDMArray2DRect/1.8',
        'Modules/BBDM/BBDMArray2DSize/1.7'         : 'Modules/BBDM/BBDMArray2DSize/1.8',
        'Modules/BBDM/BBDMArrayBlockF32/1.7'       : 'Modules/BBDM/BBDMArrayBlockF32/1.8',
        'Modules/BBDM/BBDMArrayBlockI16/1.7'       : 'Modules/BBDM/BBDMArrayBlockI16/1.8',
        'Modules/BBDM/BBDMArrayBlockUI16/1.7'      : 'Modules/BBDM/BBDMArrayBlockUI16/1.8',
        'Modules/BBDM/BBDMArrayBlockUI8/1.7'       : 'Modules/BBDM/BBDMArrayBlockUI8/1.8',
        'Modules/BBDM/BBDMArrayF32/1.7'            : 'Modules/BBDM/BBDMArrayF32/1.8',
        'Modules/BBDM/BBDMArrayF64/1.7'            : 'Modules/BBDM/BBDMArrayF64/1.8',
        'Modules/BBDM/BBDMArrayI32/1.7'            : 'Modules/BBDM/BBDMArrayI32/1.8',
        'Modules/BBDM/BBDMArrayI64/1.7'            : 'Modules/BBDM/BBDMArrayI64/1.8',
        'Modules/BBDM/BBDMArrayMemI8/1.7'          : 'Modules/BBDM/BBDMArrayMemI8/1.8',
        'Modules/BBDM/BBDMArraySparseBlockF32/1.7' : 'Modules/BBDM/BBDMArraySparseBlockF32/1.8',
        'Modules/BBDM/BBDMBase2DF32/1.7'           : 'Modules/BBDM/BBDMBase2DF32/1.8',
        'Modules/BBDM/BBDMBase2DPoint/1.7'         : 'Modules/BBDM/BBDMBase2DPoint/1.8',
        'Modules/BBDM/BBDMBase2DRect/1.7'          : 'Modules/BBDM/BBDMBase2DRect/1.8',
        'Modules/BBDM/BBDMBase2DSize/1.7'          : 'Modules/BBDM/BBDMBase2DSize/1.8',
        'Modules/BBDM/BBDMBaseBool/1.7'            : 'Modules/BBDM/BBDMBaseBool/1.8',
        'Modules/BBDM/BBDMBaseF32/1.7'             : 'Modules/BBDM/BBDMBaseF32/1.8',
        'Modules/BBDM/BBDMBaseF64/1.7'             : 'Modules/BBDM/BBDMBaseF64/1.8',
        'Modules/BBDM/BBDMBaseI16/1.7'             : 'Modules/BBDM/BBDMBaseI16/1.8',
        'Modules/BBDM/BBDMBaseI32/1.7'             : 'Modules/BBDM/BBDMBaseI32/1.8',
        'Modules/BBDM/BBDMBaseI64/1.7'             : 'Modules/BBDM/BBDMBaseI64/1.8',
        'Modules/BBDM/BBDMBaseI8/1.7'              : 'Modules/BBDM/BBDMBaseI8/1.8',
        'Modules/BBDM/BBDMBlockF32/1.7'            : 'Modules/BBDM/BBDMBlockF32/1.8',
        'Modules/BBDM/BBDMBlockI16/1.7'            : 'Modules/BBDM/BBDMBlockI16/1.8',
        'Modules/BBDM/BBDMBlockI64/1.7'            : 'Modules/BBDM/BBDMBlockI64/1.8',
        'Modules/BBDM/BBDMBlockUI8/1.7'            : 'Modules/BBDM/BBDMBlockUI8/1.8',
        'Modules/BBDM/BBDMMemI8/1.7'               : 'Modules/BBDM/BBDMMemI8/1.8',
        'Modules/BBDM/BBDMSparseBlockF32/1.7'      : 'Modules/BBDM/BBDMSparseBlockF32/1.8' }



def _getReplacementMap_BPL72():
    # return {
    #     'Libraries/BPLBase/7.1'                    : 'Libraries/BPLBase/7.2',
    #     'Libraries/BPLMain_IPP/7.1'                : 'Libraries/BPLMain_IPP/7.2',
    #     'Libraries/BPLAddOns/BPL_ImageIO2_IPP/7.1' : 'Libraries/BPLAddOns/BPL_ImageIO2_IPP/7.2',
    #     'Libraries/BPLAddOns/BPL_OpenCV/7.1'       : 'Libraries/BPLAddOns/BPL_OpenCV/7.2',
    #     'Libraries/BPLAddOns/BPL_Shell_IPP/7.1'    : 'Libraries/BPLAddOns/BPL_Shell_IPP/7.2',
    #     'Libraries/BPLAddOns/BPL_SSBA/7.1'         : 'Libraries/BPLAddOns/BPL_SSBA/7.2' }

    return {
        'Libraries/BPLBase/7.1'                    : 'Libraries/BPLBase/7.2',
        'Libraries/BPLMain_IPP/7.1'                : 'Libraries/BPLMain_IPP/7.2' }


def _getReplacementMap_Boost():
    return { 'External/boost/1.48'                 : 'External/boost/1.54' }


def _getReplacementMap_Matlab94():
    return {
        'External/Matlab/8.4'                      : 'External/Matlab/9.4',
        'External/Matlab/9.0'                      : 'External/Matlab/9.4',
        'DevelopmentTools/ToolBOSPluginMatlab/1.2' : 'DevelopmentTools/ToolBOSPluginMatlab/1.4',
        'DevelopmentTools/ToolBOSPluginMatlab/1.3' : 'DevelopmentTools/ToolBOSPluginMatlab/1.4' }


def _getReplacementMap_Middleware33():
    return {
        'Applications/ToolBOS/Middleware/3.0'      : 'Applications/ToolBOS/Middleware/3.3',
        'Applications/ToolBOS/Middleware/3.1'      : 'Applications/ToolBOS/Middleware/3.3' }


def _getReplacementMap_RTMaps456():
    return {
        'External/RTMaps/4.2'                      : 'External/RTMaps/4.56',
        'External/RTMaps/4.3'                      : 'External/RTMaps/4.56',
        'External/RTMaps/4.5'                      : 'External/RTMaps/4.56',
        'External/RTMaps/98.0'                     : 'External/RTMaps/4.56',
        'External/RTMaps/99.0'                     : 'External/RTMaps/4.56' }


def _getReplacementMap_ToolBOS():
    return { 'DevelopmentTools/ToolBOSCore/2.0'    : 'Libraries/ToolBOSLib/3.0' }


def _getReplacementMap_ToolBOSLib31():
    return { 'Libraries/ToolBOSLib/3.0'            : 'Libraries/ToolBOSLib/3.1' }


def _getReplacementMap_XIF():
    return {
        'Libraries/Data/CarGestureStatus/1.0'      : 'Libraries/Data/CarGestureStatus/1.5',
        'Libraries/Data/EntityMeasurement/1.1'     : 'Libraries/Data/EntityMeasurement/1.5',
        'Libraries/Data/EntityMeasurement/2.0'     : 'Libraries/Data/EntityMeasurement/2.5',
        'Libraries/Data/MobilEyeData/1.1'          : 'Libraries/Data/MobilEyeData/1.5',
        'Libraries/Data/OIACC_OptimizationData/1.0': 'Libraries/Data/OIACC_OptimizationData/1.5',
        'Libraries/Data/RadarData/1.1'             : 'Libraries/Data/RadarData/1.5',
        'Libraries/Data/RadarData/1.2'             : 'Libraries/Data/RadarData/1.5',
        'Libraries/Data/RadarData/2.0'             : 'Libraries/Data/RadarData/2.5',
        'Libraries/Data/GpsData/1.3'               : 'Libraries/Data/GpsData/1.5',
        'Libraries/Data/IACCInputData/1.0'         : 'Libraries/Data/IACCInputData/1.5',
        'Libraries/Data/IACCInputData/2.1'         : 'Libraries/Data/IACCInputData/2.5',
        'Libraries/Data/IbeoLrfData/1.2'           : 'Libraries/Data/IbeoLrfData/1.5',
        'Libraries/Data/IMUData/1.3'               : 'Libraries/Data/IMUData/1.5',
        'Libraries/Data/LaneData/1.3'              : 'Libraries/Data/LaneData/1.5',
        'Libraries/Data/RadarDataLRR3/1.2'         : 'Libraries/Data/RadarDataLRR3/1.5',
        'Libraries/Data/SceneData/1.2'             : 'Libraries/Data/SceneData/1.5',
        'Libraries/Data/SimGroundTruth/1.1'        : 'Libraries/Data/SimGroundTruth/1.5',
        'Libraries/Data/TrackedEntity/1.4'         : 'Libraries/Data/TrackedEntity/1.5',
        'Libraries/Data/TrackedEntity/2.1'         : 'Libraries/Data/TrackedEntity/2.5',
        'Libraries/Data/VehicleControlHigh/1.1'    : 'Libraries/Data/VehicleControlHigh/1.5',
        'Libraries/Data/VehicleControlLow/1.1'     : 'Libraries/Data/VehicleControlLow/1.5',
        'Libraries/Data/VehicleState/1.1'          : 'Libraries/Data/VehicleState/1.5',
        'Libraries/Data/VehicleStateAccord/1.1'    : 'Libraries/Data/VehicleStateAccord/1.5',
        'Libraries/Data/VehicleStateAccord/1.2'    : 'Libraries/Data/VehicleStateAccord/1.5',
        'Libraries/Data/VehicleStateAccord/1.3'    : 'Libraries/Data/VehicleStateAccord/1.5',
        'Libraries/Data/VehicleStateAccord/2.1'    : 'Libraries/Data/VehicleStateAccord/2.5',
        'Libraries/Data/VehicleStateLegend/1.1'    : 'Libraries/Data/VehicleStateLegend/1.5',
        'Libraries/Data/VehicleStateLegend/1.2'    : 'Libraries/Data/VehicleStateLegend/1.5',
        'Libraries/Data/VelodyneData/1.0'          : 'Libraries/Data/VelodyneData/1.5' }


def getReplacementMap():
    """
        Returns a dict, mapping which packages need to be mapped to which
        replacement package, e.g.:

           { 'Libraries/Foo/1.0':   'Libraries/Bar/2.0',
             'Libraries/Foo/1.1':   'Libraries/Bar/2.0' }
    """
    replacementMap = {}

    # replacementMap.update( _getReplacementMap_Anaconda2()    )
    # replacementMap.update( _getReplacementMap_BBDM18()       )
    # replacementMap.update( _getReplacementMap_BPL72()        )
    # replacementMap.update( _getReplacementMap_Boost()        )
    # replacementMap.update( _getReplacementMap_Matlab94()     )
    # replacementMap.update( _getReplacementMap_Middleware33() )
    # replacementMap.update( _getReplacementMap_RTMaps456()    )
    # replacementMap.update( _getReplacementMap_ToolBOS()      )
    # replacementMap.update( _getReplacementMap_ToolBOSLib31() )
    # replacementMap.update( _getReplacementMap_XIF()          )

    return replacementMap


# EOF
