# -*- coding: utf-8 -*-
#
#  query settings from userInstall.php file
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

from ToolBOSCore.Util import Any
from ToolBOSCore.Util import FastScript


#----------------------------------------------------------------------------
# Public class
#----------------------------------------------------------------------------


class UserInstallPHP( object ):

    rawContent = None               # raw file content, with comments

    content    = ''                 # removed comments from rawContent
    flat       = None               # replaced newlines by blanks
    lines      = None               # line-wise array


    def __init__( self, filePath ):
        Any.requireIsFileNonEmpty( filePath )

        self.rawContent = FastScript.getFileContent( filePath )

        for line in self.rawContent.splitlines():
            if not line.startswith( '#' ) and not line.startswith( '//' ):
                self.content += line + "\n"

        self.flat       = self.content.replace( '\n', ' ' )
        self.lines      = self.content.splitlines()


    def linkAllLibraries( self ):
        """
            Returns True if the "LinkAllLibraries"-flag is set.
        """
        return self.content.find( 'LinkAllLibraries' ) > 0


    def usePatchlevelHandler( self ):
        """
            Returns True if the patchlevel installation system (3-digit
            version numbering scheme) is used.
        """
        pattern = re.compile( "^\s*PatchlevelHandler_onExitStage4" )

        for line in self.lines:
            if pattern.match( line ):
                return True

        return False


    def install( self ):
        """
            Returns a list of Files/directories to be copied directly.
            A list element might be a tuple ( src, dst ) if the
            dst-subdirectory within the install path is different from
            the src-subdirectory.

            Example:

            [ 'doc',
              'etc',
              'sbin',
              ( 'foo', 'bar' ),          # copy <src>/foo to <dst>/bar
              'examples' ]
        """
        resultList  = []

        # find all occurences of Install::copy( x, y )
        rawDataList = re.findall( "Install::copy\(.*?\)", self.flat )

        # detailed extraction of "src" and "dst"
        for rawData in rawDataList:
            rawData = rawData.replace( 'Install::copy', '' )

            tokens  = rawData.split( ',' )
            Any.requireIsListNonEmpty( tokens )

            src     = self._getQuotedContent( tokens[0] )
            dst     = self._getQuotedContent( tokens[1] )
            Any.requireIsTextNonEmpty( src )
            Any.requireIsTextNonEmpty( dst )

            # replace legacy variable names
            src     = self._removeVariables( src )
            dst     = self._removeVariables( dst )

            if src == dst:
                resultList.append( src )           # "symmetric installation"
            else:
                resultList.append( ( src, dst ) )  # "asymmetric installation"

        return resultList


    def installMatching( self ):
        """
            Returns a list of following format:

            A list element might be a tuple of two elements
            ( srcDir, regexp ). In this case all files from <srcDir>
            matching <regexp> will be installed to <dstDir>.

            If the dst-subdirectory within the install path is different from
            the src-subdirectory, a three-element tuples can be provided
            (with an alternative dstDir as 3rd element).

            Example:

            [ ( 'doc', '\.pdf' ),
              ( 'etc', '\.conf' ),
              ( 'sbin', '\.(sh|py)' )
              ( 'foo', '\.txt', bar' ),    # copy <src>/foo/*.txt to <dst>/bar
              ( 'examples', '.*' ) ]
        """
        resultList = []

        # find all occurences of Install::copy( x, y )
        rawDataList = re.findall( "Install::copyMatching\(.*?\);", self.flat )

        # detailed extraction of "src" and "dst"
        for rawData in rawDataList:
            rawData = rawData.replace( 'Install::copyMatching', '' )

            tokens  = rawData.split( ',' )
            Any.requireIsListNonEmpty( tokens )

            srcDir  = self._getQuotedContent( tokens[0] )
            regexp  = self._getQuotedContent( tokens[1] )
            dstDir  = self._getQuotedContent( tokens[2] )

            # replace legacy variable names (do not touch regexp+description)
            srcDir  = self._removeVariables( srcDir )
            dstDir  = self._removeVariables( dstDir )

            Any.requireIsText( srcDir )
            Any.requireIsTextNonEmpty( regexp )
            Any.requireIsText( dstDir )

            if srcDir == dstDir:
                # "symmetric installation"
                resultList.append( ( srcDir, regexp ) )
            else:
                # "asymmetric installation"
                resultList.append( ( srcDir, regexp, dstDir ) )

        return resultList


    def umask( self ):
        """
            Returns the value of umask-setting (as integer) if specified
            in the userInstall.php, None otherwise.

            Some userInstall.php contained code like "umask( 0002 );".
            This function would return 2.
        """
        match = re.search( 'umask\s?\(\s?(\d+)\s?\);', self.flat )

        if match and match.group(1):
            result = int( match.group(1) )
            logging.debug( 'found umask: %d', result )
            return result
        else:
            return None


    def _getQuotedContent( self, s ):
        """
            Tries to find a the content enclosed by '...' or "...",
            ignoring any other leading or trailing characters.
        """
        Any.requireIsTextNonEmpty( s )

        logging.debug( 'input:  #%s#', s )

        result = ''

        # first look for single-quotes
        quotePos1 = s.find( "'" )
        quotePos2 = s.rfind( "'" )

        if quotePos1 > -1 and quotePos2 > -1:
            # return substring between quotes
            result = s[ quotePos1+1 : quotePos2 ]


        if not result:
            # single quotes not found, give a try to find double-quotes
            quotePos1 = s.find( '"' )
            quotePos2 = s.rfind( '"' )

            if quotePos1 > -1 and quotePos2 > -1:
                # return substring between quotes
                result = s[ quotePos1+1 : quotePos2 ]


        if not result:
            # not using any quotes, likely sth. like  f( $src, $dst );
            # return trimmed string, remove special characters
            result = s
            result = result.replace( '(', '' )
            result = result.replace( ')', '' )
            result = result.strip()


        logging.debug( 'found:  #%s#', result )

        return result


    def _removeVariables( self, s ):
        """
            Removes PHP variables such as $topLevelDir, $installRoot etc.
            from the string.
        """
        Any.requireIsText( s )

        s = s.replace( '$projectRoot/',   '' )
        s = s.replace( '${projectRoot}/', '' )
        s = s.replace( '$projectRoot',    '' )
        s = s.replace( '$installRoot/',   '' )
        s = s.replace( '${installRoot}/', '' )
        s = s.replace( '$installRoot',    '' )
        s = s.replace( '/$makefilePlatform',   '${MAKEFILE_PLATFORM}' )
        s = s.replace( '/${makefilePlatform}', '${MAKEFILE_PLATFORM}' )
        s = s.replace( '$makefilePlatform',    '${MAKEFILE_PLATFORM}' )

        return s


# EOF
