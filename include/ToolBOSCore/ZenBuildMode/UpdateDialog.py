#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Dialog listing available software updates
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

from PyQt5.QtWidgets import *

from ToolBOSCore.CIA.PatchSystem import PatchSystem
from ToolBOSCore.GenericGUI      import IconProvider


class UpdateDialog( QWidget, object ):

    def __init__( self, parent=None ):
        super( UpdateDialog, self ).__init__( parent )

        self._patcher = PatchSystem()
        neededPatches = self._patcher.run( dryRun=True )

        self._listLayout = QVBoxLayout()

        for patch in neededPatches:

            descr     = patch[0]
            self._listLayout.addWidget( QLabel( '* ' + descr ) )

        self._listWidget = QGroupBox( 'Patches available:' )
        self._listWidget.setLayout( self._listLayout )

        self._applyAllButton = QPushButton( '&Apply all' )
        self._applyAllButton.pressed.connect( self._applyAllUpdate )

        self._closeButton    = QPushButton( '&Close' )
        self._closeButton.pressed.connect( self.close )

        self._submitLayout = QHBoxLayout()
        self._submitLayout.setContentsMargins( 0, 0, 0, 0 )
        self._submitLayout.addStretch( 1 )
        self._submitLayout.addWidget( self._applyAllButton )
        self._submitLayout.addWidget( self._closeButton )

        self._submitWidget = QWidget()
        self._submitWidget.setLayout( self._submitLayout )

        self._dialogLayout = QVBoxLayout()
        self._dialogLayout.addWidget( self._listWidget )
        self._dialogLayout.addWidget( self._submitWidget )

        self.setLayout( self._dialogLayout )
        self.setWindowIcon( IconProvider.getIcon( 'software-update-available' ) )
        self.setWindowTitle( 'Package Updates' )
        self.setFixedSize( self.sizeHint() )

        if not neededPatches:
            self._listLayout.addWidget( QLabel( "No need to apply the patches. Already Updated." ))
            self._applyAllButton.setEnabled( False )
            self._applyAllButton.setText( 'Apply' )


    def _applyAllUpdate( self ):

        self._patcher.run()
        logging.info( "Applying all patches" )
        self._applyAllButton.setEnabled( False )
        self._applyAllButton.setText( 'Patch Applied' )


# EOF
