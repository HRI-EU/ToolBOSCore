# -*- coding: utf-8 -*-
#
#  Dynamic loading of C libraries
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


import ctypes
import logging
import os

from ToolBOSCore.Platforms import Platforms
from ToolBOSCore.Util      import Any
from ToolBOSCore.Util      import FastScript


def computeLibName( name, version='' ):
    """
        Returns the proper name of a shared library, depending on the
        platform, f.i. with '.so' or '.dll' extension and the like.
    """
    Any.requireIsTextNonEmpty( name )
    Any.requireIsText( version )

    if version:
        postfix = '.' + version
    else:
        postfix = ''

    if Platforms.getSystemType() == 'win':
        return '%s.dll%s' % (name, postfix)
    else:
        return 'lib%s.so%s' % (name, postfix)


def locate( libName ):
    """
        Searches within LD_LIBRARY_PATH for the given library,
        and in case returns the absolute path to it.

        If not found raises an EnvironmentError.
    """
    Any.requireIsTextNonEmpty( libName )


    if Platforms.getSystemType() == 'win':
        envName = 'PATH'
    else:
        envName = 'LD_LIBRARY_PATH'

    searchPath = FastScript.getEnv( envName )
    Any.requireIsTextNonEmpty( searchPath )


    for path in searchPath.split( ':' ):
        # logging.debug( path )

        libPath = os.path.join( path, libName )

        if os.path.exists( libPath ):
            logging.debug( 'found %s', libPath )
            return libPath
        # else:
        #     logging.debug( '%s: No such file', libPath )


    raise EnvironmentError( '%s not found within LD_LIBRARY_PATH' % libName )


def loadLibrary( name, version='' ):
    """
        Returns a handle to the given library.
    """
    Any.requireIsTextNonEmpty( name )


    # if neither '.so' nor '.dll' in the name, assume it is the inner part
    # of the library only

    ext = '.dll' if Platforms.getSystemType() == 'win' else '.so'

    if ext in name:
        libName = name
    else:
        libName = computeLibName( name, version )


    libPath = locate( libName )
    logging.debug( 'loading %s', libPath )
    logging.debug( 'LD_LIBRARY_PATH: %s', FastScript.getEnv( 'LD_LIBRARY_PATH' ) )

    try:
        if Platforms.getSystemType() == 'win':
            libHandle = ctypes.WinDLL( libPath )
        else:
            libHandle = ctypes.CDLL( libPath, ctypes.RTLD_GLOBAL )

    except OSError as details:
        raise OSError( details )


    _setDebugLevel( libHandle )
    _setAssertHandler( libHandle )


    return libHandle


def _setDebugLevel( libHandle ):
    """
        If the library makes use of ToolBOS's ANY_LOG framework, set the
        debug level appropriately according to the debugLevel used in Python.
    """
    Any.requireIsInstance( libHandle, ctypes.CDLL )


    try:
        debugLevel = Any.getDebugLevel()

        # Any.py logs at maximum level 5 while the Any.c logs up to infinity.
        # therefore we generally suppress setting the loglevel if above 5.

        if debugLevel < 5:
            libHandle.Any_setDebugLevel( Any.getDebugLevel() )


        libHandle.Any_setShortLogFormat()

    except AttributeError:
        # likely does not link against ToolBOSCore library
        pass


def _setAssertHandler( libHandle ):
    """
        If the library makes use of ToolBOS's assertion framework
        (ANY_REQUIRE and friends), change the default implementation
        (= quit process) to raising of an exception instead.
    """
    Any.requireIsInstance( libHandle, ctypes.CDLL )

    ANYEXITCALLBACK = ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p )
    pythonCallBack  = ANYEXITCALLBACK( _pythonicToolBOSExit )

    try:
        libHandle.AnyExit_setCallBack.restype = None
        libHandle.AnyExit_setCallBack( pythonCallBack, 0, 0 )

    except AttributeError:
        # likely does not link against ToolBOSCore library
        pass


def _pythonicToolBOSExit( *kwargs ):
    raise AssertionError( 'intercepted exit from C library' )


# EOF
