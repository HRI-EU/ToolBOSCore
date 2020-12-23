#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Dialog for SIT Installations
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


from PyQt5.QtCore    import pyqtSignal, QEvent, QObject, Qt
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *


class GlobalInstallDialog( QDialog, object ):
    """
        Provides a QDialog for interactively asking the globalinstall
        change type and reason.
    """

    cancelled    = pyqtSignal()
    ready        = pyqtSignal( str, str )


    def __init__( self ):
        super( GlobalInstallDialog, self ).__init__()

        self._radioGroup  = None
        self._reasonField = None

        changeType   = QLabel( 'Type of changes: ' )

        radio1       = QRadioButton( 'new feature' )
        radio2       = QRadioButton( 'bugfix' )
        radio3       = QRadioButton( 'documentation updated' )
        radio4       = QRadioButton( 'general improvements' )

        radio1.setChecked( True )
        radio1.setToolTip( 'example: "now supports shared memory"' )
        radio2.setToolTip( 'example: "buffer overflow in _doCompute() fixed"' )
        radio3.setToolTip( 'example: "PDF manual updated"' )
        radio4.setToolTip( 'example: "improved performance by 20%"' )

        self._radioGroup = QButtonGroup()
        self._radioGroup.addButton( radio1 )
        self._radioGroup.addButton( radio2 )
        self._radioGroup.addButton( radio3 )
        self._radioGroup.addButton( radio4 )

        self._radioGroup.setId( radio1, 1 )
        self._radioGroup.setId( radio2, 2 )
        self._radioGroup.setId( radio3, 3 )
        self._radioGroup.setId( radio4, 4 )

        radioLayout  = QVBoxLayout()
        radioLayout.setContentsMargins( 0, 0, 0, 0 )
        radioLayout.addWidget( radio1 )
        radioLayout.addWidget( radio2 )
        radioLayout.addWidget( radio3 )
        radioLayout.addWidget( radio4 )

        radioWidget  = QWidget()
        radioWidget.setLayout( radioLayout )

        reasonLabel  = QLabel( 'Reason: ' )

        self._reasonField  = QLineEdit()
        self._reasonField.setToolTip( 'leave an install log message' )
        self._reasonField.setMinimumWidth( 400 )

        detailsLayout = QGridLayout()
        detailsLayout.addWidget( changeType,  0, 0, Qt.AlignTop )
        detailsLayout.addWidget( radioWidget, 0, 1, Qt.AlignTop )
        detailsLayout.addWidget( reasonLabel, 1, 0, Qt.AlignTop )
        detailsLayout.addWidget( self._reasonField, 1, 1, Qt.AlignTop )

        detailsWidget = QGroupBox( 'Details' )
        detailsWidget.setLayout( detailsLayout )

        okButton     = QPushButton( '&OK' )
        okButton.setEnabled( False )

        cancelButton = QPushButton( '&Cancel' )

        submitLayout = QHBoxLayout()
        submitLayout.setContentsMargins( 0, 0, 0, 0 )
        submitLayout.addStretch( 1 )
        submitLayout.addWidget( okButton )
        submitLayout.addWidget( cancelButton )

        submitWidget = QWidget()
        submitWidget.setLayout( submitLayout )

        dialogLayout = QVBoxLayout()
        dialogLayout.addWidget( detailsWidget )
        dialogLayout.addWidget( submitWidget )

        self.setLayout( dialogLayout )
        self.setWindowTitle( 'Global installation into SIT' )
        self.installEventFilter( self )

        toggleOK  = lambda: okButton.setEnabled( len( self._reasonField.text() ) > 4 )

        self._reasonField.textChanged.connect( toggleOK )

        cancelButton.pressed.connect( self.close )
        cancelButton.pressed.connect( self.cancelled.emit )

        okButton.pressed.connect( self._onOkButtonPressed )
        okButton.pressed.connect( self.close )


    def eventFilter( self, obj, event ):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.cancelled.emit()

        return False


    def _onOkButtonPressed( self ):
        # changeType: convert radio button IDs to fixed string
        changeId   =  self._radioGroup.checkedId()
        changeText = { 1: 'NEW', 2: 'FIX', 3: 'DOC', 4: 'IMP' }
        changeType = changeText[ changeId ]

        # reason: take the value entered
        reason     = self._reasonField.text()

        self.ready.emit( changeType, reason )


# EOF
