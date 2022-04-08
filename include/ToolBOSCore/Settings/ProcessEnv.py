# -*- coding: utf-8 -*-
#
#  Python process environment
#  (equivalents to "source BashSrc", "which <command>" etc.)
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
import os
import sys

from ToolBOSCore.Packages        import PackageDetector, ProjectProperties
from ToolBOSCore.Storage         import SIT
from ToolBOSCore.Storage.PkgInfo import getPkgInfoContent
from ToolBOSCore.Util            import Any
from ToolBOSCore.Util            import FastScript


#----------------------------------------------------------------------------
# Public functions
#----------------------------------------------------------------------------


def checkAvailable( command:str, package:str ) -> None:
    """
        Checks if 'command' is found in $PATH.

        If not, attempts to source the given SIT package to make it available.

        If afterwards 'command' is still not found in $PATH, an
        EnvironmentError is raised.
    """
    Any.requireIsTextNonEmpty( command )
    Any.requireIsTextNonEmpty( package )

    if not which( command ):
        source( package )

    requireCommand( command )


def source( package ):
    """
        Python equivalent of "source BashSrc" from SIT, in order to setup
        PATH, LD_LIBRARY_PATH,... within the Python process.

        @anchor ProcessEnv_source
    """
    ProjectProperties.requireIsCanonicalPath( package )

    sourced = FastScript.getEnv( 'TOOLBOSCORE_SOURCED' )
    Any.requireMsg( sourced, '$TOOLBOSCORE_SOURCED must not be empty' )

    # avoid double-sourcing
    if package in sourced:
        return True

    ProjectProperties.requireIsInstalled( package )


    logging.debug( 'source "${SIT}/' + package + '/BashSrc"   # actually pkgInfo.py' )
    sourced = '%s %s' % ( package, sourced )
    FastScript.setEnv( 'TOOLBOSCORE_SOURCED', sourced )


    # load pkgInfo.py (if exists)
    try:
        content = getPkgInfoContent( project=package )
    except AssertionError:
        return True             # no such file, this is OK
    except ( IOError, OSError ) as details:
        logging.error( details )
        return False


    # setup environment of this package
    try:
        envVars = content['envVars']
    except KeyError:
        envVars = []            # no such setting, this is OK


    sitPath = SIT.getPath()

    for name, value in envVars:

        # replace known placeholdes
        value = value.replace( '${INSTALL_ROOT}',
                               os.path.join( sitPath, package ) )

        FastScript.setEnv_withExpansion( name, value )


    # source dependent packages
    try:
        # TODO: eventually extend to sourcing recommended/suggested packages
        depList = content['depends']
    except ( AssertionError, KeyError ):
        depList = []            # no such setting, this is OK

    for dep in depList:
        if not dep.startswith( 'deb://' ):
            source( SIT.strip( dep ) )


    # special treatment of PYTHONPATH:
    # After sourcing add new entries in PYTHONPATH to sys.path
    _expandSysPath()

    return True


def sourceFromHere():
    """
        Python equivalent of "source BashSrc" for package in source tree, in order to setup
        PATH, LD_LIBRARY_PATH,... within the Python process.

        @anchor ProcessEnv_source
    """
    detector = PackageDetector.PackageDetector()

    libDirArch = detector.libDirArch
    FastScript.appendEnv( 'LD_LIBRARY_PATH', libDirArch )

    binDir = ':' + detector.binDir
    FastScript.appendEnv( 'PATH', binDir )

    binDirArch = ':' + detector.binDirArch
    FastScript.appendEnv( 'PATH', binDirArch )


def which( command ):
    """
        Python equivalent of the shell command "which <command>".
    """
    path = FastScript.getEnv( 'PATH' )
    Any.requireIsTextNonEmpty( path )

    for item in path.split( ':' ):
        candidate = os.path.join( item, command )

        if os.path.exists( candidate ):
            return candidate

    return None


def requireCommand( command:str ) -> None:
    """
        Throws an EnvironmentError if 'command' is not installed.
    """
    Any.requireIsTextNonEmpty( command )

    if not which( command ):
        raise EnvironmentError( f'{command}: command not found' )


def _expandSysPath():
    """
        Checks which entries of PYTHONPATH are not in sys.path, yet,
        and appends those to sys.path.
    """
    pythonPath      = FastScript.getEnv( 'PYTHONPATH' )

    if not pythonPath:
        return

    for item in pythonPath.split( ':' ):
        if item not in sys.path:
            logging.debug( "sys.path.append( '%s' )", item )
            sys.path.append( item )


# EOF
