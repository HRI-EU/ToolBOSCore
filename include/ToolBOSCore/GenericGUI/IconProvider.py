#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Retrieves icon resources by name
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

from PyQt5.QtGui import QIcon

from ToolBOSCore.Packages import ProjectProperties
from ToolBOSCore.Settings import ToolBOSConf
from ToolBOSCore.Util     import Any


_iconCache     = {}
_iconDir       = None
_useThemeIcons = ToolBOSConf.getConfigOption( 'Qt_useThemeIcons' )


def getIcon( name ):
    """
        Returns a QIcon for the provided 'name', which used to be an action,
        extern program identifier, or other kind of operation.
    """
    Any.requireIsTextNonEmpty( name )

    icon = None


    if _useThemeIcons:
        try:
            icon = _getFreeDesktopIcon( name )
        except EnvironmentError:
            icon = None


    if icon is None:
        icon = _getBundledIcon( name )


    return icon


def _getFreeDesktopIcon( name ):
    """
        Get an icon from the desktop environment's icon theme
    """
    Any.requireIsTextNonEmpty( name )

    if QIcon.hasThemeIcon( name ):
        logging.debug( 'using freedesktop icon: %s', name )
        return QIcon.fromTheme( name )

    else:
        msg = "%s: No such icon in the desktop environment's icon theme" % name
        raise EnvironmentError( msg )


def _getBundledIcon( name ):
    """
        Get an icon bundled with the application package
    """
    global _iconCache
    global _iconDir

    Any.requireIsTextNonEmpty( name )

    try:
        # lookup cache
        return _iconCache[ name ]

    except KeyError:

        if _iconDir is None:
            scriptDir   = os.path.dirname( sys.argv[0] )
            topLevelDir = ProjectProperties.detectTopLevelDir( scriptDir )

            _iconDir    = os.path.join( topLevelDir, 'share/icons' )
            logging.debug( 'application icon dir: %s', _iconDir )
            Any.requireIsDir( _iconDir )


        # Even though the SVG would scale better, prefer the PNG version
        # as Qt's implementation does not support all SVG features, leading
        # to console warnings and rendering artefacts (see TBCORE-1832).

        svgFile = os.path.join( _iconDir, name + '.svg' )
        pngFile = os.path.join( _iconDir, name + '.png' )

        if os.path.exists( pngFile ):
            filePath = pngFile
        elif os.path.exists( svgFile ):
            filePath = svgFile
        else:
            logging.error( 'missing icon file: %s.{svg,png}', name )

            # provide empty fallback icon to prevent crashes
            return QIcon()

        Any.requireIsFile( filePath )
        logging.debug( 'using bundled icon: %s', filePath )

        # load icon and put in cache
        icon = QIcon( filePath )
        _iconCache[ icon ] = icon

        return icon


# EOF
