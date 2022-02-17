# -*- coding: utf-8 -*-
#
#  Terminal for remote process execution monitoring
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

from PyQt5.QtCore    import pyqtSignal, Qt, QProcess, QRegularExpression
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from ToolBOSCore.GenericGUI import IconProvider, ProcessExecutor, UnicodeSupport
from ToolBOSCore.Util       import Any


lightBlue   = QColor( 210, 230, 255 )
lightGreen  = QColor( 210, 255, 210 )
lightGrey   = QColor( 240, 240, 240 )
lightOrange = QColor( 255, 200, 100 )
lightYellow = QColor( 255, 248, 220 )
lightRed    = QColor( 255, 120, 120 )
solidRed    = QColor( 255,   0,   0 )


# noinspection PyArgumentList,PyUnresolvedReferences
class TerminalWidget( QWidget, object ):
    """
        Contains a QTextEdit (with domain-specific context menu) and a
        QLabel indicating the current working directory.
    """
    closeRequest          = pyqtSignal()
    hostChanged           = pyqtSignal( str )
    terminateAllProcesses = pyqtSignal()


    def __init__( self, readonly, inactiveColor=lightGrey,
                  runColor=lightYellow, exitSuccessColor=lightGreen,
                  exitFailureColor=lightRed, warningHighlightColor=lightOrange,
                  errorHighlightColor=solidRed, parent=None ):

        Any.requireIsBool( readonly )
        Any.requireIsInstance( inactiveColor,         QColor )
        Any.requireIsInstance( runColor,              QColor )
        Any.requireIsInstance( exitSuccessColor,      QColor )
        Any.requireIsInstance( exitFailureColor,      QColor )
        Any.requireIsInstance( warningHighlightColor, QColor )
        Any.requireIsInstance( errorHighlightColor,   QColor )

        super( QWidget, self ).__init__()

        self.command        = ''
        self.hostname       = 'localhost'
        self.homeDir        = os.path.expanduser( '~' )
        self.path           = os.getcwd()
        self.pipe           = None
        self.standalone     = False
        self.taskProcess    = None
        self.withX11Tunnel  = False

        self._loggingEnabled = False
        self._logFilename    = ''
        self._logFile        = None

        self.depChecker     = None
        self._missingDeps   = []

        self._closeAction   = None
        self._enabled       = False
        self._execCommand   = None
        self._showCommand   = None
        self._oldPath       = self.path
        self._oldColor      = None
        self._oldWinFlags   = None
        self._outputFilter  = None
        self._terminating   = False

        self._inactiveColor         = inactiveColor
        self._runColor              = runColor
        self._exitSuccessColor      = exitSuccessColor
        self._exitFailureColor      = exitFailureColor
        self._warningHighlightColor = warningHighlightColor
        self._errorHighlightColor   = errorHighlightColor

        self._defaultFont = QFont( 'Arial', 8 )

        self.hostnameField = QLineEdit( parent )
        self.hostnameField.setFont( self._defaultFont )
        self.hostnameField.setToolTip( 'hostname' )
        self.hostnameField.setText( self.hostname )
        self.hostnameField.setReadOnly( readonly )

        # noinspection PyUnresolvedReferences
        self.hostnameField.editingFinished.connect( self._onHostnameFieldInput )

        self.sepLabel  = QLabel( ':', parent )

        self.pathField = QLineEdit( parent )
        self.pathField.setFont( self._defaultFont )
        self.pathField.setToolTip( 'working directory (to change it type "cd ..." in operator shell below)' )
        self.pathField.setText( self.path )

        # noinspection PyUnresolvedReferences
        self.pathField.editingFinished.connect( self._onPathFieldInput )

        self.problemIndicator = QPushButton()
        self.problemIndicator.hide()

        self.xtermButton = QPushButton()
        self.xtermButton.setIcon( IconProvider.getIcon( 'utilities-terminal' ) )
        self.xtermButton.setToolTip( 'open xterm' )

        # search bar
        self.searchBar = QLineEdit( parent )
        self.searchBar.setFont( self._defaultFont )
        self.searchBar.setToolTip( 'search' )

        # noinspection PyUnresolvedReferences
        self.searchBar.textChanged.connect( self._onSearchBarFieldInput )

        self.searchBarLabel = QLabel( 'Search...', parent )
        self.searchBarLabel.setFont( self._defaultFont )

        # noinspection PyUnresolvedReferences
        self.xtermButton.pressed.connect( self._onXtermButton )

        self.hLayout  = QHBoxLayout()
        self.hLayout.setContentsMargins( 0, 0, 0, 0 )
        self.hLayout.addWidget( self.hostnameField )
        self.hLayout.addWidget( self.sepLabel )
        self.hLayout.addWidget( self.pathField )
        self.hLayout.addWidget( self.problemIndicator )
        self.hLayout.addWidget( self.xtermButton )
        self.hLayout.setStretchFactor( self.pathField, 2 )

        self.locationWidget = QWidget( parent )
        self.locationWidget.setLayout( self.hLayout )

        self.hFooterLayout = QHBoxLayout()
        self.hFooterLayout.setContentsMargins( 0, 0, 0, 0 )
        self.hFooterLayout.addWidget( self.searchBarLabel )
        self.hFooterLayout.addWidget( self.searchBar )
        self.hFooterLayout.setStretchFactor( self.searchBar, 2 )

        self.footerWidget = QWidget( parent )
        self.footerWidget.setLayout( self.hFooterLayout )
        self.footerWidget.setHidden( True )

        self.textField = self._TerminalTextEdit( warningColor=warningHighlightColor,
                                                 errorColor=errorHighlightColor,
                                                 parent=parent )

        self.textField.setColor( self._inactiveColor )
        self.textField.closeRequest.connect( self.closeRequest.emit )
        self.textField.reRunProcess.connect( self._reRun )
        self.textField.terminateThisProcess.connect( self.terminateThis )
        self.textField.terminateAllProcesses.connect( self.emitTerminateAll )
        self.textField.standaloneRequest.connect( self.toggleStandalone )
        self.textField.findRequest.connect( self.toggleSearch )

        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget( self.locationWidget )
        self.vLayout.addWidget( self.textField )
        self.vLayout.addWidget( self.footerWidget )

        self.setLayout( self.vLayout )


    def isSearchBarVisibile( self ):
        return self.footerWidget.isVisible()


    def searchBarVisibility( self, state ):
        Any.requireIsBool( state )
        self.footerWidget.setHidden( not state )


    def clear( self ):
        self.textField.clear()
        self.textField.setColor( self._inactiveColor )

        if self._logFile:
            self._logFile.close()
            self._logFile = None


    def closeEvent( self, event ):
        # in case the user closes the window: don't do that, instead put the
        # widget again into the grid-view
        event.ignore()
        self.toggleStandalone()


    def emitTerminateAll( self ):
        self._terminating = True

        self.terminateAllProcesses.emit()


    def isEnabled( self ):
        return self._enabled


    def kill( self ):
        try:
            logging.debug( 'terminating process %d', self.pipe.pid )
            self.pipe.kill()
        except ( AttributeError, OSError ):  # no such pipe, or terminated
            pass


    def run( self ):
        self._terminating = False

        self.writeCommand( self._showCommand )
        self.textField.setColor( self._runColor )
        self.taskProcess.start()


    def setColor( self, color ):
        Any.requireIsInstance( color, QColor )

        self.textField.setColor( color )


    def setCommand( self, command, showCommand=None ):
        """
            In certain cases the actual 'command' which shall be executed
            should not be visible to the user in this form.

            You may specify an alternative 'showCommand'.
        """
        Any.requireIsTextNonEmpty( command )

        self.command = command

        if not showCommand:
            self._showCommand = command
        else:
            self._showCommand = showCommand


    def setEnabled( self, enabled ):
        """
            The difference to setReadOnly() is the following:

            Use setEnabled() to mark a terminal as active or not.
            A disabled widget cannot be used and is shown with lightgrey
            shadow.

            In contrast, a terminal should be marked readonly during a
            program execution, f.i. the user cannot change values within
            this time.
        """
        self.setReadOnly( not enabled )
        self.textField.setEnabled( enabled )
        self.pathField.setEnabled( enabled )

        if self._enabled != enabled:
            # do color store / restore only if state changes, skip in case it
            # was already in the desired state (which would lead to problems
            # in color management)

            if enabled:
                # restore color if was not inactive == freshly created
                if self._oldColor is not None and \
                   self._oldColor is not self._inactiveColor:

                    self.textField.setColor( self._oldColor )
            else:
                # store original color for later restore
                # when disabling a terminal, store its original color for
                # later restore
                self._oldColor = self.textField.getColor()
                self.textField.setColor( self._inactiveColor )

        self._enabled = enabled


    def setHaveTerminateAll( self, status ):
        Any.requireIsBool( status )

        self.textField.setHaveTerminateAll( status )


    def setHostname( self, hostname ):
        Any.requireIsTextNonEmpty( hostname )

        self.hostname = hostname
        logging.debug( "changed hostname to '%s'", self.hostname )
        self._updateLabel()


    def setReadOnly( self, readOnly ):
        """
            The difference to setEnabled() is the following:

            Use setEnabled() to mark a terminal as active or not.
            A disabled widget cannot be used and is shown with lightgrey
            shadow.

            In contrast, a terminal should be marked readonly during a
            program execution, f.i. the user cannot change values within
            this time.
        """
        enabled = not readOnly

        self.hostnameField.setEnabled( enabled )
        self.pathField.setEnabled( enabled )      # not implemented, yet


    def setPath( self, path ):
        if not path:
            path = '~'                              # fallback to homedir.


        # compute new absolute path, resolve ".", ".." or symlinks

        path = os.path.expanduser( path )

        if os.path.isabs( path ):
            path = os.path.abspath( path )
        else:
            path = os.path.abspath( os.path.join( self.path, path ) )

        self.path = path
        self._updateLabel()
        self.writeText( '%s\n' % self.path )


    def setOutputFilter( self, func ):
        """
            Callback to be invoked before printing the command output to the
            terminal widget. Could be used to perform some textual
            replacements before displaying.

            The function will receive the original output as text parameter
            and is supposed to return the modified text.

            Use None to disable output filtering (= display original output).
        """
        if func is not None:
            Any.requireIsCallable( func )

        self._outputFilter = func


    def setTerminateAll( self, status ):
        Any.requireIsBool( status )

        self._haveTerminateAll = status


    def setToolTip( self, toolTipText ):
        Any.requireIsTextNonEmpty( toolTipText )

        self.textField.setToolTip( toolTipText )


    def setWithX11Tunnel( self, withX11 ):
        """
            Use SSH's X11 forwarding when executing commands on remote
            hosts?
        """
        Any.requireIsBool( withX11 )

        self.withX11Tunnel = withX11

    def setupLogging( self, enabled, filename ):
        self._loggingEnabled = enabled
        self._logFilename    = filename

        if enabled:
            logFileDir =  os.path.dirname( filename )
            if not os.path.exists( logFileDir ):
                os.mkdir( logFileDir )

            self._logFile = open( filename, 'w' )

    def setup( self ):
        self.taskProcess = ProcessExecutor.ProcessExecutor()

        self.taskProcess.setWithX11Tunnel( self.withX11Tunnel )

        # do not pollute the output with colorization escape sequences (TBCORE-1375)
        self.taskProcess.unsetEnv( 'TERM' )

        if self.command:
            self.taskProcess.setCommand( self.command )

        if self.hostname:
            self.taskProcess.setHostname( self.hostname )

        if self.path:
            self.taskProcess.setWorkingDirectory( self.path )

        self.taskProcess.started.connect( lambda: self.setReadOnly( True ) )
        self.taskProcess.started.connect( self.textField.programStarted )
        self.taskProcess.newStdOut.connect( self.writeText )
        self.taskProcess.newStdErr.connect( self.writeText )
        self.taskProcess.finished.connect( self._setTerminalColorFromExitStatus )


        # The thread may live longer than the actual process execution.
        # Therefore, react on both thread and program termination and
        # re-enable the widgets.
        enable = lambda: self.setReadOnly( False )
        self.taskProcess.finished.connect( enable )
        self.taskProcess.finished.connect( self.textField.programFinished )

        if self.hostname not in ( 'localhost', '127.0.0.1', '::1' ) and \
            self.command.strip().startswith( 'cd' ):

            # "cd" on remote host
            self.taskProcess.newProgramExitStatus.connect( self._resetPath )

        return self.taskProcess


    def terminateThis( self ):
        self._terminating = True

        if self.taskProcess is None or self.taskProcess.state() == QProcess.NotRunning:
            self._setTerminalColorFromExitStatus( 'no process' )
        else:
            self.taskProcess.terminate()


    def toggleSearch( self ):
        self.searchBarVisibility( not self.isSearchBarVisibile() )


    def toggleStandalone( self):
        self.standalone = not self.standalone

        if self.standalone:
            self._oldWinFlags = self.windowFlags()
            self.setWindowFlags( Qt.Window )

            # noinspection PyArgumentList
            screen = QApplication.desktop().screenGeometry()

            width  = screen.width()  * 0.5
            height = screen.height() * 0.75
            self.resize( width, height )

            self._closeAction = QAction( "Close", self )
            self._closeAction.setShortcut( 'Ctrl+W' )
            self._closeAction.triggered.connect( self.close )

            self.addAction( self._closeAction )

        else:
            self.setWindowFlags( self._oldWinFlags )
            self.removeAction( self._closeAction )

            self._closeAction = None


        self.textField.setStandalone( self.standalone )

        # when changing the window flags the font gets reset --> ensure the
        # right font, and do not forget to show() it!
        self.textField.setFontFamily( "Courier New" )
        self.show()


    def writeCommand( self, command ):
        self.textField.writeCommand( command )


    def writeText( self, toWrite ):
        text = UnicodeSupport.convert( toWrite )

        if self._outputFilter:
            text = self._outputFilter( text )

        if self._loggingEnabled:
            self._logFile.write( text )
            self._logFile.flush()

        self.textField.writeText( text )


    def _onHostnameFieldInput( self ):
        self.problemIndicator.hide()

        self.setHostname( str( self.hostnameField.text() ) )
        self.setup()

        self.hostChanged.emit( self.hostname )


    def _onSearchBarFieldInput( self ):
        if self.searchBar.isModified():
            searchText = self.searchBar.text()
            self.textField.findAndHighlightAll( searchText )


    def _onPathFieldInput( self ):
        newPath = str( self.pathField.text() )

        if os.path.abspath( os.path.expanduser( newPath ) ) != self.path:
            self.writeCommand( 'cd %s' % newPath )
            self.setPath( newPath )
            self.setColor( self._exitSuccessColor )       # but unsure if exists
            logging.info( "cd %s", self.path )


    def _onXtermButton( self ):
        ProcessExecutor.runXterm( self.hostname, self.path )


    def _resetPath( self, status ):
        if status == 0:
            self._oldPath = self.path    # keep for next 'cd'
        else:
            self.path = self._oldPath
            self._updateLabel()


    def _reRun( self ):
        """
            Launches the same command again.

            If necessary stops any still running thread in this terminal.
        """
        if self.command:
            self.taskProcess.terminate( )
            self.run()
        else:
            logging.info( 'cannot re-run (no command executed yet)' )


    def _setTerminalColorFromExitStatus( self, status ):
        self.textField.ensureCursorVisible()

        if status == 'no process':
            self.writeText( '[no process running]\n' )

        elif self._terminating:
            self.textField.setColor( self._exitFailureColor )
            self.writeText( '[Terminated]\n' )

        elif status == 0:
            self.textField.setColor( self._exitSuccessColor )
            self.writeText( '[Done]\n' )

        else:
            self.textField.setColor( self._exitFailureColor )
            self.writeText( '[Exited with status %d]\n' % status )

        self.textField.ensureCursorVisible()


    def _updateLabel( self ):
        # update hostname in textfield
        self.hostnameField.setText( self.hostname )

        # update directory in textfield
        showPath = os.path.expanduser( self.path )
        showPath = showPath.replace( self.homeDir, '~' )
        self.pathField.setText( showPath )


    # noinspection PyArgumentList,PyUnresolvedReferences
    class _TerminalTextEdit( QTextEdit, object ):
        """
            Contains a QTextEdit (with domain-specific context menu.
        """
        closeRequest          = pyqtSignal()
        reRunProcess          = pyqtSignal()
        standaloneRequest     = pyqtSignal()
        terminateThisProcess  = pyqtSignal()
        terminateAllProcesses = pyqtSignal()
        findRequest           = pyqtSignal()


        class _SearchHighlighter( QSyntaxHighlighter ):

            def __init__( self, parent=None, pattern=None ):
                super( QSyntaxHighlighter, self ).__init__( parent )

                self.keywordFormat = QTextCharFormat()
                self.keywordFormat.setForeground( Qt.darkBlue )
                self.keywordFormat.setFontWeight( QFont.Bold )

                if pattern:
                    self.highlightingRules = [ ( QRegularExpression( pattern ), self.keywordFormat ) ]
                else:
                    self.highlightingRules = []

            def setPattern( self, pattern=None ):
                if pattern:
                    self.highlightingRules = [ ( QRegularExpression( pattern ), self.keywordFormat ) ]
                else:
                    self.highlightingRules = []


            def highlightBlock( self, text ):
                for pattern, format in self.highlightingRules:
                    globalMatch = pattern.globalMatch( text )
                    while globalMatch.hasNext():
                        match = globalMatch.next()
                        length = match.capturedLength()
                        start = match.capturedStart()
                        self.setFormat( start, length, format )

                self.setCurrentBlockState( 0 )


        def __init__( self, warningColor=lightOrange,
                      errorColor=solidRed, parent=None ):

            Any.requireIsInstance( warningColor, QColor )
            Any.requireIsInstance( errorColor, QColor )

            super( QTextEdit, self ).__init__( parent )

            self.setReadOnly( True )
            self.setFontFamily( "Courier New" )
            self.setContextMenuPolicy( Qt.CustomContextMenu )
            self.customContextMenuRequested.connect( self._showContextMenu )

            self._autoScroll              = True
            self._frozen                  = False
            self._haveReRunAction         = False
            self._haveTerminateThisAction = False
            self._haveTerminateAllAction  = False
            self._standalone              = False
            self._tooltipText             = ''

            self._highlightCharNone   = QTextCharFormat()
            self._highlightCharNone.setFontFamily( "Courier New" )
            self._highlightCharNone.setFontPointSize( 9 )

            self._highlightBlockNone  = QTextBlockFormat()

            self._highlightCharWarn   = QTextCharFormat()
            self._highlightCharWarn.setFontFamily( "Courier New" )
            self._highlightCharWarn.setFontPointSize( 9 )

            self._highlightBlockWarn  = QTextBlockFormat()
            self._highlightBlockWarn.setBackground( warningColor )

            self._highlightCharError  = QTextCharFormat()
            self._highlightCharError.setFontFamily( "Courier New" )
            self._highlightCharError.setFontWeight( QFont.Bold )
            self._highlightCharError.setFontPointSize( 9 )

            self._highlightBlockError = QTextBlockFormat()
            self._highlightBlockError.setBackground( errorColor )

            self._searchHighlighter = self._SearchHighlighter()


        def getColor( self ):
            return self.palette().color( self.backgroundRole() )


        def programFinished( self ):
            self._haveTerminateThisAction = False


        def programStarted( self ):
            self._haveReRunAction         = True
            self._haveTerminateThisAction = True
            self._autoScroll              = True


        def setColor( self, color ):
            Any.requireIsInstance( color, QColor )

            palette = self.palette()
            palette.setColor( QPalette.Base, color )
            self.setAutoFillBackground( True )
            self.setPalette( palette )


        def setHaveTerminateAll( self, status ):
            Any.requireIsBool( status )

            self._haveTerminateAllAction = status


        def setStandalone( self, boolean ):
            Any.requireIsBool( boolean )
            self._standalone = boolean


        def wheelEvent( self, event ):
            scrollBar = self.verticalScrollBar()
            self._autoScroll = scrollBar.value() == scrollBar.maximum()

            super( QTextEdit, self ).wheelEvent( event )


        def writeCommand( self, command ):
            if not self._frozen:
                self._cursorToEnd()
                self.append( '<b>$ %s</b><br/>\n' % command )
                self._cursorToEnd()

                self._haveReRunAction = True


        def writeText( self, toWrite ):
            if not self._frozen:

                text = UnicodeSupport.convert( toWrite )

                self._cursorToEnd()
                cursor = self.textCursor()

                begin = cursor.position()
                self.insertPlainText( text )
                end   = cursor.position()

                if text.find( 'error:' ) >= 0 or \
                   text.find( '[ERROR]' ) >= 0 or \
                   text.find( 'make: *** [all] Error' ) >= 0:

                    highlightChar    = self._highlightCharError
                    highlightBlock   = self._highlightBlockError
                    self._autoScroll = False

                elif text.find( 'warning:' ) >= 0 or \
                     text.find( '[WARNING]' ) >= 0:

                    highlightChar    = self._highlightCharWarn
                    highlightBlock   = self._highlightBlockWarn


                else:
                    highlightChar    = self._highlightCharNone
                    highlightBlock   = self._highlightBlockNone


                cursor.setPosition( begin, QTextCursor.MoveAnchor )
                cursor.setPosition( end, QTextCursor.KeepAnchor )

                Any.requireIsInstance( highlightChar, QTextCharFormat )
                cursor.setCharFormat( highlightChar )

                Any.requireIsInstance( highlightBlock, QTextBlockFormat )
                cursor.setBlockFormat( highlightBlock )

                self._cursorToEnd()


        def _clearTerminal( self ):
            self.clear()


        def _cursorToEnd( self ):
            """
                Mouse clicks change the cursor position, hence we need to
                update the cursor's write location (move back to end of
                text) otherwise build logs get mixed up.

                This function considers the self._autoScroll property:
                If 'True' then the vertical scrollbar will always be at the
                bottom to allow the user reading the very latest loglines.
                If self._autoScroll is False the scrollbar won't change its
                position.
            """
            scrollBar       = self.verticalScrollBar()
            oldScrollBarPos = scrollBar.value()

            cursor = self.textCursor()
            cursor.movePosition( QTextCursor.End, QTextCursor.MoveAnchor )
            self.setTextCursor( cursor )

            if not self._autoScroll:
                scrollBar.setValue( oldScrollBarPos )


        def findAndHighlightAll( self, text ):
            Any.requireIsText( text )

            # Disable the highlighting
            self._searchHighlighter.setDocument( None )

            # if we have something to search
            if text:
                self._searchHighlighter.setPattern( text )
                self._searchHighlighter.setDocument( self.document() )


        def _freeze( self ):
            self.writeText( '[Terminal frozen]\n' )
            self._frozen = True


        def _reRunProcess( self ):
            self.reRunProcess.emit()


        def _showContextMenu( self, pos ):
            menu = self.createStandardContextMenu()

            standaloneAction = QAction( self )
            standaloneAction.triggered.connect( lambda: self.standaloneRequest.emit() )

            if self._standalone:
                standaloneAction.setText( 'Attach to main window' )
                standaloneAction.setShortcut( QKeySequence( Qt.CTRL + Qt.Key_W ) )
            else:
                standaloneAction.setText( 'Detach from main window' )

            menu.addAction( standaloneAction )


            # the "terminate"-action is only available during process execution

            terminateThisAction = QAction( self )
            terminateThisAction.setText( 'Terminate this' )
            terminateThisAction.triggered.connect( self._terminateThisProcess )
            terminateThisAction.setEnabled( self._haveTerminateThisAction )

            menu.addAction( terminateThisAction )


            # if the "terminate all"-action is enabled, ist must be always visible

            if self._haveTerminateAllAction:
                terminateAllAction = QAction( self )
                terminateAllAction.setText( 'Terminate all' )
                terminateAllAction.triggered.connect( self._terminateAllProcesses )

                menu.addAction( terminateAllAction )


            if self._frozen:
                menu.addAction( 'Un-freeze', self._unfreeze )
            else:
                menu.addAction( 'Freeze', self._freeze )

            menu.addSeparator()
            menu.addAction( 'Clear', self._clearTerminal )


            # the "re-run"-action is disabled until a command was executed

            reRunAction = QAction( self )
            reRunAction.setText( 'Re-run' )
            reRunAction.triggered.connect( self._reRunProcess )
            reRunAction.setEnabled( self._haveReRunAction )

            menu.addAction( reRunAction )


            # the "close"-action is disabled on the localhost-terminal,
            # therefore it is handled separately

            closeAction = QAction( self )
            closeAction.setText( 'Close' )
            closeAction.triggered.connect( self.closeRequest.emit )
            closeAction.setEnabled( self._tooltipText != 'localhost' )

            menu.addAction( closeAction )

            # Search
            searchAction = QAction( self )
            searchAction.setText('Find...')
            searchAction.triggered.connect( self.findRequest.emit )

            menu.addSeparator()
            menu.addAction( searchAction )

            menu.exec_( self.mapToGlobal( pos ) )


        def _terminateThisProcess( self ):
            self.terminateThisProcess.emit()


        def _terminateAllProcesses( self ):
           self.terminateAllProcesses.emit()


        def _unfreeze( self ):
            self._frozen = False
            self.writeText( '[Terminal activated]\n' )


class MultiTermWidget( QGroupBox, object ):
    """
        Provides a group box for various QWidgets, arranged in a grid layout.
    """


    def __init__( self, parent=None ):

        super( QGroupBox, self ).__init__( 'console outputs', parent )

        self._terminals          = []
        self.layout              = QVBoxLayout()

        # Control the vertical resizing between Containers
        self._colSplitter        = QSplitter( Qt.Vertical )
        self._maxCols            = 3
        self._rowContainers      = []
        self._rowSplitter        = []
        self._currentContainer   = None
        self._currentRowSplitter = None

        self.layout.setContentsMargins( 0, 0, 0, 0 )   # no add. margin
        self.layout.addWidget( self._colSplitter )
        self.setLayout( self.layout )


    def addTerminal( self, terminal ):
        """
            Puts the provided terminal into a grid layout, with dynamic
            resizing and handles for manual resize.
        """
        self._terminals.append( terminal )

        if not self._currentRowSplitter or \
                ( self._currentRowSplitter and
                  self._currentRowSplitter.count() >= self._maxCols ):
            self._currentRowSplitter = QSplitter( Qt.Horizontal )
            self._rowSplitter.append( self._currentRowSplitter )
            self._currentContainer = None

        if not self._currentContainer:
            hLayout = QHBoxLayout()
            hLayout.setContentsMargins( 0, 0, 0, 0 )
            hLayout.addWidget( self._currentRowSplitter )

            self._currentContainer = QWidget()
            self._rowContainers.append( self._currentContainer )
            self._currentContainer.setLayout( hLayout )

            self._colSplitter.addWidget( self._currentContainer )

        self._currentRowSplitter.addWidget( terminal )
        self.setHaveTerminateAll( len( self._terminals ) > 1 )

        # ensure to only connect exactly once even if this addTerminal()
        # might be called repetitive on the same terminal, otherwise
        # the slot gets executed multiple times resulting in multiple
        # '[Terminated]' messages
        try:
            terminal.terminateAllProcesses.disconnect()
        except TypeError:
            pass                                 # was not connected

        terminal.terminateAllProcesses.connect( self.terminateAllProcesses )
        terminal.show()


    def clear( self ):
        for terminal in self._terminals:
            terminal.setHaveTerminateAll( False )
            terminal.hide()

        for splitter in self._rowSplitter:
            splitter.hide()

        for container in self._rowContainers:
            container.hide()

        self._terminals = []
        self._rowContainers = []
        self._rowSplitter = []
        self._currentContainer = None
        self._currentRowSplitter = None


    def getTerminals( self ):
        return self._terminals

    def setHaveTerminateAll( self, status ):
        Any.requireIsBool( status )

        for terminal in self._terminals:
            terminal.setHaveTerminateAll( status )


    def setOutputFilter( self, func ):
        """
            Callback to be invoked before printing the command output to the
            terminal widget. Could be used to perform some textual
            replacements before displaying.

            The function will receive the original output as text parameter
            and is supposed to return the modified text.

            Use None to disable output filtering (= display original output).
        """
        if func is not None:
            Any.requireIsCallable( func )

        for terminal in self._terminals:
            terminal.setOutputFilter( func )


    def terminateAllProcesses( self ):
        logging.debug( 'terminating all...' )

        for terminal in self._terminals:
            terminal.terminateThis()


# EOF

