# -*- coding: utf-8 -*-
#
#  Bindings to Serialize subsystem from ToolBOSCore C library
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

from ToolBOSCore.Util import Any
from ToolBOSCore.Util import DynamicLoader


formatsAvailable = frozenset( [ 'Ascii', 'Binary', 'Json', 'Matlab',
                                'Python', 'Xml' ] )


def requireValidFormat( formatName ):
    Any.requireIsTextNonEmpty( formatName )

    Any.requireIsIn( formatName, formatsAvailable )


class AbstractSerializer( object ):
    """
        Superclass of the Serialize subsystem.
    """

    def __init__( self, serializeFunc ):

        Any.requireIsCallable( serializeFunc )


        self._lowLevelSerializer = None
        self._toolbosLib         = DynamicLoader.loadLibrary( 'ToolBOSLib' )
        self._serFunc            = serializeFunc

        Any.requireIsNotNone( self._toolbosLib )
        Any.requireIsNotNone( self._serFunc )

        self._toolbosLib.CalcSizeSerializer_new.restype           = ctypes.c_void_p
        self._toolbosLib.CalcSizeSerializer_init.argtypes         = [ ctypes.c_void_p ]
        self._toolbosLib.CalcSizeSerializer_open.restype          = ctypes.c_void_p
        self._toolbosLib.CalcSizeSerializer_open.argtypes         = [ ctypes.c_void_p, ctypes.c_char_p ]
        self._toolbosLib.CalcSizeSerializer_getTotalSize.restype  = ctypes.c_long
        self._toolbosLib.CalcSizeSerializer_getTotalSize.argtypes = [ ctypes.c_void_p ]



class CalcSizeSerializer( AbstractSerializer ):
    """
        Performs a dummy-serialization with the only goal to determine the
        length in the target Serialization format.
    """
    def __init__( self, serializeFunc ):
        super( CalcSizeSerializer, self ).__init__( serializeFunc )

        self._serializer = self._toolbosLib.CalcSizeSerializer_new()
        Any.requireIsNotNone( self._serializer )
        self._toolbosLib.CalcSizeSerializer_init( self._serializer )


    def getTotalSize( self, data, name, formatName ):
        Any.requireIsNotNone( data )
        Any.requireIsTextNonEmpty( name )
        requireValidFormat( formatName )

        self._lowLevelSerializer = self._toolbosLib.CalcSizeSerializer_open( self._serializer, formatName )
        logging.info( self._lowLevelSerializer )

        self._serFunc( data, name, self._lowLevelSerializer )

        logging.debug( 'fetching total size...' )
        serializedSize = self._toolbosLib.CalcSizeSerializer_getTotalSize( self._serializer )
        logging.debug( 'done' )

        return serializedSize


# EOF
