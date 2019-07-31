#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Generic About-dialog for GUIs
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
import multiprocessing
import socket
import sys

from PyQt5.QtCore    import pyqtSignal, QThread, Qt
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from ToolBOSCore.GenericGUI               import PixmapProvider
from ToolBOSCore.Packages.CopyrightHeader import getCopyright
from ToolBOSCore.Util                     import FastScript


class AboutDialog( QWidget ):

    def __init__( self, parent ):
        super( AboutDialog, self ).__init__( parent )

        logo = QLabel()
        logo.setPixmap( PixmapProvider.getPixmap( 'ToolBOS-Logo-small' ) )
        logo.setAlignment( Qt.AlignCenter )

        palette = logo.palette()
        palette.setColor( QPalette.Background, QColor( 255, 255, 255 ) )
        self.setAutoFillBackground( True )
        self.setPalette( palette )

        copyrightInfo = QTextEdit()
        copyrightInfo.setText( getCopyright() )
        copyrightInfo.setReadOnly( True )

        self._dialog = QDialog( parent )

        layout = QGridLayout()
        layout.addWidget( logo,          0, 0 )
        layout.addWidget( copyrightInfo, 0, 1 )

        #          label text (key)      value                      lines to display
        info = [ ( 'TOOLBOSCORE_ROOT',   FastScript.getEnv( 'TOOLBOSCORE_ROOT'  ), 1 ),
                 ( 'TOOLBOSMIDDLEWARE_ROOT', FastScript.getEnv( 'TOOLBOSMIDDLEWARE_ROOT' ), 1 ),
                 ( 'SIT',                FastScript.getEnv( 'SIT'               ), 1 ),
                 ( 'MAKEFILE_PLATFORM',  FastScript.getEnv( 'MAKEFILE_PLATFORM' ), 1 ),
                 ( 'PATH',               FastScript.getEnv( 'PATH'              ), 3 ),
                 ( 'LD_LIBRARY_PATH',    FastScript.getEnv( 'LD_LIBRARY_PATH'   ), 3 ),
                 ( 'PYTHONPATH',         FastScript.getEnv( 'PYTHONPATH'        ), 3 ),
                 ( 'python interpreter', sys.executable,                           1 ),
                 ( 'python version',     sys.version,                              1 ),
                 ( 'hostname',           socket.gethostname(),                     1 ),
                 ( 'CPUs',               str( multiprocessing.cpu_count() ),       1 ),
                 ( 'memory',             'calculating...',                         1 ) ]

        i       = 1
        memText = None

        for key, value, length in info:

            keyWidget = QLabel( key + ':' )

            if length == 1:
                valueWidget = QLineEdit( value )
            else:
                valueWidget = QPlainTextEdit( value )
                valueWidget.setMaximumHeight( 80 )

            valueWidget.setReadOnly( True )
            valueWidget.setFont( QFont( "Courier", 10 ) )

            if key == 'memory':
                memText = valueWidget         # store a handle to this widget

            layout.addWidget( keyWidget,   i, 0 )
            layout.addWidget( valueWidget, i, 1 )
            i += 1

        okButton = QPushButton( '&OK' )
        okButton.setFocus()
        okButton.setMaximumWidth( 200 )
        okButton.clicked.connect( self._dialog.close )

        layout.addWidget( okButton, i, 1 )

        # noinspection PyArgumentList
        dialogWidth = QApplication.desktop().screenGeometry().width() / 3 * 2

        self._dialog.setLayout( layout )
        self._dialog.setMinimumWidth( dialogWidth )
        self._dialog.setModal( True )
        self._dialog.show()

        self._thread = self._FreeMemDetectorThread()
        self._thread.start()
        self._thread.newData.connect( lambda s: memText.setText( s ) )

        # stop thread upon close
        self._dialog.accepted.connect( self._thread.terminate )
        self._dialog.rejected.connect( self._thread.terminate )
        okButton.clicked.connect( self._thread.terminate )


    class _FreeMemDetectorThread( QThread, object ):

        newData = pyqtSignal( str )

        def __init__( self ):
            QThread.__init__( self )


        def run( self ):
            from psutil import virtual_memory
            from time   import sleep

            while True:
                mem     = virtual_memory()
                memText = 'total: %s MB, used: %s MB (%d%%)' % \
                          ( mem.total / ( 1024 * 1024 ),
                            ( mem.total - mem.available )  / ( 1024 * 1024 ),
                            mem.percent )

                logging.debug( memText )
                self.newData.emit( memText )
                sleep( 1 )


# EOF
