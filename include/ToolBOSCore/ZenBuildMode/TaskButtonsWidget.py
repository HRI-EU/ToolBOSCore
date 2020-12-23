#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Main task buttons (build, clean, install, exit,...)
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


import os

from PyQt5.QtCore    import pyqtSignal
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from ToolBOSCore.Storage      import ProxyDir, SIT
from ToolBOSCore.Util         import Any


class TaskButtonsWidget( QGroupBox, object ):
    """
        Provides a group box with the main control buttons (build, clean,
        install, run unittest,...)
    """

    build         = pyqtSignal()
    clean         = pyqtSignal()
    globalInstall = pyqtSignal()
    proxyInstall  = pyqtSignal()
    quit          = pyqtSignal()
    test          = pyqtSignal()

    hasProxy      = ProxyDir.isProxyDir( SIT.getPath() )


    def __init__( self ):
        super( QGroupBox, self ).__init__( 'commands' )

        self._buildButton      = QPushButton( "&build" )
        self._cleanButton      = QPushButton( "&distclean" )
        self._testButton       = QPushButton( "run &testsuite" )
        self._proxyInstButton  = QPushButton( "pro&xy inst." )
        self._globalInstButton = QPushButton( "global &inst." )
        self._quitButton       = QPushButton( "&quit" )

        self._cleanButton.setToolTip( 'delete build artefacts' )
        self._buildButton.setToolTip( 'compile for selected platforms' )
        self._proxyInstButton.setToolTip( 'install into Proxy-SIT' )
        self._globalInstButton.setToolTip( 'globally install into SIT' )
        self._testButton.setToolTip( 'start unittest (if present)' )

        if not self.hasProxy:
            self._proxyInstButton.setToolTip( 'No Proxy-SIT available' )
            self._proxyInstButton.setEnabled( False )

        self._cleanButton.pressed.connect( self.clean.emit )
        self._buildButton.pressed.connect( self.build.emit )
        self._proxyInstButton.pressed.connect( self.proxyInstall.emit )
        self._globalInstButton.pressed.connect( self.globalInstall.emit )
        self._testButton.pressed.connect( self.test.emit )
        self._quitButton.pressed.connect( self.quit.emit )

        # set start-up focus and run
        self._buildButton.setFocus()

        self._layout = QGridLayout()
        self._layout.addWidget( self._cleanButton,      1, 1 )
        self._layout.addWidget( self._buildButton,      1, 2 )
        self._layout.addWidget( self._proxyInstButton,  2, 1 )
        self._layout.addWidget( self._globalInstButton, 2, 2 )
        self._layout.addWidget( self._testButton,       3, 1 )
        self._layout.addWidget( self._quitButton,       3, 2 )


        if not os.path.exists( 'unittest.sh' ) and \
           not os.path.exists( 'unittest.bat' ):

            self._testButton.setEnabled( False )
            self._testButton.setToolTip( 'unittest.sh or unittest.bat not found' )

        self.setLayout( self._layout )


    def setEnabled( self, status, button='all' ):
        Any.requireIsBool( status )
        Any.requireIsTextNonEmpty( button )

        if button == 'all':
            self._buildButton.setEnabled( status )
            self._cleanButton.setEnabled( status )
            self._globalInstButton.setEnabled( status )
            self._proxyInstButton.setEnabled( status and self.hasProxy )
            self._testButton.setEnabled( status )

        elif button == 'build':
            self._buildButton.setEnabled( status )

        elif button == 'clean':
            self._cleanButton.setEnabled( status )

        elif button == 'globalInstall':
            self._globalInstButton.setEnabled( status )

        elif button == 'proxyInstall':
            self._proxyInstButton.setEnabled( status and self.hasProxy  )

        elif button == 'test':
            self._testButton.setEnabled( status )

        else:
            raise ValueError( 'unknown button: %s' % button )


# EOF
