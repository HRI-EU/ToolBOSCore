# -*- coding: utf-8 -*-
#
#  pkgInfo.py modifier functions
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


import ast
import io
import logging
import re
import os

from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.Storage.PkgInfo          import getPkgInfoContent
from ToolBOSCore.Storage.PkgInfoWriter    import PkgInfoWriter
from ToolBOSCore.Util                     import Any
from ToolBOSCore.Util                     import FastScript


class PkgInfoInterface( object ):

    def __init__( self, details=None ):
        """
            Allows modifying an existing pkgInfo.py file, f.i. add/remove
            entries.

            Multiple changes can be applied in a row. The actual re-writing
            of the file is done using write().

            We attempt to modify the package in the current working directory
            unless another PackageDetector class is provided.
        """
        if details is not None:
            Any.requireIsInstance( details, PackageDetector )
            self._details = details
        else:
            self._details = PackageDetector()

        self._filePath = os.path.join( self._details.topLevelDir, 'pkgInfo.py' )
        self._worker   = PkgInfoWriter( self._details, sourceTree=True )

        try:
            self._content  = FastScript.getFileContent( self._filePath )
            self.checkSyntax()
            self._data     = getPkgInfoContent( dirName=self._details.topLevelDir )

        except IOError:
            self._content  = self._worker.addLeadIn()

        except SyntaxError:
            raise


    def checkSyntax( self, content=None ):
        """
            Simple check for valid Python syntax.

            If provided 'content' will be checked, the internal
            self._content otherwise.

            If OK just passes, otherwises raises SyntaxError.
        """
        if content is None:
            toCheck = self._content
        else:
            toCheck = content

        Any.requireIsTextNonEmpty( toCheck )

        try:
            ast.parse( toCheck )
        except SyntaxError as details:
            logging.debug( details )
            logging.debug( '<content>' )
            logging.debug( toCheck )
            logging.debug( '</content>' )
            raise


    def get( self, key ):
        """
            Returns the value of the specified key.

            Raises a KeyError if key is not found.
        """
        try:
            return self._data[ key ]
        except KeyError:
            raise KeyError( '%s: No such key in %s', key, self._filePath )


    def set( self, key, value ):
        """
            Add key/value pair at the end of pkgInfo.py.

            If 'key' already exists it will be overwritten with the new value.
        """
        Any.requireIsTextNonEmpty( key )
        # value might be anything, can't check for it

        newContent = io.StringIO()
        table      = { key: value }
        regexp     = re.compile( r'^%s\s+=' % key )
        found      = False                  # overall found in pkgInfo.py
        foundNow   = False                  # helpervar. used in loop


        # first remove '# EOF' and any trailing whitespaces
        self._removeLeadOut()


        # data to be inserted (or updated)
        newData    = self._worker.writeTable( table, allowNoneValue=True )


        # loop over the lines and copy all existing data, however if the key
        # is found then update it rather than writing the original data
        for line in self._content.splitlines():

            # if we had just found the line then ignore further lines
            # (multi-line assignment)
            if foundNow is True and len(line) > 0 and line[0] == ' ':
                continue
            else:
                foundNow = False

            if regexp.match( line ):
                found    = True
                foundNow = True
                newContent.write( newData.strip() )     # remove double '\n'

            else:
                newContent.write( line )

            newContent.write( '\n' )


        # add new data at the end if not updating existing data
        if not found:
            newContent.write( '\n' )
            newContent.write( newData )


        self.checkSyntax( newContent.getvalue() )

        if found:
            logging.debug( "updated key '%s'", key )
        else:
            logging.debug( "added key '%s'", key )


        # done
        self._content = newContent.getvalue()
        self._addLeadOut()


    def remove( self, key ):
        """
            Remove key/value pair from pkgInfo.py.

            ATTENTION: This function operates line-wise, removing the line
                       starting with 'key' and all following lines which do
                       not start at the beginning of the line.
        """
        Any.requireIsTextNonEmpty( key )

        # first remove '# EOF' and any trailing whitespaces
        self._removeLeadOut()


        newContent = io.StringIO()
        regexp     = re.compile( r'^%s\s+=' % key )
        lines      = self._content.splitlines()
        skip       = 0
        found      = False

        for i, line in enumerate( lines ):
            if skip > 0:
                skip -= 1

            else:
                if regexp.match( line ):
                    # remove the matching line by not copying it to newContent
                    logging.debug( "removed key '%s'", key )
                    found = True

                    # if the record is multi-line (content continues in next
                    # line but indented), or followed by a blank line than
                    # remove them, too --> find next regular assignment
                    for candidate in lines[ i+1: ]:
                        if candidate == '' or candidate.startswith( ' ' ):
                            skip += 1
                        else:
                            break

                else:
                    # copy content
                    newContent.write( line )
                    newContent.write( '\n' )

                    skip = 0


        self.checkSyntax( newContent.getvalue() )

        if not found:
            logging.debug( 'key %s not found', key )


        # done
        self._content = newContent.getvalue()
        self._addLeadOut()


    def write( self ):
        FastScript.setFileContent( self._filePath, self._content )
        logging.debug( '%s written', self._filePath )


    def _addLeadOut( self ):
        self._content = self._content.strip()
        self._content += '\n\n\n# EOF\n'


    def _removeLeadOut( self ):
        self._content = self._content.replace( '# EOF', '' )
        self._content = self._content.strip()


# EOF
