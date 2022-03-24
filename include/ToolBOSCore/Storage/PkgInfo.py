# -*- coding: utf-8 -*-
#
#  Functions to query basic project properties
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

from ToolBOSCore.Storage import SIT
from ToolBOSCore.Util    import Any
from ToolBOSCore.Util    import FastScript


def getPkgInfoContent( project = None, dirName = None, filename = None ):
    """
        Returns a dict with all variables declared in the corresponding
        pkgInfo.py file:

        * project: specify a canonical path, e.g. "Libraries/Spam/42.0"
        * dirName: specify a path (abs. or rel.) from where to read the pkgInfo
        * filename: specify the complete path of the pkgInfo.py file to read
        * without any parameters: read the pkgInfo.py from the current dir.

        Be aware of side effects if the specified file contains function
        calls.
    """
    from ToolBOSCore.Packages.ProjectProperties import requireIsCanonicalPath

    if not filename:
        if project:
            requireIsCanonicalPath( project )
            filename = os.path.join( SIT.getPath(), project, 'pkgInfo.py' )
        elif dirName:
            Any.requireIsDir( dirName )
            filename = os.path.join( dirName, 'pkgInfo.py' )
        else:
            filename = 'pkgInfo.py'

    Any.requireIsFile( filename )

    try:
        content = FastScript.execFile( filename )
    except SyntaxError as details:
        raise SyntaxError( 'unable to parse %s: %s' % ( filename, details ) )

    return content


def getSVNRevision( package ):
    """
        Returns the last globally installed SVN revision of the package
        as stored in the pkgInfo.py file.
    """
    return getPkgInfoContent( package )['revision']


def getSVNLocation( package ):
    """
        Returns the SVN repository URL of the package as stored in the
        pkgInfo.py file.
    """
    try:
        return getPkgInfoContent( package )['repositoryUrl']
    except AssertionError:
        raise AssertionError( "%s: No such package" % package )
    except KeyError:
        raise AssertionError( "%s: SVN repository location unknown" % package )


# EOF
