# -*- coding: utf-8 -*-
#
#  Functions to query the user's dtbos.cfg file
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
import re

from ToolBOSCore.Util import FastScript, Any


def getRecentProject():
    """
        Returns the path to the last graph opened with DTBOS, or None
        if unable to determine (not set, or file not existing).
    """
    return getConfigValue( 'RecentProject0' )


def getConfigFilePath():
    """
        Returns the path to the user's "dtbos.cfg", but it does not
        necessarily have to exist.
    """
    return os.path.expanduser( '~/.HRI/ToolBOS/dtbos.cfg' )


def getConfigContent():
    """
        Returns the content of dtbos.cfg as list of strings.

        Returns empty list if dtbos.cfg does not exist.
    """
    try:
        return FastScript.getFileContent( getConfigFilePath(),
                                          splitLines=True )
    except AssertionError:
        return []


def getConfigValue( key ):
    """
        Returns the value of the specified DTBOS config key.

        Returns None if not found or the configfile does not exist.
    """
    Any.requireIsTextNonEmpty( key )

    expr = re.compile( '^%s=(.*)\n' % key )

    for line in getConfigContent():
        tmp = expr.match( line )

        if tmp:
            return tmp.group(1)

    return None


# EOF
