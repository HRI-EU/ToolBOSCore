# -*- coding: utf-8 -*-
#
#  Interface to Debian/Ubuntu/... package management
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


import io
import re

from ToolBOSCore.Util import Any, FastScript
from ToolBOSCore.Settings import ProcessEnv


#----------------------------------------------------------------------------
# Constants, settings,...
#----------------------------------------------------------------------------


_debPkgCache = None


#----------------------------------------------------------------------------
# Public functions
#----------------------------------------------------------------------------


def getSystemPackages():
    """
        Fetches the list of Debian packages installed on the system,
        returning a dict mapping "packageName" => "version".
    """
    if not ProcessEnv.which( 'dpkg' ):
        raise EnvironmentError( 'Not a Debian-based operating system' )

    output = io.StringIO()
    regexp = re.compile( r"^ii\s+(.+?)\s+(.+?)\s.+$" )
    result = {}

    try:
        FastScript.execProgram( 'dpkg -l', stdout=output )
    except OSError as details:
        raise OSError( details )

    for line in output.getvalue().splitlines():
        if line.startswith( 'ii  ' ):
            tmp = regexp.match( line )

            name    = tmp.group(1)
            version = tmp.group(2)

            # try to cut-off the arch postfix (e.g. ":i386" or ":amd64")
            name    = name.split( ':' )[0]

            result[ name ] = version

    return result


def isInstalled( packageName ):
    """
        Looks for a certain Debian package *.deb to be installed on the
        computer running this Python process.

        The packageName must be in typical Debian/Ubuntu/... style, e.g.:
        'gcc', 'php5-cli', 'libpng2',...

        Attention: This function will not work on Microsoft Windows and
                   Non-Debian-based Linux distributions unless the 'dpkg'
                   utility is present. If 'dpkg' cannot be executed,
                   an OSError will be thrown.
    """
    global _debPkgCache

    Any.requireIsTextNonEmpty( packageName )

    if not _debPkgCache:
        try:
            _debPkgCache = getSystemPackages()
        except OSError as details:
            raise OSError( details )

    return packageName in _debPkgCache


def getDepInstallCmd( canonicalPaths ):
    """
        Returns the Debian/Ubuntu command-line to install all the
        listed packages.

        Example:
            toAptDepsCmd( [ 'deb://foo', 'deb://bar', 'deb://baz' ] )
            'apt install foo bar baz'

        If 'canonicalPaths' does not contain any item starting with
        'deb://' the function will return None.
    """
    Any.requireIsListNonEmpty( canonicalPaths )

    expr     = re.compile( '^deb://(.+)' )
    result   = '$ apt install'
    debFound = False

    for canonicalPath in canonicalPaths:
        tmp = expr.match( canonicalPath )

        if tmp:
            debFound = True
            pkgName  = tmp.group(1)
            Any.requireIsTextNonEmpty( pkgName )

            result   = '%s %s' % ( result, pkgName )


    return result if debFound else None


# EOF
