#!/usr/bin/env python3
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
from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.Packages.CopyrightHeader import getCopyright
from ToolBOSCore.Util                     import FastScript


class AboutDialog( QDialog ):

    _font = QFont( "Courier", 10 )


    def __init__( self, parent=None ):
        super( AboutDialog, self ).__init__( parent )

        logo = QLabel()
        logo.setPixmap( PixmapProvider.getPixmap( 'ToolBOS-Logo-small' ) )
        logo.setAlignment( Qt.AlignCenter )

        copyrightInfo = QPlainTextEdit()
        copyrightInfo.setFont( self._font )
        copyrightInfo.setPlainText( getCopyright() )
        copyrightInfo.setReadOnly( True )

        layout = QGridLayout()
        layout.addWidget( logo,          0, 0 )
        layout.addWidget( copyrightInfo, 0, 1 )

        tcRoot     = FastScript.getEnv( 'TOOLBOSCORE_ROOT' )
        tcDetector = PackageDetector( tcRoot )
        tcDetector.retrieveMakefileInfo()
        tcVersion  = tcDetector.packageVersion
        tcVersion += '.%d' % tcDetector.patchlevel if tcDetector.patchlevel else ''
        tcInfo     = '%s (Version: %s)' % ( tcRoot, tcVersion )

        mwRoot     = FastScript.getEnv( 'TOOLBOSMIDDLEWARE_ROOT' )
        if mwRoot:
            mwDetector = PackageDetector( mwRoot )
            mwDetector.retrieveMakefileInfo()
            mwVersion  = mwDetector.packageVersion
            mwVersion += '.%d' % mwDetector.patchlevel if mwDetector.patchlevel else ''
            mwInfo     = '%s (Version: %s)' % ( mwRoot, mwVersion )
        else:
            mwInfo     = 'not available'

        #          label text (key)       value                                     lines to display
        info = [ ( 'ToolBOS Core',        tcInfo,                                   1 ),
                 ( 'ToolBOS Middleware',  mwInfo,                                   1 ),
                 ( '$SIT',                FastScript.getEnv( 'SIT'               ), 1 ),
                 ( '$MAKEFILE_PLATFORM',  FastScript.getEnv( 'MAKEFILE_PLATFORM' ), 1 ),
                 ( '$PATH',               FastScript.getEnv( 'PATH'              ), 3 ),
                 ( '$LD_LIBRARY_PATH',    FastScript.getEnv( 'LD_LIBRARY_PATH'   ), 3 ),
                 ( '$PYTHONPATH',         FastScript.getEnv( 'PYTHONPATH'        ), 3 ),
                 ( 'Python interpreter',  sys.executable,                           1 ),
                 ( 'Python version',      sys.version,                              1 ),
                 ( 'Hostname',            socket.gethostname(),                     1 ),
                 ( 'CPUs',                str( multiprocessing.cpu_count() ),       1 ),
                 ( 'Memory',              'calculating...',                         1 ) ]

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
            valueWidget.setFont( self._font )

            if key == 'Memory':
                memText = valueWidget         # store a handle to this widget

            layout.addWidget( keyWidget,   i, 0 )
            layout.addWidget( valueWidget, i, 1 )
            i += 1

        self._standardButtons = QDialogButtonBox( QDialogButtonBox.Close )
        self._standardButtons.clicked.connect( self.close )

        layout.addWidget( self._standardButtons, i, 1 )

        # noinspection PyArgumentList
        dialogWidth = QApplication.desktop().screenGeometry().width() / 3 * 2

        self.setLayout( layout )
        self.setMinimumWidth( dialogWidth )
        self.setModal( True )
        self.setWindowTitle( 'About ToolBOS SDK' )

        self._thread = self._FreeMemDetectorThread()
        self._thread.start()
        self._thread.newData.connect( lambda s: memText.setText( s ) )

        # stop thread upon close
        self.accepted.connect( self._thread.terminate )
        self.rejected.connect( self._thread.terminate )
        self._standardButtons.clicked.connect( self._thread.terminate )


    class _FreeMemDetectorThread( QThread, object ):

        newData = pyqtSignal( str )

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


if __name__ == '__main__':
    app    = QApplication( [] )
    app.setStyle( 'fusion' )

    aboutDialog = AboutDialog()
    aboutDialog.show()

    app.exec_()


# EOF
