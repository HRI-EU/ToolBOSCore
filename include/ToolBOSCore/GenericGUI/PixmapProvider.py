#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Retrieves pixmap resources by name
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
import os
import sys

from PyQt5.QtGui import QPixmap

from ToolBOSCore.Packages import ProjectProperties
from ToolBOSCore.Util     import FastScript


_pixmapCache = {}
_pixmapDir   = None


def getPixmap( name ):
    """
        Returns a QPixmap for the provided 'name', which used to be
        the short form of a filename (without path and file extension).
    """
    FastScript.requireIsTextNonEmpty( name )

    global _pixmapCache
    global _pixmapDir


    try:
        # lookup cache
        return _pixmapCache[ name ]

    except KeyError:

        if _pixmapDir is None:
            scriptDir   = os.path.dirname( sys.argv[0] )
            topLevelDir = ProjectProperties.detectTopLevelDir( scriptDir )

            _pixmapDir    = os.path.join( topLevelDir, 'share/pixmaps' )
            FastScript.requireIsDir( _pixmapDir )

        filePath = os.path.join( _pixmapDir, name + '.png' )
        FastScript.requireIsFile( filePath )
        logging.debug( 'using pixmap: %s', filePath )

        # load pixmap and put in cache
        pixmap = QPixmap( filePath )
        _pixmapCache[ pixmap ] = pixmap

        return pixmap


# EOF
