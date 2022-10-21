#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  List of (reverse) package dependencies
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
import os

from PyQt5.QtCore    import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *

from ToolBOSCore.ZenBuildMode                 import QtPackageModel
from ToolBOSCore.Packages                     import BSTPackage, ProjectProperties
from ToolBOSCore.Packages.DebianPackage       import DebianPackage
from ToolBOSCore.Packages.PackageFactory      import PackageFactory
from ToolBOSCore.Storage                      import ProxyDir, SIT
from ToolBOSCore.Util                         import Any


class DependenciesDialog( QWidget, object ):

    def __init__( self, model ):
        super( DependenciesDialog, self ).__init__()

        Any.requireIsInstance( model, QtPackageModel.BSTPackageModel )

        numColumns          = 4

        self._model         = model
        self._treeMode      = True
        self._reverseMode   = False
        self._tree          = None
        self._treeWidget    = QTreeWidget()
        self._red           = QColor( 255, 120, 120 )
        self._green         = QColor( 220, 255, 220 )
        self._grey          = QColor( 240, 240, 240 )
        self._canonicalPath = self._model.getCanonicalPath()
        self._sitProxyPath  = SIT.getPath()
        self._sitRootPath   = SIT.getRootPath()
        self._hasProxy      = ProxyDir.isProxyDir( self._sitProxyPath )

        # obtain data and create one QTreeWidgetItem for each
        self._data1 = self._model.getDependencySet()
        self._data2 = self._model.getDependencyTree()
        self._data3 = self._model.getReverseDependencySet()
        self._data4 = self._model.getReverseDependencyTree()

        self._aptCmd = self._model.getDepInstallCmd_APT()

        logging.debug( 'data1: %s', self._data1 )
        logging.debug( 'data2: %s', self._data2 )
        logging.debug( 'data3: %s', self._data3 )
        logging.debug( 'data4: %s', self._data4 )

        depsEnabled    = self._data1 is not None and self._data2 is not None
        revDepsEnabled = self._data3 is not None and self._data4 is not None

        if depsEnabled:
            self._tree1 = self._createTreeWidgetFromSet(  self._data1, False )
            self._tree2 = self._createTreeWidgetFromList( self._data2, False )

        if revDepsEnabled:
            self._tree3 = self._createTreeWidgetFromSet(  self._data3, True  )
            self._tree4 = self._createTreeWidgetFromList( self._data4, True  )

        if not depsEnabled and not revDepsEnabled:
            logging.error( 'unable to show dependency-dialog' )
            return

        depsTooltip    = 'low-level packages needed by the current one'

        if revDepsEnabled:
            revDepsTooltip = 'high-level packages which use the current one'
        else:
            revDepsTooltip = 'not globally installed --> no reverse dependencies'

        self._depRadio_direct = QRadioButton( '&dependencies' )
        self._depRadio_direct.setChecked( True )
        self._depRadio_direct.setToolTip( depsTooltip )
        self._depRadio_direct.clicked.connect(self._showDependencies)

        self._depRadio_reverse = QRadioButton( '&reverse dependencies' )
        self._depRadio_reverse.setToolTip( revDepsTooltip )
        self._depRadio_reverse.setEnabled( revDepsEnabled )
        self._depRadio_reverse.clicked.connect( self._showReverseDependencies )

        depSelectLayout  = QVBoxLayout()
        depSelectLayout.addWidget( self._depRadio_direct )
        depSelectLayout.addWidget( self._depRadio_reverse )

        depSelectWidget  = QGroupBox( 'direction' )
        depSelectWidget.setLayout( depSelectLayout )


        # initial / default view: show own dependencies as tree
        self._tree = self._tree2
        self._updateView()

        self._treeWidget.setColumnCount( numColumns )
        self._treeWidget.setRootIsDecorated( False )   # top-left has no parent line
        self._treeWidget.setSortingEnabled( False )

        header = self._treeWidget.header()
        header.setStretchLastSection( False )
        header.setSectionResizeMode( 0, QHeaderView.Stretch ) # stretch first column

        headerWidget = QTreeWidgetItem( [ 'dependency',
                                          'installed in proxy SIT',
                                          'installed in global SIT',
                                          'installed locally' ] )

        for i in range( 1, numColumns ):
            header.setSectionResizeMode( i, QHeaderView.ResizeToContents )
            headerWidget.setTextAlignment( i, Qt.AlignCenter )


        self._treeWidget.setHeaderItem( headerWidget )


        self._aptLabel = QLabel( 'Debian/Ubuntu packages needed:' )

        self._aptWidget = QTextEdit( self._aptCmd )
        self._aptWidget.setFixedHeight( 100 )
        self._aptWidget.setFontFamily( "Courier New" )
        self._aptWidget.setReadOnly( True )


        toggleView   = QPushButton( '&toggle tree/flat view' )
        toggleView.pressed.connect( self._toggleTree )

        self._expandButton = QPushButton( '&expand all' )
        self._expandButton.pressed.connect( self._treeWidget.expandAll )

        self._collapseButton = QPushButton( '&collapse all' )
        self._collapseButton.pressed.connect( self._treeWidget.collapseAll )
        self._collapseButton.pressed.connect( lambda: self._tree.setExpanded( True ) )

        closeButton  = QPushButton( '&OK' )
        closeButton.pressed.connect( self.close )

        buttonLayout = QHBoxLayout()
        buttonLayout.setAlignment( Qt.AlignRight )
        buttonLayout.addWidget( toggleView )
        buttonLayout.addSpacing( 1 )
        buttonLayout.addWidget( self._expandButton )
        buttonLayout.addWidget( self._collapseButton )
        buttonLayout.addWidget( closeButton )

        buttonWidget = QWidget()
        buttonWidget.setLayout( buttonLayout )

        mainLayout   = QVBoxLayout()
        mainLayout.addWidget( depSelectWidget )
        mainLayout.addWidget( self._treeWidget )
        mainLayout.addWidget( self._aptLabel )
        mainLayout.addWidget( self._aptWidget )
        mainLayout.addWidget( buttonWidget )

        # noinspection PyArgumentList
        screen       = QApplication.desktop().screenGeometry()

        dialogWidth  = screen.width()  * 0.5
        dialogHeight = screen.height() * 0.75

        self.setLayout( mainLayout )
        self.setWindowTitle( 'Dependencies of %s' % self._canonicalPath )
        self.resize( dialogWidth, dialogHeight )
        self.move( screen.center() - self.rect().center() )  # center
        self.show()


    def _showDependencies( self ):
        self._reverseMode = False
        self._tree = self._tree2 if self._treeMode else self._tree1
        self._updateView()




    def _showReverseDependencies( self ):
        self._reverseMode = True
        self._tree = self._tree4 if self._treeMode else self._tree3
        self._updateView()


    def _showList( self ):
        self._treeMode = False
        self._tree = self._tree3 if self._reverseMode else self._tree1
        self._updateView()

        self._collapseButton.setEnabled( False )
        self._expandButton.setEnabled( False )


    def _showTree( self ):
        self._treeMode = True
        self._tree = self._tree4 if self._reverseMode else self._tree2
        self._updateView()

        self._collapseButton.setEnabled( True )
        self._expandButton.setEnabled( True )


    def _toggleTree( self ):
        self._treeMode = not self._treeMode

        if self._reverseMode:
            self._showReverseDependencies()
        else:
            self._showDependencies()


    def _updateView( self ):
        self._treeWidget.takeTopLevelItem( 0 )
        self._treeWidget.insertTopLevelItem( 0, self._tree )
        self._tree.setExpanded( True )         # expand top-level at startup


    def _createTreeWidgetFromList( self, package, reverseMode ):
        Any.requireMsg( Any.isInstance( package, BSTPackage.BSTPackage ) or \
                        Any.isInstance( package, DebianPackage ),
                        'unexpected datatype: %s' % type(package) )
        Any.requireIsBool( reverseMode )

        Any.requireIsTextNonEmpty( package.url )
        result = self._createCellWidget( package )

        treeData = package.revDepTree if reverseMode else package.depTree

        if treeData:
            Any.requireIsList( treeData )

            for dep in treeData:
                child = self._createTreeWidgetFromList( dep, reverseMode )
                result.addChild( child )

        return result


    def _createTreeWidgetFromSet( self, package, reverseMode ):
        Any.requireMsg( Any.isInstance( package, BSTPackage.BSTPackage ) or \
                        Any.isInstance( package, DebianPackage ),
                        'unexpected datatype: %s' % type(package) )
        Any.requireIsBool( reverseMode )

        treeData = list(package.revDepSet) if reverseMode else list(package.depSet)
        Any.requireIsList( treeData )

        treeData.sort()

        Any.requireIsTextNonEmpty( package.url )
        result = self._createCellWidget( package )

        factory = PackageFactory()

        for packageURL in treeData:
            dep   = factory.create( packageURL )
            child = self._createCellWidget( dep )
            result.addChild( child )

        return result


    def _createCellWidget( self, package ):
        Any.requireMsg( Any.isInstance( package, BSTPackage.BSTPackage ) or \
                        Any.isInstance( package, DebianPackage ),
                        'unexpected datatype: %s' % type(package) )

        Any.requireIsTextNonEmpty( package.url )

        cell     = QTreeWidgetItem( [ package.url ] )
        inSystem = self._model.isInstalled_locally
        inProxy  = self._model.isInstalled_proxySIT
        inGlobal = self._model.isInstalled_globalSIT

        ProjectProperties.requireIsURL( package.url )

        if package.url.startswith( 'sit://' ):
            ProjectProperties.requireIsCanonicalPath( SIT.strip( package.url ) )

            if self._hasProxy:
                self._setCellColorCode( cell, 1, inProxy(  package.url ) )
            else:
                self._setCellColorCode( cell, 1, None )

            self._setCellColorCode( cell, 2, inGlobal( package.url ) )
            self._setCellColorCode( cell, 3, None  )
        else:
            self._setCellColorCode( cell, 1, None )
            self._setCellColorCode( cell, 2, None )
            self._setCellColorCode( cell, 3, inSystem( package.url ) )

        return cell


    def _setCellColorCode( self, child, column, status ):
        Any.requireIsInstance( child, QTreeWidgetItem )
        Any.requireIsInt( column )

        if status is None:
            color = self._grey
            text  = ''

        elif status is True:
            color = self._green
            text  = 'yes'

        elif status is False:
            color = self._red
            text  = 'no'

        else:
            raise ValueError( 'unexpected status: %s', status )

        child.setBackground( column, color )
        child.setText( column, text )
        child.setTextAlignment( column, Qt.AlignCenter )


# EOF
