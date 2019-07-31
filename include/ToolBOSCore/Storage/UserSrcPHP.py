# -*- coding: utf-8 -*-
#
#  Settings from legacy userSrc.php file
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


import os
import re

from ToolBOSCore.Util import Any
from ToolBOSCore.Util import FastScript


#----------------------------------------------------------------------------
# Public functions
#----------------------------------------------------------------------------


def getUserSrcAsXML( filename ):
    """
        Executes 'UserSrcToXML.php' for the specified file, returning its
        full, unprocessed console output (which should be simplfied XML),
        e.g.:

            '<env name="PATH" value="${TOOLBOSCORE_ROOT}/bin:${PATH}"/>
             <env name="HOSTOS" value="${MAKEFILE_OS}"/>
             <env name="HOSTARCH" value="${MAKEFILE_CPU}"/>
             <alias name=""dmake" value=""make -j 16"">/>'

        When parsing the results, be aware of the duplicated double-quotes
        when strings themselves contain double-quotes.
    """
    from six import StringIO

    output = StringIO()
    exe    = os.getenv( 'TOOLBOSCORE_ROOT' ) + '/include/ConvertUserSrcToXML.php'
    cmd    = '%s %s' % ( exe, filename )

    FastScript.execProgram( cmd, stdout=output )

    return output.getvalue()


def getEnvSettingsFromUserSrcContent( xmlData ):
    """
        Returns a list of tuples with the environment variable settings
        extracted from the provided XML data.

        Use getUserSrcAsXML() to read-in the file content.

        This function explicitly does not return a Python dict to preserve
        the order of appearance in the file.
    """
    Any.requireIsString( xmlData )

    pattern = re.compile( '^\s+<env\sname="(.+?)">(.+)</env>$' )
    result  = []

    for line in xmlData.split( "\n" ):
        tmp = pattern.match( line )

        if tmp:
            result.append( ( tmp.group(1), tmp.group(2) ) )

    return result


def getAliasesFromUserSrcContent( xmlData ):
    """
        Returns a list of tuples with shell alias definitions extracted from
        the provided XML data.

        Use getUserSrcAsXML() to read-in the file content.

        This function explicitly does not return a Python dict to preserve
        the order of appearance in the file.
    """
    Any.requireIsString( xmlData )

    pattern = re.compile( '^\s+<alias\sname="(.+?)">(.*)</alias>$' )
    result  = []

    for line in xmlData.split( "\n" ):
        tmp = pattern.match( line )

        if tmp:
            result.append( ( tmp.group(1), tmp.group(2) ) )

    return result


def getBashCodeFromUserSrcContent( xmlData ):
    """
        If user-specific Bash code is specified in the provided xmlData,
        a tuple of lines will be returned, an empty tuple if not found.

        Use getUserSrcAsXML() to read-in the file content.

        Note: Do not wonder about returning void, only a very few HRI-EU
              packages need to specify custom Bash code in their userSrc.php
              file.
    """
    Any.requireIsString( xmlData )

    pattern = re.compile( '^\s+<code\sshell="bash">(.*)</code>$' )
    result  = []

    for line in xmlData.split( "\n" ):
        tmp = pattern.match( line )

        if tmp:
            result.append( tmp.group(1) )

    return result


def getCmdCodeFromUserSrcContent( xmlData ):
    """
        If user-specific cmd.exe code is specified in the provided xmlData,
        a tuple of lines will be returned, an empty tuple if not found.

        Use getUserSrcAsXML() to read-in the file content.

        Note: Do not wonder about returning void, only a very few HRI-EU
              packages need to specify custom cmd.exe code in their userSrc.php
              file.
    """
    Any.requireIsString( xmlData )

    pattern = re.compile( '^\s+<code\sshell="cmd">(.*)</code>$' )
    result  = []

    for line in xmlData.split( "\n" ):
        tmp = pattern.match( line )

        if tmp:
            result.append( tmp.group(1) )

    return result


# EOF
