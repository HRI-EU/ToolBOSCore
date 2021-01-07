#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Operator console widget
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

from PyQt5.QtCore    import QEvent, Qt, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *

from ToolBOSCore.Util import Any


class ConsoleWidget( QGroupBox, object ):

    localCommand       = pyqtSignal( str )
    remoteCommand      = pyqtSignal( str )
    localReturnPressed = pyqtSignal()
    emptyRemoteCommand = pyqtSignal()


    def __init__( self, parent=None ):

        super( QGroupBox, self ).__init__( 'operator shell' )

        self._localShellLabel  = QLabel( 'execute on localhost:', parent )
        self._localShell       = Console( parent )
        self._localShell.setToolTip( 'execute command on operator machine' )

        self._remoteShellLabel = QLabel( 'execute on all remote hosts:', parent )
        self._remoteShell      = Console( parent )
        self._remoteShell.setToolTip( 'execute command on each connected compile host' )

        layout = QVBoxLayout()
        layout.addWidget( self._localShellLabel )
        layout.addWidget( self._localShell )
        layout.addWidget( self._remoteShellLabel )
        layout.addWidget( self._remoteShell )

        self._localShell.returnPressed.connect( self._onLocalShellInput )
        self._remoteShell.returnPressed.connect( self._onRemoteShellInput )

        self.setLayout( layout )

        self.lastUsedShell = self._localShell


    def addCommandToHistory_local( self, command ):
        self._localShell.addCommandToHistory( command )


    def addCommandToHistory_remote( self, command ):
        self._remoteShell.addCommandToHistory( command )


    def clear( self ):
        self._localShell.setText( '' )
        self._remoteShell.setText( '' )


    def setEnabled( self, status ):
        self._localShell.setEnabled( status )
        self._remoteShell.setEnabled( status )


    def setFocus( self, Qt_FocusReason=None ):
        """
            Qt_FocusReason is ignored and only kept for consistency because
            we override a method from QWidget.
        """
        self.lastUsedShell.setFocus()


    def _onLocalShellInput( self ):
        self.lastUsedShell = self._localShell

        command = self._localShell.text( )

        self.clear()

        self.localCommand.emit( command )


    def _onRemoteShellInput( self ):
        self.lastUsedShell = self._remoteShell

        command = self._remoteShell.text( )

        self.clear()

        self.remoteCommand.emit( command )


# noinspection PyUnresolvedReferences
class Console( QLineEdit, object ):
    """
        Subclass of QLineEdit which looks for Key up/down events, and in case
        uses previously stored commands to emulate shell-style working.
    """

    def __init__( self, parent=None ):
        super( QLineEdit, self ).__init__( parent )

        self.cmdHistory    = []
        self.cmdHistoryIdx = 0

        self.returnPressed.connect( self._onTextInput )
        self.installEventFilter( self )


    def addCommandToHistory( self, command ):
        Any.requireIsTextNonEmpty( command )

        self.cmdHistory.append( command )
        self.cmdHistoryIdx = len( self.cmdHistory )    # last elem = total number
        logging.debug( 'history command %d: %s', len( self.cmdHistory ),
                                                 command )


    def eventFilter( self, obj, event ):
        if event.type() == QEvent.KeyPress:

            keyUpDown = False

            if event.key() == Qt.Key_Up:
                if self.cmdHistoryIdx > 0:
                    self.cmdHistoryIdx -= 1
                    logging.debug( 'self.cmdHistoryIdx=%d', self.cmdHistoryIdx )
                    keyUpDown = True

            elif event.key() == Qt.Key_Down:
                if self.cmdHistoryIdx < len(self.cmdHistory):
                    self.cmdHistoryIdx += 1
                    logging.debug( 'self.cmdHistoryIdx=%d', self.cmdHistoryIdx )
                    keyUpDown = True

            if keyUpDown:
                try:
                    self.setText( self.cmdHistory[ self.cmdHistoryIdx ] )
                    logging.debug( 'setText=%s', self.cmdHistory[ self.cmdHistoryIdx ] )
                except IndexError:
                    pass
            # else a normal command or backspace or whatsoever was entered

        return False


    def _onTextInput( self ):
        command = str(self.text()).strip()

        # do not store empty command in history
        if command:
            self.addCommandToHistory( command )


# EOF
