# -*- coding: utf-8 -*-
#
#  Package documentation API
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

from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.Platforms.Platforms      import getHostPlatform
from ToolBOSCore.Settings                 import ProcessEnv
from ToolBOSCore.Settings.ToolBOSConf     import getConfigOption
from ToolBOSCore.Storage                  import SIT
from ToolBOSCore.Util                     import Any, FastScript


class DocumentationCreator( object ):
    """
        API to create HTML documentation for a package.

        You may redirect input/output streams by providing StringIO
        instances.

        'details' should be a PackageDetector instance to use.
    """

    def __init__( self, projectRoot, sitPath=None, stdout=None,
                  stderr=None, details=None ):

        Any.requireIsDir( projectRoot )

        self.projectRoot = projectRoot
        logging.debug( 'topLevelDir=%s', projectRoot )

        if details is None:
            details = PackageDetector( projectRoot )

            try:
                details.retrieveMakefileInfo()
            except EnvironmentError as e:
                logging.warning( e )                    # e.g. $SIT not defined in environment

        else:
            Any.requireIsInstance( details, PackageDetector)

        if sitPath is None:
            sitPath = SIT.getPath()


        if FastScript.getEnv( 'MAKEFILE_DOC' ) == 'FALSE':
            handler = NullBackend
        elif details.docTool == 'doxygen':
            handler = DoxygenBackend
        elif details.docTool == 'matdoc':
            handler = MatlabBackend
        elif details.docTool == '':
            handler = NullBackend
        elif details.isMatlabPackage():

            # Matlab is no longer needed, and there are also issues starting
            # with Ubuntu 16.04 (see CIA-1131)

            handler = NullBackend

        else:
            handler = DoxygenBackend

        self.backend = handler( details, sitPath, stdout, stderr )


    def generate( self ):
        """
            Creates HTML documentation for the specified package.

            If the environment variable MAKEFILE_DOC is set to FALSE,
            the entire documentation creation is skipped, e.g. for quick
            debugging sessions where you don't need to build the docs all
            the time.

            It internally follows the Strategy Design Pattern to select the
            appropriate documentation tool depending on the package type.
        """
        self.backend.setup()
        self.backend.execute()
        self.backend.cleanup()


class AbstractBackend( object ):

    def __init__( self, details, sitPath, stdout=None, stderr=None ):
        Any.requireIsInstance( details, PackageDetector)

        self.details = details
        self.sitPath = sitPath
        self.docDir  = os.path.join( self.details.topLevelDir, 'doc' )
        self.stdout  = stdout
        self.stderr  = stderr

        Any.requireIsDir( self.details.topLevelDir )


    def setup( self ):
        pass


    def execute( self ):
        raise NotImplementedError()


    def cleanup( self ):
        pass


class NullBackend( AbstractBackend ):
    """
        Dummy handler according to the "NULL" Design Pattern that won't
        create any documentation but has the same interface as regular
        handlers.

        This is used to entirely skip creating the documentation.
        See DocumentationCreator.generate() for details.
    """
    def execute( self ):
        logging.info( 'skipping doc creation' )


class DoxygenBackend( AbstractBackend ):
    """
        Creates package documentations using 'doxygen'.
    """

    def __init__( self, details, sitPath, stdout=None, stderr=None ):
        super( DoxygenBackend, self ).__init__( details, sitPath, stdout, stderr )

        if not os.path.isdir( self.docDir ):
            FastScript.mkdir( self.docDir )

        if not self.details.packageCategory:
            raise ValueError( 'unable to detect package category from CMakeLists.txt' )


        self.mainDoxyfile = os.path.join( self.docDir, 'Doxyfile' )
        self.autoDoxyfile = os.path.join( self.docDir, 'autoDoxyfile' )
        self.userDoxyfile = os.path.join( self.docDir, 'userDoxyfile' )


    def setup( self ):
        FastScript.setEnv( 'PROJECT_NAME', self.details.packageName )
        FastScript.setEnv( 'PROJECT_VERSION', self.details.packageVersion )

        self._createMainDoxyfile()
        self._createUserDoxyfile()
        self._createAutoDoxyfile()


    def execute( self ):
        logging.info( 'running doxygen...' )
        doxygenBinary = self._findDoxygen()

        try:
            FastScript.execProgram( doxygenBinary,
                                    stdout=self.stdout,
                                    stderr=self.stderr,
                                    workingDir=self.docDir )
        except OSError:
            logging.error( 'unable to execute doxygen (maybe not in $PATH)?' )


    def cleanup( self ):
        FastScript.remove( self.mainDoxyfile )
        FastScript.remove( self.autoDoxyfile )

        if os.path.getsize( self.userDoxyfile ) == 0:   # created by us
            FastScript.remove( self.userDoxyfile )


    def _createMainDoxyfile( self ):
        fileName = 'Doxyfile'
        content  = ''
        template = os.path.join( FastScript.getEnv( 'TOOLBOSCORE_ROOT' ),
                                 'etc', fileName )
        Any.requireIsFileNonEmpty( template )

        if os.path.isdir( os.path.join( self.details.topLevelDir, 'examples' ) ):
            logging.debug( 'doxygen: indexing examples' )
            content += 'EXAMPLE_PATH           = ../examples\n' + \
                       'EXAMPLE_PATTERNS       =\n' + \
                       'EXAMPLE_RECURSIVE      = YES\n'

        if self.details.isComponent():
            logging.debug( 'doxygen: indexing src/*.{c,cpp}' )
            content += 'FILE_PATTERNS          = *.c *.cpp *.h\n'

        content = FastScript.getFileContent( template ) + content
        FastScript.setFileContent( self.mainDoxyfile, content )


    def _createUserDoxyfile( self ):
        if not os.path.exists( self.userDoxyfile ):
            FastScript.setFileContent( self.userDoxyfile, '' )  # "NULL" design pattern


    def _createAutoDoxyfile( self ):
        content = 'TAGFILES = '

        logging.debug( 'cross-linking doxygen documentation into %s', self.sitPath )

        if self.details.inheritedProjects:
            logging.debug( 'dependencies: %s', self.details.inheritedProjects )
        else:
            logging.debug( 'no dependencies found --> no cross-links' )


        for dep in self.details.inheritedProjects:
            depRoot    = os.path.join( self.sitPath, dep )
            depTagFile = os.path.join( depRoot, 'doc', 'doxygen.tag' )
            depHTMLDir = os.path.join( depRoot, 'doc', 'html' )

            # ignore if we can't cross-link

            depTagFileExists = os.path.exists( depTagFile )
            depHTMLDirExists = os.path.exists( depHTMLDir )

            logging.debug( 'processing dependency: %s', dep )
            logging.debug( '  %s: %s', depTagFile, depTagFileExists )
            logging.debug( '  %s: %s', depHTMLDir, depHTMLDirExists )

            if depTagFileExists and depHTMLDirExists:
                content += '%s=%s ' % ( depTagFile, depHTMLDir )
                logging.debug( '  linking %s', depTagFile )
            else:
                logging.debug( '  not linking' )

            logging.debug( '' )

        FastScript.setFileContent( self.autoDoxyfile, content )


    def _findDoxygen( self ):
        sitPath      = SIT.getRootPath()
        package      = getConfigOption( 'package_doxygen' )
        hostPlatform = getHostPlatform()
        fileName     = 'doxygen'
        exePath      = os.path.join( sitPath, package, 'bin', hostPlatform, fileName )

        if os.path.exists( exePath ):
            return exePath

        else:
            logging.debug( '%s: No such file', exePath )
            logging.debug( 'falling back to "doxygen" in $PATH' )

            found = ProcessEnv.which( 'doxygen' )

            if found:
                logging.debug( 'using doxygen from $PATH: %s', found )
                return found
            else:
                raise EnvironmentError( '"doxygen" neither found in SIT nor installed locally' )


class MatlabBackend( AbstractBackend ):
    """
        Creates package documentations using 'matdoc'.
    """

    def setup( self ):
        fileName = os.path.join( self.details.topLevelDir, 'matdoc.pm' )

        if os.path.isfile( fileName ):
            return             # nothing to do, maintainer made custom one

        username = FastScript.getCurrentUserFullName()

        content  = '# matdoc configuration file auto-generated by ToolBOSCore\n\n' + \
                   '# directories to exclude\n' + \
                   '@Exclude = qw(doc lib obj install test);\n\n' + \
                   '# project maintainer(s)\n' + \
                   ( "@Maintainers = ( '%s' );\n\n" % username ) + \
                   '# create doc index for each subdirectory?\n' + \
                   '$Separate = 0;\n\n'

        FastScript.setFileContent( fileName, content )


    def execute( self ):
        logging.info( 'running matdoc...' )

        prog = self._findMatdoc()
        cmd  = '%s %s' % ( prog, self.details.packageName )
        msg  = 'matdoc not found'

        if not os.path.exists( prog ):
            logging.error( '%s: No such file' )
            logging.error( msg )
            return

        try:
            FastScript.execProgram( cmd,
                                    stdout=self.stdout,
                                    stderr=self.stderr )
        except OSError as details:
            logging.debug( details )
            logging.error( msg )
            return

        oldName = os.path.join( self.details.topLevelDir, 'doc', 'auto/html' )
        newName = os.path.join( self.details.topLevelDir, 'doc', 'html' )
        FastScript.remove( newName )

        try:
            os.rename( oldName, newName )
        except OSError as details:
            logging.debug( details )
            logging.error( msg )
            return

        FastScript.remove( os.path.join( self.details.topLevelDir, 'doc', 'auto' ) )


    def cleanup( self ):
        docDir = os.path.join( self.details.topLevelDir, 'doc', 'matdoc' )

        FastScript.remove( os.path.join( docDir, 'doc' ) )
        FastScript.remove( os.path.join( docDir, 'syntax' ) )
        FastScript.remove( os.path.join( docDir, self.details.packageName ) )


    def _findMatdoc( self ):
        sitPath      = SIT.getRootPath()
        package      = getConfigOption( 'package_matdoc' )
        fileName     = 'matdoc'
        exePath      = os.path.join( sitPath, package, 'bin', fileName )

        if os.path.exists( exePath ):
            return exePath
        else:
            logging.warning( '%s: No such file', exePath )
            return fileName                         # default to 'matdoc'


# EOF
