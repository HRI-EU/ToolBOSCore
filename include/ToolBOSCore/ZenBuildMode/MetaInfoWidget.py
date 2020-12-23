#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Shows package meta-info such as name, revision,...
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


from PyQt5.QtWidgets import *

from ToolBOSCore.ZenBuildMode import DependenciesDialog, QtPackageModel
from ToolBOSCore.GenericGUI   import BusyWaitDialog
from ToolBOSCore.Util         import Any


class MetaInfoWidget( QGroupBox, object ):

    def __init__( self, model, parent=None ):
        super( QGroupBox, self ).__init__( 'package meta-info' )

        Any.requireIsInstance( model, QtPackageModel.BSTPackageModel )

        self._model         = model

        self._busyDialog    = None

        self._listDepDialog = None

        self._labelName     = QLabel( '<b>name:</b>',         parent )
        self._name          = QLabel( 'n/a',                  parent )
        self._labelVersion  = QLabel( '<b>version:</b>',      parent )
        self._version       = QLabel( 'n/a',                  parent )
        self._labelCategory = QLabel( '<b>category:</b>',     parent )
        self._category      = QLabel( 'n/a',                  parent )
        self._labelRevision = QLabel( '<b>revision:</b>',     parent )
        self._revision      = QLabel( 'n/a',                  parent )
        self._labelDeps     = QLabel('<b>dependencies:</b>',  parent )
        self._listDepButton = QPushButton( '&show' )

        buttonFont          = self._listDepButton.font()
        buttonFont.setPointSize( 8 )

        msg = 'retrieving package dependencies... (this may take some time)'
        self._listDepButton.setFont( buttonFont )
        self._listDepButton.setEnabled( False )
        self._listDepButton.setToolTip( msg )

        self._layout = QGridLayout()
        self._layout.addWidget( self._labelName,         0, 0 )
        self._layout.addWidget( self._name,              0, 1 )
        self._layout.addWidget( self._labelVersion,      1, 0 )
        self._layout.addWidget( self._version,           1, 1 )
        self._layout.addWidget( self._labelCategory,     2, 0 )
        self._layout.addWidget( self._category,          2, 1 )
        self._layout.addWidget( self._labelRevision,     3, 0 )
        self._layout.addWidget( self._revision,          3, 1 )
        self._layout.addWidget( self._labelDeps,         4, 0 )
        self._layout.addWidget( self._listDepButton,     4, 1 )
        self.setLayout( self._layout )

        model.newName.connect( self.setName )
        model.newVersion.connect( self.setVersion )
        model.newCategory.connect( self.setCategory )
        model.newRevision.connect( self.setRevision )
        model.depsDetected.connect( self._enableListDepButton )

        self._listDepButton.clicked.connect( self._onListDepButtonPressed )


    def _enableListDepButton( self, val ):
        self._listDepButton.setEnabled( val )
        if val:
            self._listDepButton.setToolTip( '' )
        else:
            self._listDepButton.setToolTip( 'unable to retrieve dependencies' )


    def _onListDepButtonPressed( self ):
        self._listDepDialog = DependenciesDialog.DependenciesDialog( self._model )
        self._listDepDialog.show()


    def setName( self, name ):
        self._name.setText( name )


    def setVersion( self, version ):
        self._version.setText( version )


    def setCategory( self, category ):
        self._category.setText( category )


    def setRevision( self, string ):
        self._revision.setText( string )


# EOF
