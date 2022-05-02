#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  QMessageBox showing an error popup + error log on console
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
import sys
import traceback

from PyQt5.QtWidgets import QMessageBox, QSizePolicy, QTextEdit

from ToolBOSCore.Util import Any


class QMessageBoxResizable( QMessageBox ):
    _minWidth  = 400
    _minHeight = 200

    # Resize a QMessageBox is a bit tricky because we also need to resize
    # the internal message
    def event( self, e ):
        result = super( QMessageBoxResizable, self ).event( e )
        self.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        self.setMinimumHeight( self._minHeight )
        self.setMaximumHeight( 16777215 )
        self.setMinimumWidth( self._minWidth )
        self.setMaximumWidth( 16777215 )

        message = self.findChild( QTextEdit )

        if message:
            message.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
            message.setMinimumHeight( self._minHeight )
            message.setMaximumHeight( 16777215 )
            message.setMinimumWidth( self._minWidth )
            message.setMaximumWidth( 16777215 )

        return result


def ErrorDialog( title, msg, printException=False, resizable=False ):
    msg = str( msg )                             # also accept exception types

    Any.requireIsTextNonEmpty( title )
    Any.requireIsTextNonEmpty( msg )

    excType, _excValue, excTraceback = sys.exc_info()
    if excType:
        if hasattr( excType, 'description' ):
            description = excType.description
        else:
            description = str( excType )
    else:
        description = excType = 'Error'

    if printException or Any.getDebugLevel() >= 5:
        tbs = traceback.format_tb( excTraceback )
        logging.error( '%s, %s', excType, msg )
        logging.error( ''.join( tbs ) )
    else:
        logging.error( msg )

    msgBox = QMessageBoxResizable() if resizable else QMessageBox()
    msgBox.setIcon( QMessageBox.Critical )
    msgBox.setText( description )
    msgBox.setWindowTitle( title )
    msgBox.setDetailedText( msg )
    msgBox.setStandardButtons( QMessageBox.Ok )
    msgBox.setEscapeButton( QMessageBox.Ok )

    msgBox.exec_()


# EOF
