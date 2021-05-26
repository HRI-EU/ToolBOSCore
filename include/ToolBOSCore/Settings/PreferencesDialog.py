#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Edit/save/restore ToolBOS.conf settings via GUI
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


import functools
import logging

import sip

sip.setapi( 'QString', 2 )
sip.setapi( 'QVariant', 2 )

from PyQt5.QtCore    import QSize
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from ToolBOSCore.GenericGUI           import IconProvider
from ToolBOSCore.Settings.ToolBOSConf import ToolBOSConf
from ToolBOSCore.Util                 import Any


def run():
    app    = QApplication( [] )
    window = PreferencesDialog()

    window.show()

    return app.exec_()


class PreferencesDialog( QDialog, object ):

    _iconSize       = QSize( 16, 16 )

    _styleChanged   = 'font-weight: bold;'
    _styleUnchanged = 'color: grey;'


    def __init__( self, appName=None, parent=None ):
        super( PreferencesDialog, self ).__init__( parent )


        self._conf     = ToolBOSConf()
        self._allData  = self._conf.getConfigOptions()
        self._appName  = appName
        self._userData = self._conf.getUserConfigOptions()
        self._labels   = {}
        self._fields   = {}
        self._revert   = {}
        i              = 0
        table          = QWidget()
        layout         = QGridLayout()

        Any.requireIsDictNonEmpty( self._allData )
        Any.requireIsDict( self._userData )


        for name, value in sorted( self._allData.items() ):

            if appName is not None and not name.startswith( appName ):
                continue


            if appName:
                label = QLabel( name.replace( appName + "_", '' ) )
            else:
                label = QLabel( name )

            field  = QLineEdit( repr(value) )
            revert = QPushButton()


            # by default long lines would be scrolled to see the end
            # of the text, however we want to see the beginning of
            # long settings
            field.setCursorPosition( 0 )


            # highlight user-modified entries
            changed = name in self._userData

            if changed:
                style = self._styleChanged
            else:
                style = self._styleUnchanged

            label.setStyleSheet( style )
            field.setStyleSheet( style )


            field.textChanged.connect( functools.partial( self._onChange, name ) )

            revert.setIcon( IconProvider.getIcon( 'edit-undo' ) )
            revert.setMaximumHeight( field.sizeHint().height() )
            revert.pressed.connect( functools.partial( self._onRevert, name ) )
            revert.setToolTip( 'revert to default' )
            revert.setEnabled( changed )

            layout.addWidget( label,  i, 0 )
            layout.addWidget( field,  i, 1 )
            layout.addWidget( revert, i, 2 )


            self._labels[ name ] = label
            self._fields[ name ] = field
            self._revert[ name ] = revert

            i += 1

        table.setLayout( layout )

        scrollArea         = QScrollArea()
        scrollArea.setWidget( table )
        scrollArea.setWidgetResizable( True )

        self._saveButton   = QPushButton( '&Save' )
        self._quitButton   = QPushButton( '&Quit' )

        self._submitLayout = QHBoxLayout()
        self._submitLayout.setContentsMargins( 0, 0, 0, 0 )
        self._submitLayout.addStretch( 1 )
        self._submitLayout.addWidget( self._saveButton )
        self._submitLayout.addWidget( self._quitButton )

        self._submitWidget = QWidget()
        self._submitWidget.setLayout( self._submitLayout )

        self._dialogLayout = QVBoxLayout()
        self._dialogLayout.addWidget( scrollArea )
        self._dialogLayout.addWidget( self._submitWidget )

        self.setLayout( self._dialogLayout )
        self.setWindowIcon( IconProvider.getIcon( 'ToolBOS' ) )
        self.setModal( True )

        if appName:
            self.setWindowTitle( '%s Preferences' % appName )
        else:
            self.setWindowTitle( 'ToolBOS SDK Preferences' )


        # hack: no appname means show full list --> resize geometry,
        #       with name we assume to get a small widget only --> auto-geometry
        if appName is None:
            screen       = QApplication.desktop().screenGeometry()
            dialogWidth  = screen.width()  / 5 * 3
            dialogHeight = screen.height() / 5 * 3

            self.resize( dialogWidth, dialogHeight )
            self.move( screen.center() - self.rect().center() )  # center


        self._saveButton.pressed.connect( self._onSave )
        self._quitButton.pressed.connect( self.close )


    def _onChange( self, name ):
        Any.requireIsText( name )

        name   = str( name )
        label  = self._labels[ name ]
        field  = self._fields[ name ]
        revert = self._revert[ name ]

        label.setStyleSheet( self._styleChanged )
        field.setStyleSheet( self._styleChanged )

        revert.setEnabled( True )
        revert.setToolTip( 'revert to default' )


    def _onRevert( self, name ):
        logging.error( 'not implemented, yet' )

        logging.info( 'reverting %s', name )

        label       = self._labels[ name ]
        field       = self._fields[ name ]
        revert      = self._revert[ name ]
        font        = QFont()

        try:
            normalValue = self._conf.getNormalValue( name )
            self._allData[ name ] = normalValue
            field.setText( repr( normalValue ) )
            logging.info( 'config option "%s" reverted to %s', name, normalValue )
            self._conf.delUserConfigOption( name )

        except KeyError:
            # This exception occurs only when the given key is not present in both
            # machine and default settings i.e. when a new key was added by the user
            logging.info( "%s has no default value, deleting this key", name )

            self._conf.delUserConfigOption( name )

            font.setItalic( True )
            field.setFont( font )
            field.setText( 'no default value' )

        label.setStyleSheet( self._styleUnchanged )
        field.setStyleSheet( self._styleUnchanged )

        font.setItalic( False )
        field.setFont( font )

        revert.setEnabled( False )


    def _onSave( self ):
        logging.info( 'saving preferences' )

        for name, field in self._fields.items():

            oldValue = repr( self._allData[ name ] )
            newValue = str( field.text() )

            if newValue == 'no default value':
                pass
            elif oldValue != newValue:
                logging.info( 'value of "%s" changed: %s ==> %s',
                              name, oldValue, newValue )

                self._conf.setUserConfigOption( name, eval(newValue) )


        self._conf.save()


# EOF
