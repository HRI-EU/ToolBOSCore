#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Menu bar
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

from ToolBOSCore.ZenBuildMode import SettingsDialog
from ToolBOSCore.GenericGUI   import AboutDialog, WebBrowser


class MenuBar( QMenuBar, object ):

    build         = pyqtSignal()
    clean         = pyqtSignal()
    globalInstall = pyqtSignal()
    proxyInstall  = pyqtSignal()
    test          = pyqtSignal()

    openPackage   = pyqtSignal( str )
    quit          = pyqtSignal()


    def __init__( self, parent=None ):
        super( QMenuBar, self ).__init__( parent )

        self.parent          = parent

        self._aboutDialog    = None
        self._webBrowser     = None
        self._settingsDialog = None
        self._sqDialog       = None


        # "File" section

        fileOpenAction = QAction( '&Open package', parent )
        fileOpenAction.setShortcut( 'Ctrl+O' )
        fileOpenAction.triggered.connect( self.fileOpen )

        fileQuitAction = QAction( '&Quit', parent )
        fileQuitAction.setShortcut( 'Ctrl+Q' )
        fileQuitAction.triggered.connect( self.quit.emit )

        self.fileMenu = QMenu( '&File', parent )
        self.fileMenu.addAction( fileOpenAction )
        self.fileMenu.addAction( fileQuitAction )


        # "Edit" section

        self.editMenu = QMenu( '&Edit', parent )
        self.editMenu.addAction( 'Prefere&nces', self.editPreferences )


        # "Help" section

        self.helpMenu = QMenu( "&Help", parent )
        self.helpMenu.addAction( "&About", self.helpAbout )

        self.helpDocuAction = QAction( '&Online documentation', parent )
        self.helpDocuAction.setShortcut( 'F1' )
        self.helpDocuAction.triggered.connect( self.helpOnlineDocumentation )

        self.helpMenu.addAction( self.helpDocuAction )


        # "Run" section

        runDistcleanAction = QAction( '&Distclean', parent )
        runDistcleanAction.triggered.connect( self.clean.emit )

        runBuildAction = QAction( '&Build', parent )
        runBuildAction.triggered.connect( self.build.emit )

        runProxyInstallAction = QAction( 'Pro&xy installation', parent )
        runProxyInstallAction.triggered.connect( self.proxyInstall.emit )

        runGlobalInstallAction = QAction( 'Global &installation', parent )
        runGlobalInstallAction.triggered.connect( self.globalInstall.emit )

        runUnittestAction = QAction( '&Testsuite', parent )
        runUnittestAction.triggered.connect( self.test.emit )

        self.runMenu = QMenu( '&Run', parent )
        self.runMenu.addAction( runDistcleanAction )
        self.runMenu.addAction( runBuildAction )
        self.runMenu.addAction( runProxyInstallAction )
        self.runMenu.addAction( runGlobalInstallAction )
        self.runMenu.addAction( runUnittestAction )


        self.addMenu( self.fileMenu )
        self.addMenu( self.editMenu )
        self.addMenu( self.runMenu )
        self.addMenu( self.helpMenu )


    def editPreferences( self ):
        self._settingsDialog = SettingsDialog.SettingsDialog( self.parent )


    def fileOpen( self ):
        desc     = 'Open package (top-level directory)'
        path     = os.getcwd()
        selected = QFileDialog.getExistingDirectory( self.parent, desc, path )

        if selected:
            self.openPackage.emit( selected )


    def helpAbout( self ):
        self._aboutDialog = AboutDialog.AboutDialog( self.parent )
        self._aboutDialog.show()


    def helpOnlineDocumentation( self ):
        WebBrowser.openToolBOSDocumentation( 'ToolBOS_Util_BuildSystemTools_ZenBuildMode',
                                             self )


# EOF
