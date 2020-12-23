# -*- coding: utf-8 -*-
#
#  Functions to create a new package
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


import io
import logging

import sip

sip.setapi( 'QString', 2 )
sip.setapi( 'QVariant', 2 )

from PyQt5.QtCore    import pyqtSignal
from PyQt5.QtCore    import QThread
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *

from ToolBOSCore.GenericGUI import PixmapProvider
from ToolBOSCore.Packages   import PackageCreator
from ToolBOSCore.Util       import Any


class PackageCreatorGUI( object ):

    vbox    = None
    gridWid = None
    grid    = None
    qwiz    = None

    _startupWidth = 800


    def _createWizardPage_chooseTemplateType( self ):
        """
            Returns a QWizardPage object which asks for the data source.
        """
        page = QWizardPage()
        page.setTitle( 'Select template type' )
        page.setSubTitle( 'Please choose the type of package to be created.' )

        radios = []
        group  = QVBoxLayout( page )


        tmp = filter( self._isVisibleTemplate, PackageCreator.getTemplatesAvailable() )
        self._templatesAvailable = list( tmp )

        for template in self._templatesAvailable:
            logging.debug( 'available template: %s', template )
            text  = template.replace( '_', ' ' )
            radio = QRadioButton( text )
            page.registerField( template, radio )
            radios.append( radio )
            group.addWidget( radio )

        Any.requireMsg( len(radios) > 0, "No templates found, likely a bug :-(" )


        radios[0].setChecked( True )

        return page


    def _createWizardPage_details( self ):
        """
            Returns a QWizardPage object which asks for necessary parameters.
        """
        class MyDetailsPage( QWizardPage ):

            def __init__( self, templatesAvailable ):
                """
                    Factory method to produce this wizard page.
                """
                super( QWizardPage, self ).__init__()

                Any.requireIsListNonEmpty( templatesAvailable )


                self.setTitle( 'Package details' )
                self.setSubTitle( 'Please provide remaining information ' +
                                  'for starting the package creation process.' )

                self.vbox         = QVBoxLayout( self )
                self.gridWid      = QWidget()
                self.grid         = QGridLayout()
                self.nameLabel    = QLabel( 'Package name:' )
                self.nameValue    = QLineEdit( 'MyPackage' )
                self.versionLabel = QLabel( 'Package version:' )
                self.versionValue = QLineEdit( '1.0' )
                self.flatStyle    = QCheckBox( 'flat directory structure (new style)' )
                self.goButton     = QPushButton( '&Create' )
                self.logWindow    = QTextEdit()

                self.flatStyle.setChecked( True )

                self.grid.addWidget( self.nameLabel,    1, 1 )
                self.grid.addWidget( self.nameValue,    1, 2 )
                self.grid.addWidget( self.versionLabel, 2, 1 )
                self.grid.addWidget( self.versionValue, 2, 2 )
                self.grid.addWidget( self.flatStyle,    3, 2 )
                self.grid.addWidget( self.goButton,     4, 2 )

                # -11 is the default margin on most platforms
                self.gridWid.setContentsMargins( -8, 0, -8, 0 )
                self.gridWid.setLayout( self.grid )
                self.vbox.addWidget( self.gridWid )
                self.vbox.addWidget( self.logWindow )

                self.goButton.pressed.connect( self.onGoButtonPressed )

                # the asterisk flags it is mandatory (= needs to be filled)
                self.registerField( 'packageName*',    self.nameValue )
                self.registerField( 'packageVersion*', self.versionValue )

                self.packageName    = None
                self.packageVersion = None
                self.template       = None
                self.finished       = False
                self.workerThread   = None

                self._templatesAvailable = templatesAvailable


            def initializePage( self ):
                """
                    This is called by QWizard every time this wizard
                    page is shown. It is primarily used to prepare the
                    GUI depending on selections the user made on previous
                    wizard pages.
                """
                self.finished = False

                self.goButton.setEnabled( True )
                self.logWindow.setEnabled( False )
                self.logWindow.setReadOnly( True )
                self.logWindow.setFixedHeight( 250 )
                self.logWindow.setText( 'log output will be shown here...' )

                self.template = None

                for template in self._templatesAvailable:
                    if self.field( template ):
                        self.template = template
                        break


            def onGoButtonPressed( self ):
                """
                    Perform the creation with the settings from the GUI.
                """
                self.goButton.setEnabled( False )
                self.logWindow.setEnabled( True )
                self.logWindow.clear()

                self.packageName    = self.field( 'packageName'    )
                self.packageVersion = self.field( 'packageVersion' )
                flatStyle           = self.flatStyle.isChecked()
                args                = [ '--flat' ] if flatStyle else []

                args.extend( [ self.template, self.packageName, self.packageVersion ] )

                command = 'BST.py --new %s' % ' '.join( args )

                self.logWindow.insertHtml( '$ <b>' + command + '</b>\n' )
                logging.info( 'executing: %s', command )

                self.workerThread = PackageCreatorThread( self.template,
                                                          self.packageName,
                                                          self.packageVersion,
                                                          flatStyle )

                self.workerThread.finished.connect( self.onProcessFinished )
                self.workerThread.newOutput.connect( lambda s: self.onNewOutput( s ) )
                self.workerThread.start()


            def onProcessFinished( self ):
                """
                    Actions to be done after the export finished.
                """
                self.finished = True
                self.completeChanged.emit()


            def isComplete( self ):
                """
                    Returns 'bool' when finish button shall be enabled.
                """
                return self.finished


            def onNewOutput( self, output ):
                """
                    Write output into log window.
                """
                self.logWindow.append( output )


        return MyDetailsPage( self._templatesAvailable )


    def _isVisibleTemplate( self, templateName ):
        """
            Returns a boolean whether or not the given template is intended
            to be shown in the PackageCreator GUI.
        """
        template = PackageCreator.packageCreatorFactory( templateName,
                                                           "DummyPackage",
                                                           "0.0" )

        return template.show


    def runGUI( self, parent=None ):

        class SideWidget( QWidget ):
            """
                Derived class showing the BST logo on white ground.
                Such widget is shown on the left side of the wizard dialog.
            """
            def __init__( self ):
                QWidget.__init__( self )

                bannerImage = PixmapProvider.getPixmap( 'BST-Banner' )

                bannerWidget = QLabel()
                bannerWidget.setPixmap( bannerImage )

                layout = QVBoxLayout()
                layout.addWidget( bannerWidget )

                self.setLayout( layout )
                self.setStyleSheet( 'background-color: white;' )


        self.qwiz = QWizard( parent )
        self.qwiz.addPage( self._createWizardPage_chooseTemplateType() )
        self.qwiz.addPage( self._createWizardPage_details()  )
        self.qwiz.setWindowTitle( 'Build System Tools - Package Creator' )
        self.qwiz.setSideWidget( SideWidget() )

        self.qwiz.setMinimumWidth( self.qwiz.width() * 1.3 )
        self.qwiz.resize( self._startupWidth, self.qwiz.height() )

        self.qwiz.show()


    def main( self ):
        """
            Call this function if PackageCreator is the only Qt GUI
            application at this time.

            When called from another Qt application use runGUI() instead.
        """
        app = QApplication( [] )
        app.setStyle( 'fusion' )

        self.runGUI()
        app.exec_()


class PackageCreatorThread( QThread ):

    newOutput = pyqtSignal( str )


    # Python 2.7 has a bug when threads are created outside the "threading"
    # module (such as by QThread). In Python 3.x this is already solved.
    #
    # http://stackoverflow.com/questions/13193278/understand-python-threading-bug
    #
    # A workaround is to provide a __block member
    __block  = None

    def __init__( self, templateName, packageName, packageVersion, flatStyle ):
        QThread.__init__( self )

        Any.requireIsTextNonEmpty( templateName )
        Any.requireIsTextNonEmpty( packageName )
        Any.requireIsTextNonEmpty( packageVersion )
        Any.requireIsBool( flatStyle )

        self.templateName   = templateName
        self.packageName    = packageName
        self.packageVersion = packageVersion
        self.flatStyle      = flatStyle


    def run( self ):
        progressLog = io.StringIO()
        debugLevel  = logging.DEBUG if Any.getDebugLevel() > 3 else logging.INFO

        Any.addStreamLogger( progressLog, debugLevel, False )

        PackageCreator.runTemplate( self.templateName,
                                    self.packageName,
                                    self.packageVersion,
                                    flatStyle=self.flatStyle )

        self.newOutput.emit( progressLog.getvalue() )


# EOF
