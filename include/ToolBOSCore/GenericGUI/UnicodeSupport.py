#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Various UTF-8 / -16 conversion functions, incl. Qt types
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


import logging

from PyQt5.QtCore import QByteArray

from ToolBOSCore.Util import Any


def convert( x ):
    """
        Converts a string of various types to unicode-aware object:

        accepts objects of type:
            * bytes
            * str
            * unicode
            * QByteArray

        returns:
            Py2: unicode
            Py3: str
    """
    if isinstance( x, QByteArray ):
        return convertQByteArray( x )

    elif isinstance( x, bytes ):
        return convertBytes( x )

    elif isinstance( x, str ):
        return convertStr( x )

    elif isinstance( x, unicode ):
        return x

    else:
        raise ValueError( 'unexpected datatype: %s' % type( x ) )


def convertBytes( b ):
    """
        Converts a string of Python's 'byte' type to 'str'.
    """
    Any.requireIsInstance( b, bytes )

    return b.decode( 'utf8' )


def convertQByteArray( qba ):
    """
        Converts a string of PyQt's 'QByteArray' type to:

        Py2: unicode
        Py3: str
    """
    Any.requireIsInstance( qba, QByteArray )

    data = qba.data()
    Any.requireIsInstance( data, bytes )

    return convertBytes( data )


def convertStr( s ):
    """
        Converts a string of Python's 'str' type to:

        Py2: unicode
        Py3: str (no need to do anything)
    """
    Any.requireIsInstance( s, str )

    # no need to do anything (str-objects are unicode-ready)

    return s


# EOF
