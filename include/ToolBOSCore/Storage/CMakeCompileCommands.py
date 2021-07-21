# -*- coding: utf-8 -*-
#
#  Interface to CMake's "compile_commands.json" files
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


import json
import shlex

from ToolBOSCore.Util import Any, FastScript


class CMakeCompileCommands:

    def __init__( self, filePath:str ) -> None:
        """
            Creates an instance for accessing the specified CMake
            compile commands file, e.g. in case of BST.py found under
            'build/<platformName>/compile_commands.json'.
        """
        Any.requireIsFileNonEmpty( filePath )
        self._filePath = filePath

        self._data = None

        self._loadFile()


    def getCompilerCommand( self, sourceFile: str ) -> str:
        """
            Returns a long string with the compiler command invoked by CMake
            to build this sourcefile.

            The sourceFile must be provided as absolute path.
            If no information to this file are found, a ValueError is raised.
        """
        Any.requireIsFileNonEmpty( sourceFile )

        for item in self._data:
            # Each item in self._data is a JSON-encoded dictionary with 3 entries:
            #
            # item[0] == 'directory' == path to build directory
            # item[1] == 'command'   == compiler command line
            # item[2] == 'file'      == absolute path to sourcefile

            itemAsDict = dict( item )

            if itemAsDict['file'] == sourceFile:
                return itemAsDict['command']

        raise ValueError( '%s: No compile information found' % sourceFile )


    def getDefinesAsString( self, sourceFile: str ) -> str:
        """
            Returns a long string with all compiler defines set for the given file
            using add_definitions() in CMakeLists.txt (in this package or
            included ones).

            This does not include definitions from the code using #define.

            The sourceFile must be provided as absolute path.
            If no information to this file are found, a ValueError is raised.
        """
        Any.requireIsFileNonEmpty( sourceFile )

        command = self.getCompilerCommand( sourceFile )
        result  = ''

        for candidate in shlex.split( command ):
            if candidate.startswith( '-D' ):
                result += candidate + ' '

        return result


    def getIncludePathsAsString( self, sourceFile: str ) -> str:
        """
            Returns a long string with all include paths set for the given file
            using include_directories() in CMakeLists.txt (in this package or
            included ones).

            This means all paths where the compiler would search for header
            files (beside system defaults), in the form "-I/path1 -I/path2...".

            The sourceFile must be provided as absolute path.
            If no information to this file are found, a ValueError is raised.

            If no additional paths are set, an empty string will be returned.
        """
        Any.requireIsFileNonEmpty( sourceFile )

        command = self.getCompilerCommand( sourceFile )
        result  = ''

        for candidate in shlex.split( command ):
            if candidate.startswith( '-I' ):
                result += candidate + ' '

        return result


    def _loadFile( self ):
        """
            Reads the JSON file and stores the data into a member variable.
        """
        content    = FastScript.getFileContent( self._filePath )
        Any.requireIsTextNonEmpty( content )

        self._data = json.loads( content )
        Any.requireIsListNonEmpty( self._data )


# EOF
