# -*- coding: utf-8 -*-
#
#  Python wrapper around the CMake build system
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


import collections
import glob
import logging
import os
import re
import shlex
import six
import subprocess

from ToolBOSCore.BuildSystem import Compilers
from ToolBOSCore.Util        import FastScript
from ToolBOSCore.Util        import Any, VersionCompat


#----------------------------------------------------------------------------
# Public API
#----------------------------------------------------------------------------


class CMakeServer( object ):
    """
        The CMake server-mode is a JSON protocol with which applications
        can communicate reliably with the CMake build system.

        The API documentation can be found at:
        https://cmake.org/cmake/help/v3.10/manual/cmake-server.7.html
    """

    def __init__( self, topLevelDir, buildDir, verbose=False ):
        Any.requireIsDirNonEmpty( topLevelDir )
        Any.requireIsDirNonEmpty( buildDir )
        Any.requireIsBool( verbose )

        self._pipe        = None
        self._projectRoot = topLevelDir
        self._stdin       = VersionCompat.StringIO()
        self._stdout      = VersionCompat.StringIO()
        self._topLevelDir = buildDir
        self._verbose     = verbose            # log raw queries + replies


    def connect( self ):
        logging.debug( 'connecting to CMake server' )

        self._openPipe()
        self._handshake()
        self._configure()
        self._compute()


    def disconnect( self ):
        logging.debug( 'disconnecting from CMake server' )

        self._closePipe()


    def getCodeModel( self ):
        logging.debug( 'retrieving CMake code model' )

        cmd = '{"type":"codemodel"}'
        return self._query( cmd, 'codemodel' )


    def _openPipe( self ):
        # CMake 3.10.2 on Ubuntu 18.04 needs '--experimental' flag
        args = [ 'cmake', '-E', 'server', '--debug', '--experimental' ]

        logging.debug( 'opening pipe: %s', ' '.join( args ) )


        if six.PY2:
            self._pipe = subprocess.Popen( args,
                                           bufsize=1,    # 1 == line buffered
                                           cwd=self._topLevelDir,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE )
        else:
            self._pipe = subprocess.Popen( args,
                                           bufsize=1,    # 1 == line buffered
                                           cwd=self._topLevelDir,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           encoding='utf8' )


    def _closePipe( self ):
        logging.debug( 'closing pipe' )

        self._pipe.terminate()


    def _query( self, payload, command ):
        """
            A query is wrapped into a fixed string pattern, and then sent
            via named pipe to CMake. The result is a JSON data response.

            The 'command' is the CMake command name (e.g. "compute")
            which we search for to discover the end of the message.
        """
        Any.requireIsTextNonEmpty( payload )
        Any.requireIsTextNonEmpty( command )

        leadIn   = '[== "CMake Server" ==['
        leadOut  = ']== "CMake Server" ==]'
        query    = '%s\n%s\n%s\n' % ( leadIn, payload, leadOut )

        if self._verbose:
            logging.debug( '<QUERY>%s</QUERY>', query )

        # send query
        self._pipe.stdin.write( query )
        self._pipe.stdin.flush()

        # according to the protocol we expect a reply in 3 steps:
        #    - one         lead-in    with starting + trailing newline
        #    - one or more payload(s) with            trailing newline
        #    - one         lead-out   with            trailing newline
        #
        reply = self._queryWorker( leadIn, command, leadOut )

        if self._verbose:
            logging.debug( '<REPLY>%s</REPLY>', reply )

        Any.requireIsTextNonEmpty( reply )

        reply = reply.strip()
        reply = reply.replace( leadIn, '' )
        reply = reply.replace( leadOut, '' )
        reply = reply.strip()

        return reply


    def _queryWorker( self, leadIn, command, leadOut ):
        Any.requireIsTextNonEmpty( leadIn )
        Any.requireIsTextNonEmpty( command )
        Any.requireIsTextNonEmpty( leadOut )

        lastLine = '"inReplyTo":"%s","type":"reply"}' % command
        reply = ''

        while True:

            while True:
                line = self._pipe.stdout.readline()
                if line:
                    reply += line

                if leadOut + '\n' in reply:
                    break

            if self._verbose:
                logging.debug( 'searching for last line: %s', lastLine )
                logging.debug( 'reply ends with: %s', reply[-100:] )

            if lastLine in reply:
                break

        return reply


    def _handshake( self ):
        logging.debug( 'starting protocol handshake' )

        cmd = '{"type":"handshake","protocolVersion":{"major":1},"sourceDirectory":"%s","buildDirectory":"%s","generator":"Unix Makefiles"}' % \
              ( self._projectRoot, self._topLevelDir)
        self._query( cmd, 'handshake' )

    def _configure( self ):
        logging.info( 'configuring CMake project (this may take some time...)' )

        cmd = '{"type":"configure"}'
        self._query( cmd, 'configure' )


    def _compute( self ):
        logging.debug( 'cmputing CMake-internals (this may take some time...)' )

        cmd = '{"type":"compute"}'
        self._query( cmd, 'compute' )


Switches = collections.namedtuple( 'Switches', [ 'c', 'cpp' ] )


def getIncludePathsAsString( targetPlatform, targetName ):
    """
        Returns a long string with all include paths set for the package
        using include_directories() in CMakeLists.txt (in this package or
        included ones).

        This means all paths where the compiler would search for header
        files (beside system defaults), in the form "-I/path1 -I/path2...".

        If no additional paths are set, an empty string will be returned.

        NOTE: CMake supports that include directories may be different for
              various target platforms, and even per executable and/or
              library. Therefore you need to specify both of them.
              A rule of thumb is targetName='<PROJECTNAME>-global'.
    """
    Any.requireIsTextNonEmpty( targetPlatform )
    Any.requireIsTextNonEmpty( targetName )

    fileName = os.path.join( 'build/%s/CMakeFiles/%s.dir/flags.make' %
                             ( targetPlatform, targetName ) )

    Any.requireIsDirNonEmpty( 'build/%s' % targetPlatform )
    Any.requireIsFileNonEmpty( fileName )

    # read-in ground truth information
    logging.debug( 'parsing %s', fileName )
    content    = FastScript.getFileContent( fileName, splitLines=True )
    raw_C      = ''
    raw_CPP    = ''
    regexp_C   = re.compile( '^(?:C_FLAGS|C_INCLUDES)\s=\s+(.*)$' )
    regexp_CPP = re.compile( '^(?:CXX_FLAGS|CXX_INCLUDES)\s=\s+(.*)$' )
    result     = ''

    for line in content:
        tmp = regexp_C.search( line )

        if tmp:
            raw_C = tmp.group( 1 )
            # logging.debug( 'raw C flags: %s' % raw_C )

        tmp = regexp_CPP.search( line )

        if tmp:
            raw_CPP = tmp.group( 1 )
            # logging.debug( 'raw CPP flags: %s' % raw_CPP )

    for candidate in ( shlex.split( raw_C ) + shlex.split( raw_CPP ) ):
        if candidate.startswith( '-I' ):
            result += candidate + ' '

    return result


def getIncludePathsAsList( targetPlatform, targetName ):
    """
        Returns a list with all include paths set for the package
        using include_directories() in CMakeLists.txt (in this package or
        included ones).

        This means all paths where the compiler would search for header
        files (beside system defaults).

        If no additional paths are set, an empty list will be returned.

        NOTE: CMake supports that include directories may be different for
              various target platforms, and even per executable and/or
              library. Therefore you need to specify both of them.
              A rule of thumb is targetName='<PROJECTNAME>-global'.
    """
    Any.requireIsTextNonEmpty( targetPlatform )
    Any.requireIsTextNonEmpty( targetName )

    result  = []

    # we are adding a trailing blank so that the " -I" replacement will
    # also work on the first element
    raw = getIncludePathsAsString( targetPlatform, targetName )
    tmp = (' ' + raw ).replace( ' -I', ' ' )

    for token in tmp.split():
        result.append( token.strip() )


    # remove empty entries (if present)
    try:
        result.remove( '' )
    except ValueError:
        pass

    return frozenset( result )


def getStdSwitches( targetPlatform, targetName ):
    """
        Returns a string with the compiler std switch.

        NOTE: CMake supports that compiler definitions may be different for
              various target platforms, and even per executable and/or
              library. Therefore you need to specify both of them.
              A rule of thumb is targetName='<PROJECTNAME>-global'.
    """
    Any.requireIsTextNonEmpty( targetPlatform )
    Any.requireIsTextNonEmpty( targetName )

    # We need defaults because the macro parser needs the switch to
    # correctly parse c++ code.


    fileName = os.path.join( 'build/%s/CMakeFiles/%s.dir/flags.make' %
                             ( targetPlatform, targetName ) )

    Any.requireIsDirNonEmpty( 'build/%s' % targetPlatform )
    Any.requireIsFileNonEmpty( fileName )

    # read-in ground truth information
    logging.debug( 'parsing %s', fileName )
    content           = FastScript.getFileContent( fileName, splitLines=True )
    raw_C_CFLAGS      = ''
    raw_CPP_CFLAGS    = ''
    regexp_C_CFLAGS   = re.compile( r'^C_FLAGS\s=\s+(.*)$' )
    regexp_CPP_CFLAGS = re.compile( r'^CXX_FLAGS\s=\s+(.*)$' )

    for line in content:
        tmp = regexp_C_CFLAGS.search( line )

        if tmp:
            raw_C_CFLAGS = tmp.group( 1 )

        tmp = regexp_CPP_CFLAGS.search( line )

        if tmp:
            raw_CPP_CFLAGS = tmp.group( 1 )

    # get the default language standards
    standards = Compilers.getDefaultLanguageStandard(targetPlatform)
    cStdSwitch   = '-std={}'.format( standards[ 'c' ] )
    cppStdSwitch = '-std={}'.format( standards[ 'c++' ] )

    # look if the user specified different standards in the C_FLAGS/CPP_FLAGS
    # CMake variables
    candidates = shlex.split( raw_C_CFLAGS )
    for candidate in candidates:
        if candidate.startswith( '-std=' ):
            cStdSwitch = candidate

    candidates = shlex.split( raw_CPP_CFLAGS )
    for candidate in candidates:
        if candidate.startswith( '-std=' ):
            cppStdSwitch = candidate

    return Switches( c=cStdSwitch, cpp=cppStdSwitch )


def getCDefinesAsString( targetPlatform, targetName ):
    """
        Returns a long string with all compiler definitions set for the
        package using the addDefinitions() directive.

        This means all definitions passed to the compiler in the given path
        (beside system defaults), in the form "-DDEFINE1 -DFOO=BAR...".

        If no additional definitions are set, an empty string will be returned.

        NOTE: CMake supports that compiler definitions may be different for
              various target platforms, and even per executable and/or
              library. Therefore you need to specify both of them.
              A rule of thumb is targetName='<PROJECTNAME>-global'.
    """
    Any.requireIsTextNonEmpty( targetPlatform )
    Any.requireIsTextNonEmpty( targetName )

    fileName = os.path.join( 'build/%s/CMakeFiles/%s.dir/flags.make' %
                             ( targetPlatform, targetName ) )

    Any.requireIsDirNonEmpty( 'build/%s' % targetPlatform )
    Any.requireIsFileNonEmpty( fileName )

    # read-in ground truth information
    logging.debug( 'parsing %s', fileName )
    content           = FastScript.getFileContent( fileName, splitLines=True )
    raw_C             = ''
    raw_CPP           = ''
    raw_C_CFLAGS      = ''
    raw_CPP_CFLAGS    = ''
    regexp_C          = re.compile( '^C_DEFINES\s=\s+(.*)$' )
    regexp_CPP        = re.compile( '^CXX_DEFINES\s=\s+(.*)$' )
    regexp_C_CFLAGS   = re.compile( '^C_FLAGS\s=\s+(.*)$' )
    regexp_CPP_CFLAGS = re.compile( '^CXX_FLAGS\s=\s+(.*)$' )
    result            = ''

    for line in content:
        tmp  = regexp_C.search( line )

        if tmp:
            raw_C = tmp.group( 1 )
            # logging.debug( 'raw C defines: %s' % raw_C )

        tmp = regexp_CPP.search( line )

        if tmp:
            raw_CPP = tmp.group( 1 )
            # logging.debug( 'raw CPP defines: %s' % raw_CPP )

        tmp = regexp_C_CFLAGS.search(line)

        if tmp:
            raw_C_CFLAGS = tmp.group(1)

        tmp = regexp_CPP_CFLAGS.search(line)

        if tmp:
            raw_CPP_CFLAGS = tmp.group(1)

    candidates = ( shlex.split( raw_C ) +
                   shlex.split( raw_CPP ) +
                   shlex.split( raw_C_CFLAGS ) +
                   shlex.split( raw_CPP_CFLAGS ) )

    for candidate in candidates:
        if candidate.startswith( '-D' ):
            result += candidate + ' '

    return result


def getCDefinesAsList( targetPlatform, targetName ):
    """
        Returns a list with all compiler definitions set for the
        package using the addDefinitions() directive.

        If no additional definitions are set, an empty list will be returned.

        NOTE: CMake supports that compiler definitions may be different for
              various target platforms, and even per executable and/or
              library. Therefore you need to specify both of them.
              A rule of thumb is targetName='<PROJECTNAME>-global'.
    """
    Any.requireIsTextNonEmpty( targetPlatform )
    Any.requireIsTextNonEmpty( targetName )

    result  = []
    regexp  = re.compile( '-D\s*(.*)' )

    for token in getCDefinesAsString( targetPlatform, targetName ).split():

        if token.startswith( '-D' ):
            tmp  = regexp.search( token )
            item = (tmp.group(1)).strip()
            result.append( item )

    return frozenset(result)


def getHeaderAndLanguageMap( targetPlatform ):
    """
        Returns a dictionary mapping header files to the set of language
        files that use it.
    """
    platformBuildDir        = os.path.join( 'build', targetPlatform )
    targetBuildDirsWildcard = os.path.join( platformBuildDir, 'CMakeFiles', '*.dir' )
    targetBuildDirs         = glob.glob( targetBuildDirsWildcard )
    result                  = {}


    for buildDir in targetBuildDirs:

        try:
            result.update( _parseDependDotMake( buildDir, platformBuildDir ) )

        except IOError:
            # most likely the depend.make does not exist for this target,
            # this might happen if there are no dependencies by the target
            # or if this is a pseudo-target such as "doc" coming from
            # FindDoxygen.cmake
            logging.debug( 'ignoring target: %s', buildDir )

    return result


def _parseDependDotMake( targetBuildDir, platformBuildDir ):
    """
        Returns a dictionary mapping header files to the set of language
        files that use it.

        The dictionary is obtained parsing the file
        build/<targetPlatform>/CMakeFiles/<targetName>.dir/depend.make
    """
    Any.requireIsTextNonEmpty( targetBuildDir )
    Any.requireIsTextNonEmpty( platformBuildDir )

    dependDotMakePath = os.path.join( targetBuildDir, 'depend.make' )

    lines  = FastScript.getFileContent( dependDotMakePath, splitLines=True )
    result = collections.defaultdict( set )

    languageNormalizationMap = {
        '.c'  : 'c',
        '.C'  : 'c++',
        '.CC' : 'c++',
        '.CPP': 'c++',
        '.CXX': 'c++',
        '.cc' : 'c++',
        '.cpp': 'c++',
        '.cxx': 'c++',
    }

    for l in lines:
        # skip comments and empty lines
        if Any.isTextNonEmpty( l ) and not l.startswith( '#' ):
            # lines are in the format
            # /path/to/obj/file.{c,cpp,cc,cxx}.o: /path/to/dependencyfile.{c,cpp,cc,cxx,h,hpp,hxx,hh}
            objFile, depFile = l.split( ':' )
            srcFile, objExt  = os.path.splitext( objFile.strip( ) )
            srcName, srcExt  = os.path.splitext( srcFile )
            depFile          = depFile.strip( )
            _, depFileExt    = os.path.splitext( depFile )
            language         = languageNormalizationMap[ srcExt ]

            if depFileExt.lower( ) in ('.h', '.hxx', '.hpp', '.hh'):
                if not os.path.isabs( depFile ):
                    relPath = os.path.join( platformBuildDir, depFile )
                    absPath = os.path.abspath( relPath )
                else:
                    absPath = depFile
                result[ absPath ].add( language )


    return result


# EOF
