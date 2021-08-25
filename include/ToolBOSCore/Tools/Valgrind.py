#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  run Valgrind on project
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


import os
import tempfile

from collections import namedtuple

from ToolBOSCore.Util import Any, FastScript

FastScript.tryImport( 'lxml' )
from lxml import etree


_valgrindCmd = 'valgrind --xml=yes --xml-file=%s %s'

_kindMap = {
    'InvalidFree'         : 'Free/delete/delete[] on an invalid pointer',
    'MismatchedFree'      : 'Free/delete/delete[] does not match allocation function (eg doing new[] then free on the result)',
    'InvalidRead'         : 'Read of an invalid address:',
    'InvalidWrite'        : 'Write of an invalid address',
    'InvalidJump'         : 'Jump to an invalid address',
    'Overlap'             : 'Args overlap other otherwise bogus in eg memcpy',
    'InvalidMemPool'      : 'Invalid mem pool specified in client request',
    'UninitCondition'     : 'Conditional jump/move depends on undefined value',
    'UninitValue'         : 'Other use of undefined value (primarily memory addresses)',
    'SyscallParam'        : 'System call params are undefined or point to undefined/unaddressible memory',
    'ClientCheck'         : '"error" resulting from a client check request',
    'Leak_DefinitelyLost' : 'Memory leak: the referenced blocks are definitely lost',
    'Leak_IndirectlyLost' : 'Memory leak: the referenced blocks are lost because all pointers to them are also in leaked blocks',
    'Leak_PossiblyLost'   : 'Memory leak: only interior pointers to referenced blocks were found',
    'Leak_StillReachable' : 'Memory leak: pointers to un-freed blocks are still available'
}

Error = namedtuple( 'Error', [ 'kind', 'description', 'fname', 'lineno' ] )


def checkExecutable( executablePath, details, stdout=None, stderr=None ):
    tmpFile = tempfile.mktemp()
    cmd     = _valgrindCmd % (tmpFile, executablePath)

    FastScript.execProgram( cmd, stdout=stdout, stderr=stderr )
    failed, numErrors = parseOutput( tmpFile, details )
    FastScript.remove( tmpFile )

    return failed, numErrors


def parseOutput( statusFile, details ):
    Any.requireIsFileNonEmpty( statusFile )

    out = etree.parse( statusFile )
    errors = [ errorParser( error, details ) for error in out.findall( 'error' ) ]

    return bool( errors ), errors


def errorParser( errorRoot, details ):
    kindNode        = errorRoot.find( 'kind' )
    descriptionNode = errorRoot.find( 'xwhat' )
    stackNode       = errorRoot.find( 'stack' )

    Any.requireMsg( kindNode is not None, 'Malformed Valgrind output' )
    Any.requireMsg( descriptionNode is not None, 'Malformed Valgrind output' )

    kind        = _kindMap[ kindNode.text ]
    description = descriptionNode.find( 'text' ).text
    fname       = ''
    lineno      = ''

    # Try to isolate among the stack frames
    # the last one in our code, to help the
    # user find the root of the problem.
    if stackNode is not None:
        for frame in stackNode.findall( 'frame' ):
            objNode = frame.find('obj')
            if objNode is not None:
                obj               = objNode.text
                stackFrameObjPath = os.path.realpath( obj )

                if stackFrameObjPath.startswith( details.topLevelDir ):
                    fileNode = frame.find( 'file' )
                    lineNode = frame.find( 'line' )

                    if fileNode is not None:
                        fname  = fileNode.text

                    if lineNode is not None:
                        lineno = lineNode.text

    return Error( kind, description, fname, lineno )


# EOF
