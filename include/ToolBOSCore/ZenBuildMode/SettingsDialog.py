#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Settings dialog
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

from PyQt5.QtCore    import QRegExp, Qt
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from ToolBOSCore.Platforms import CrossCompilation
from ToolBOSCore.Platforms import Platforms
from ToolBOSCore.Settings  import ToolBOSConf
from ToolBOSCore.Util      import Any


class SettingsDialog( QWidget, object ):

    def __init__( self, parent ):
        super( QWidget, self ).__init__()

        hostPlatform    = Platforms.getHostPlatform()
        nativePlatforms = Platforms.getPlatformNames()
        xcmpPlatforms   = CrossCompilation.getSwitchEnvironmentList( hostPlatform )
        defaultNative   = CrossCompilation.getNativeCompilationList()
        defaultXcmp     = CrossCompilation.getCrossCompilationList()

        self._platformCBs_nat     = {}
        self._platformCBs_xcmp    = {}
        self._hostnameFields_nat  = {}
        self._hostnameFields_xcmp = {}
        self._settingsDialog      = None
        self._toolBOSConf         = ToolBOSConf.getGlobalToolBOSConf()

        # rows corresponds to number of total platforms (native +
        # cross-compilation), plus 2 lines for the bold headlines
        rows = len(nativePlatforms) + len(xcmpPlatforms) + 2

        table = QTableWidget()
        table.setRowCount( rows )
        table.setColumnCount( 3 )
        table.setHorizontalHeaderLabels( ( 'platform name',
                                           'enabled at start-up',
                                           'hostname' ) )

        hHeader = table.horizontalHeader()
        hHeader.setSectionResizeMode( QHeaderView.Stretch )
        hHeader.setSectionsClickable( False )

        vHeader = table.verticalHeader()
        vHeader.setSectionResizeMode( QHeaderView.Stretch )
        vHeader.setSectionsClickable( False )
        vHeader.hide()

        boldFont    = QFont( "Helvetica", 14, QFont.Bold )

        nativeLabel = QTableWidgetItem( 'native compilation:' )
        nativeLabel.setFont( boldFont )
        nativeLabel.setFlags( Qt.ItemIsEnabled )

        table.setSpan( 0, 0, 1, 3 )
        table.setItem( 0, 0, nativeLabel )

        validator = QRegExpValidator( QRegExp( "[a-z]{1,16}[a-z0-9\-]*" ) )

        i = 1
        for platform in nativePlatforms:
            # column 1: platform name
            platformLabel = QTableWidgetItem( platform )
            platformLabel.setFlags( Qt.ItemIsEnabled )
            table.setItem( i, 0, platformLabel )


            # column 2: enabled at start-up?
            cellLayout = QHBoxLayout()
            cellWidget = QWidget()
            checkbox   = QCheckBox()
            checkbox.setChecked( platform in defaultNative )

            self._platformCBs_nat[ platform ] = checkbox

            cellLayout.setAlignment( Qt.AlignCenter )
            cellLayout.addWidget( checkbox )
            cellLayout.setContentsMargins( 0, 0, 0, 0 )
            cellWidget.setLayout( cellLayout )

            table.setCellWidget( i, 1, cellWidget )


            # column 3: hostname
            hostname      = CrossCompilation.getNativeCompileHost( platform )
            hostnameField = QLineEdit( hostname )
            hostnameField.setMaxLength( 64 )
            hostnameField.setValidator( validator )
            table.setCellWidget( i, 2, hostnameField )

            self._hostnameFields_nat[ platform ] = hostnameField

            i += 1


        xcmpLabel = QTableWidgetItem( 'cross-compilation:' )
        xcmpLabel.setFont( boldFont )
        xcmpLabel.setFlags( Qt.ItemIsEnabled )

        table.setSpan( i, 0, 1, 3 )
        table.setItem( i, 0, xcmpLabel )

        # i = 1                         # append, thus do not reset to 1
        i += 1                          # instead mind add. row for xcmpLabel

        for platform in xcmpPlatforms:
            # column 1: platform name
            platformLabel = QTableWidgetItem( platform )
            platformLabel.setFlags( Qt.ItemIsEnabled )
            table.setItem( i, 0, platformLabel )


            # column 2: enabled at start-up?
            cellLayout = QHBoxLayout()
            cellWidget = QWidget()
            checkbox   = QCheckBox()
            checkbox.setChecked( platform in defaultXcmp )
            self._platformCBs_xcmp[ platform ] = checkbox

            cellLayout.setAlignment( Qt.AlignCenter )
            cellLayout.addWidget( checkbox )
            cellLayout.setContentsMargins( 0, 0, 0, 0 )
            cellWidget.setLayout( cellLayout )

            table.setCellWidget( i, 1, cellWidget )


            # column 3: hostname
            hostname      = CrossCompilation.getCrossCompileHost( platform )
            hostnameField = QLineEdit( hostname )
            hostnameField.setMaxLength( 64 )
            hostnameField.setValidator( validator )
            table.setCellWidget( i, 2, hostnameField )

            self._hostnameFields_xcmp[ platform ] = hostnameField

            i += 1


        table.resizeRowsToContents()
        table.resizeColumnsToContents()

        self._tableLayout = QVBoxLayout()
        self._tableLayout.addWidget( table )

        self._tableWidget = QGroupBox( 'Compile hosts' )
        self._tableWidget.setLayout( self._tableLayout )

        self._restoreButton = QPushButton( '&Restore defaults' )
        self._okButton      = QPushButton( '&Save' )

        self._cancelButton  = QPushButton( '&Cancel' )

        self._submitLayout = QHBoxLayout()
        self._submitLayout.setContentsMargins( 0, 0, 0, 0 )
        self._submitLayout.addStretch( 1 )
        self._submitLayout.addWidget( self._restoreButton )
        self._submitLayout.addWidget( self._okButton )
        self._submitLayout.addWidget( self._cancelButton )

        self._submitWidget = QWidget()
        self._submitWidget.setLayout( self._submitLayout )

        self._dialogLayout = QVBoxLayout()
        self._dialogLayout.addWidget( self._tableWidget )
        self._dialogLayout.addWidget( self._submitWidget )

        dialogWidth  = table.width() * 1.75 # screen.width() / 5 * 3
        dialogHeight = table.height() * 1.5 #screen.height() / 5 * 3

        self._settingsDialog = QDialog( parent )
        self._settingsDialog.setLayout( self._dialogLayout )
        self._settingsDialog.setWindowTitle( 'Preferences' )
        self._settingsDialog.resize( dialogWidth, dialogHeight )
        self._settingsDialog.setModal( True )
        self._settingsDialog.show()

        self._restoreButton.pressed.connect( self._restoreDefaults )
        self._restoreButton.pressed.connect( self._settingsDialog.close )
        self._cancelButton.pressed.connect( self._settingsDialog.close )
        self._okButton.pressed.connect( self._saveSettings )
        self._okButton.pressed.connect( self._settingsDialog.close )


    def _restoreDefaults( self ):
        logging.info( 'restoring default settings' )

        # remove existing settings (if any)

        self._toolBOSConf.delUserConfigOption( 'BST_defaultPlatforms_native' )

        self._toolBOSConf.delUserConfigOption('BST_defaultPlatforms_xcmp')

        self._toolBOSConf.delUserConfigOption( 'hostname' )


    def _saveSettings( self ):
        defaultHostnames_nat  = ToolBOSConf.getConfigOption( 'BST_compileHosts' )
        defaultHostnames_xcmp = ToolBOSConf.getConfigOption( 'BST_crossCompileHosts' )
        userCompileHosts      = {}
        userCrossCompileHosts = {}

        enabledPlatforms_nat  = []
        enabledPlatforms_xcmp = []


        logging.debug( 'checkbox status:' )

        for platform, checkbox in self._platformCBs_nat.items():
            checked = checkbox.isChecked()
            logging.debug( '%s (native): %s', platform, checked )

            if checked:
                enabledPlatforms_nat.append( platform )


            hostnameField   = self._hostnameFields_nat[ platform ]
            Any.requireIsInstance( hostnameField, QLineEdit )

            enteredHostname = str( hostnameField.text() )
            Any.requireIsText( enteredHostname )                           # might be empty


            try:
                defaultHostname = defaultHostnames_nat[ platform ]
            except KeyError:
                defaultHostname = None


            if defaultHostname is None:
                defaultHostname = ''


            if enteredHostname != '' and enteredHostname != defaultHostname:
                logging.info( 'user-modified hostname: %s=%s', platform, enteredHostname )
                userCompileHosts[ platform ] = enteredHostname



        for platform, checkbox in self._platformCBs_xcmp.items():
            checked = checkbox.isChecked()
            logging.debug( '%s (cross):  %s', platform, checked )

            if checked:
                enabledPlatforms_xcmp.append( platform )

            hostnameField   = self._hostnameFields_xcmp[ platform ]
            Any.requireIsInstance( hostnameField, QLineEdit )

            enteredHostname = str( hostnameField.text() )
            Any.requireIsText( enteredHostname )                           # might be empty


            try:
                defaultHostname = defaultHostnames_xcmp[ platform ]
            except KeyError:
                defaultHostname = None


            if defaultHostname is None:
                defaultHostname = ''


            if enteredHostname != '' and enteredHostname != defaultHostname:
                logging.info( 'user-modified hostname: %s=%s', platform, enteredHostname )
                userCrossCompileHosts[ platform ] = enteredHostname


        enabledPlatforms_nat.sort()
        enabledPlatforms_xcmp.sort()


        self._toolBOSConf.setUserConfigOption( 'BST_defaultPlatforms_native',
                                                enabledPlatforms_nat )

        self._toolBOSConf.setUserConfigOption( 'BST_defaultPlatforms_xcmp',
                                                enabledPlatforms_xcmp )

        self._toolBOSConf.setUserConfigOption( 'BST_userCompileHosts',
                                                userCompileHosts )

        self._toolBOSConf.setUserConfigOption( 'BST_userCrossCompileHosts',
                                                userCrossCompileHosts )

        self._toolBOSConf.save()


# EOF
