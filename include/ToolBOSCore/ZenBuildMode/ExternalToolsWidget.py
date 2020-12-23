#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Launchers for external tools (IDEs etc.)
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

from PyQt5.QtCore    import QSize, Qt
from PyQt5.QtWidgets import *

from ToolBOSCore.ZenBuildMode import QtPackageModel,\
                                     SettingsDialog, UpdateDialog
from ToolBOSCore.SoftwareQuality import CheckRoutineDialog
from ToolBOSCore.GenericGUI   import BusyWaitDialog, \
                                     IconProvider, PixmapProvider, \
                                     ProcessExecutor
from ToolBOSCore.Util         import Any


class ExternalToolsWidget( QWidget, object ):

    def __init__( self, model, parent=None ):
        super( QWidget, self ).__init__()

        Any.requireIsInstance( model, QtPackageModel.BSTPackageModel )

        self.parent          = parent
        self.model           = model

        self._pkgCreator     = None
        self._settingsDialog = None
        self._sqDialog       = None

        self._busyDialog     = None

        iconSize             = QSize( 32, 32 )

        self.updateButton = QToolButton()
        self.updateButton.setEnabled( False )
        self.updateButton.setIcon( IconProvider.getIcon( 'software-update-available' ) )
        self.updateButton.setIconSize( iconSize )
        self.updateButton.setToolTip( 'No patches available, package is up-to-date' )
        self.updateButton.clicked.connect( self._onUpdateButtonPressed )

        settingsButton = QToolButton()
        settingsButton.setIconSize( iconSize )
        settingsButton.setToolTip( 'set preferences' )
        settingsButton.setIcon( IconProvider.getIcon( 'preferences-system' ) )
        settingsButton.clicked.connect( self._onSettingsButtonPressed )

        logo = QLabel()
        logo.setPixmap( PixmapProvider.getPixmap( 'ToolBOS-Logo-small' ) )
        logo.setAlignment( Qt.AlignCenter )

        icemonButton = QToolButton()
        icemonButton.setIconSize( iconSize )
        icemonButton.setToolTip( 'compile farm status (Icecream Monitor)' )
        icemonButton.setIcon( IconProvider.getIcon( 'IcecreamMonitor' ) )
        icemonButton.clicked.connect( self._onIceMonButtonPressed )

        sqButton = QToolButton()
        sqButton.setIconSize( iconSize )
        sqButton.setToolTip( 'Software Quality' )
        sqButton.setIcon( IconProvider.getIcon( 'QualityGuideline' ) )
        sqButton.clicked.connect( self._onSoftwareQualityDialogPressed )

        iconGrid = QGridLayout()
        iconGrid.setContentsMargins( 0, 0, 0, 0 )
        iconGrid.addWidget( icemonButton,      0, 0 )
        iconGrid.addWidget( sqButton,          0, 1 )
        iconGrid.addWidget( self.updateButton, 1, 0 )
        iconGrid.addWidget( settingsButton,    1, 1 )

        iconWidget = QGroupBox( 'utilities', self )
        iconWidget.setLayout( iconGrid )

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins( 0, 0, 0, 0 )
        mainLayout.addStretch( 1 )
        mainLayout.addWidget( logo )
        mainLayout.addStretch( 1 )
        mainLayout.addWidget( iconWidget )

        self.setLayout( mainLayout )


    def showUpdateIndicator( self ):
        self.updateButton.setToolTip( 'There are patches available for this package' )
        self.updateButton.setEnabled( True )


    def _onPkgCreatorButtonPressed( self ):
        logging.info( 'starting Package Creator' )

        from ToolBOSCore.Packages.PackageCreatorGUI import PackageCreatorGUI

        self._pkgCreator = PackageCreatorGUI()
        self._pkgCreator.runGUI( self.parent )


    def _onCLionButtonPressed( self ):
        from ToolBOSCore.Tools import CLion

        CLion.createProject()
        CLion.startGUI()


    def _onIceMonButtonPressed( self ):
        self._runProcess( 'icemon -n HRI1004', 'Icrecream Monitor' )


    def _onSoftwareQualityDialogPressed( self ):
        if self.model.isQualityCheckPreparationFinished():
            if self._busyDialog is not None:
                self._busyDialog.close()
                self._busyDialog = None

            self._sqDialog = CheckRoutineDialog.CheckRoutineDialog( self.model, self.parent )
            self._sqDialog.show()
        else:
            self.model.sqCheckPrepared.connect( self._onSoftwareQualityDialogPressed )

            self._busyDialog = BusyWaitDialog.BusyWaitDialog( 'analyzing package... (this may take some time)' )


    def _onUpdateButtonPressed(self):
        self._updateDialog = UpdateDialog.UpdateDialog()
        self._updateDialog.show()


    def _onSettingsButtonPressed( self ):
        self._settings = SettingsDialog.SettingsDialog( self.parent )


    def _runProcess( self, cmd, description ):
        Any.requireIsTextNonEmpty( cmd )
        Any.requireIsTextNonEmpty( description )

        logging.info( 'launching %s', description )

        process = ProcessExecutor.ProcessExecutor()
        process.setCommand( cmd )
        process.setDetached( True )
        process.start()


# EOF
