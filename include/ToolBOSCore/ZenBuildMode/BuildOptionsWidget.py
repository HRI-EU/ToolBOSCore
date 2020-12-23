#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Build options such as verbosity or parallelization
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


from PyQt5.QtCore    import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *

from ToolBOSCore.Util import Any, FastScript


class BuildOptionsWidget( QGroupBox, object ):

    def __init__( self, parent=None ):
        super( QGroupBox, self ).__init__( 'options', parent )

        self._verboseOption   = QCheckBox( '&verbose' )
        self._verboseOption.setChecked( Any.getDebugLevel() > 3 )
        self._verboseOption.setToolTip( 'show debug messages?' )

        self._parallelOption  = QCheckBox( 'parallel jobs:' )
        self._parallelValue   = QLineEdit()
        self._parallelWidget  = QWidget()
        self._parallelLayout  = QHBoxLayout()

        jobs = FastScript.getEnv( 'BST_BUILD_JOBS' )

        if jobs:
            if jobs == '1':
                self._parallelOption.setChecked( False )
                self._parallelValue.setEnabled( False )
                self._parallelValue.setText( '32' ) # 1 would be a bad default
            else:
                self._parallelOption.setChecked( True )
                self._parallelValue.setEnabled( True )
                self._parallelValue.setText( jobs )
        else:
            self._parallelOption.setChecked( False )
            self._parallelValue.setEnabled( False )
            self._parallelValue.setText( '32' )     # default parallelization

        self._parallelOption.setToolTip( 'parallel build ("-j" option)' )
        # noinspection PyUnresolvedReferences
        self._parallelOption.stateChanged.connect( self._onParallelOption )
        self._parallelValue.setValidator( QIntValidator( 1, 99, self._parallelWidget ) )
        self._parallelValue.setMaxLength( 2 )
        self._parallelValue.setMaximumWidth( 30 )
        self._parallelValue.setToolTip( 'number of parallel build jobs' )
        self._parallelValue.resize( 0, 0 )

        self._parallelLayout.setAlignment( Qt.AlignLeft )
        self._parallelLayout.addWidget( self._parallelOption )
        self._parallelLayout.addWidget( self._parallelValue )
        self._parallelLayout.addStretch( 1 )
        self._parallelLayout.setContentsMargins( 0, 0, 0, 0 )   # no add. margin
        self._parallelWidget.setLayout( self._parallelLayout )

        layout = QVBoxLayout()
        layout.addWidget( self._verboseOption )
        layout.addWidget( self._parallelWidget )

        self.setLayout( layout )


    def getParallelValue( self ):
        if self._parallelOption.isChecked():
            return int( self._parallelValue.text() )
        else:
            return 1


    def getVerboseValue( self ):
        return self._verboseOption.isChecked()


    def setEnabled( self, state ):
        self._verboseOption.setEnabled( state )
        self._parallelOption.setEnabled( state )
        self._parallelValue.setEnabled( self._parallelOption.isChecked() and state )


    def _onParallelOption( self, state ):
        self._parallelValue.setEnabled( bool(state) )


# EOF
