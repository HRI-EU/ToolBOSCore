#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import os
import shlex
import socket
import threading

import sip

sip.setapi( 'QString', 2 )
sip.setapi( 'QVariant', 2 )

from PyQt5.QtCore    import pyqtSignal, QObject, QByteArray
from PyQt5.QtWidgets import *

from ToolBOSCore.BuildSystem  import BuildSystemTools
from ToolBOSCore.ZenBuildMode import BuildOptionsWidget, ConsoleWidget,\
                                     DependencyChecker, ExternalToolsWidget,\
                                     InstallDialog, MenuBar, MetaInfoWidget,\
                                     QtPackageModel, TaskButtonsWidget
from ToolBOSCore.GenericGUI   import IconProvider, TerminalWidget
from ToolBOSCore.Packages     import ProjectProperties
from ToolBOSCore.Platforms    import CrossCompilation, Platforms
from ToolBOSCore.Settings     import ToolBOSConf
from ToolBOSCore.Storage      import VersionControl
from ToolBOSCore.Tools        import SSH
from ToolBOSCore.Util         import Any, FastScript


class MainWindow( QObject, object ):
    """
        GUI controller class
    """
    _seqTasksRun      = pyqtSignal()
    _seqTasksFinished = pyqtSignal()


    def __init__( self, projectRoot=None ):

        QObject.__init__( self )

        self.app                    = None
        self.console                = None
        self.controlsLayout         = None
        self.controlsWidget         = None
        self.enabledCBs             = []
        self.externalTools          = None
        self.globalInstDialog       = None
        self.lock                   = threading.Lock()
        self.mainLayout             = None
        self.mainWidget             = None
        self.menuBar                = None
        self.metaInfo               = None
        self.model                  = QtPackageModel.BSTPackageModel()
        self.multiTermWidget        = None
        self.optionsWidget          = None
        self.platformCBs_nat        = {}
        self.platformCBs_natLayout  = None
        self.platformCBs_natWidget  = None
        self.platformCBs_xcmp       = {}
        self.platformCBs_xcmpLayout = None
        self.platformCBs_xcmpWidget = None
        self.projectRoot            = projectRoot
        self.rightPaneLayout        = None
        self.rightPaneWidget        = None
        self.runningProcesses       = 0
        self.taskButtons            = None
        self.terminals              = {}
        self.visibleRemoteTerminals = set()
        self.window                 = None

        self._depCheckers           = {}
        self._seqTasks              = []                # task queue
        self._toolBOSConf           = ToolBOSConf.getGlobalToolBOSConf()

        # unset VERBOSE environment variable as this would be inherited to
        # child processes, this is not intended -- instead we will rely on
        # the corresponding checkbox
        FastScript.unsetEnv( 'VERBOSE' )


    def build( self ):
        options = ''

        if self.optionsWidget.getVerboseValue():
            options += ' -v'

        jobs = self.optionsWidget.getParallelValue()

        if jobs > 1:
            options += ' -j %d' % jobs

        protoCmd = 'BST.py %s' % options
        self.console.addCommandToHistory_remote( protoCmd )
        self._disableButtons()
        self._focusRemoteTerminals()


        for platform, checkbox in self.platformCBs_nat.items():
            if checkbox.isChecked():
                try:
                    terminal = self.terminals[ 'nativ_' + platform ]
                    hostname = terminal.hostname
                    command  = protoCmd

                    logging.info( 'compiling natively on %s for %s',
                                  hostname, platform )

                    self._execProgram( terminal, command )
                except KeyError:
                    pass            # don't build / ignore disabled platforms


        for platform, checkbox in self.platformCBs_xcmp.items():
            if checkbox.isChecked():
                try:
                    platform = str( checkbox.text() )
                    terminal = self.terminals[ 'xcomp_' + platform ]
                    hostname = terminal.hostname
                    command  = '%s -p %s' % ( protoCmd, platform )

                    logging.info( 'cross-compiling on %s for %s', hostname, platform )
                    logging.debug( 'terminal=%s', str(terminal) )

                    self._execProgram( terminal, command )
                except KeyError:
                    pass            # don't build / ignore disabled platforms


    def clean( self ):
        if self.optionsWidget.getVerboseValue():
            command = 'BST.py -dv'
        else:
            command = 'BST.py -d'

        self.console.addCommandToHistory_local( command )
        self._focusLocalTerminal()
        self._execProgram( self.terminals[ 'localhost' ], command )


    def quit( self ):
        logging.debug( 'closing connections...' )

        for terminal in self.terminals.values():
            terminal.kill()

        logging.debug( 'exiting application...' )
        self.app.closeAllWindows()


    def globalInstall( self ):
        force = self._toolBOSConf.getConfigOption( 'BST_svnCheck' ) == False

        if force or self.globalInstall_vcsCheck():
            self.globalInstall_askReason()


    def globalInstall_vcsCheck( self ):
        try:
            vcs    = VersionControl.auto()
            errors = vcs.consistencyCheck()

        except EnvironmentError:

            errors = [ 'No VCS revision information.',
                       'Unable to find ".svn" or ".git" directories.',
                       'Please make sure to install from a SVN working '
                       'copy or Git repository.' ]


        if errors:
            title = errors[0]
            msg   = 'Attention: ' + errors[1] + '\n\n' + errors[2]

            dialog = QMessageBox()
            dialog.critical( self.window, title, msg, QMessageBox.Cancel )
            dialog.show()

            return False
        else:
            return True


    def globalInstall_askReason( self ):
        self.globalInstDialog = InstallDialog.GlobalInstallDialog()
        self.globalInstDialog.cancelled.connect( self._enableButtons )
        self.globalInstDialog.ready.connect( self.globalInstall_exec )
        self.globalInstDialog.show()


    def globalInstall_exec(self, changeType, reason):
        Any.requireIsTextNonEmpty( changeType )
        Any.requireIsTextNonEmpty( reason )

        # escape any doublequotes to not confuse the shlex used later on
        # (TBCORE-1323)
        reason     = reason.replace( '"', '\\"' )
        logging.debug( 'reason: %s', reason )


        # Potentially this could be more generalized, f.i. into
        # PackageDetector / pkgInfo.py --> "Does pkg. need seq. install"?
        Any.requireIsTextNonEmpty( self.projectRoot )
        installHook  = os.path.join( self.projectRoot, 'installHook.sh' )
        doSeqInstall = os.path.exists( installHook )


        if doSeqInstall:
            msg = '%s: %s (<MAKEFILE_PLATFORM>)' % ( changeType, reason )
        else:
            msg = '%s: %s' % ( changeType, reason )


        if self.optionsWidget.getVerboseValue():
            command = 'BST.py -ivy -M "%s"' % msg
        else:
            command = 'BST.py -iy -M "%s"' % msg


        # If the package has a installHook.sh (like in most "External" pkg.)
        # we need to launch the native installation on each individual
        # platform rather than on localhost only so that the installHook.sh
        # gets executed for each platform (see TBCORE-1094).

        if doSeqInstall:
            logging.info( 'performing sequential installation for each platform' )
            self._execProgramSequential( command )
        else:
            logging.info( 'performing combined multi-platform installation' )
            self._focusLocalTerminal()
            self._execProgram( self.terminals[ 'localhost' ], command )


    def main( self ):
        self.app                    = QApplication( [] )

        self.app.setStyle( 'fusion' )

        self.window                 = QMainWindow()
        self.menuBar                = MenuBar.MenuBar( self.window )
        self.mainLayout             = QGridLayout()
        self.mainWidget             = QWidget()
        self.multiTermWidget        = TerminalWidget.MultiTermWidget()
        self.optionsWidget          = BuildOptionsWidget.BuildOptionsWidget()
        self.controlsLayout         = QHBoxLayout()
        self.controlsWidget         = QWidget()
        self.metaInfo               = MetaInfoWidget.MetaInfoWidget( self.model, self.controlsWidget )
        self.console                = ConsoleWidget.ConsoleWidget( self.controlsWidget )
        self.taskButtons            = TaskButtonsWidget.TaskButtonsWidget()
        self.platformCBs_natLayout  = QVBoxLayout()
        self.platformCBs_natWidget  = QGroupBox( 'build natively on' )
        self.platformCBs_xcmpLayout = QVBoxLayout()
        self.platformCBs_xcmpWidget = QGroupBox( 'cross-compile for' )
        self.rightPaneLayout        = QVBoxLayout()
        self.rightPaneWidget        = QWidget()
        self.runningProcesses       = 0


        self._seqTasksRun.connect( self._onSeqTasksRun )
        self._seqTasksFinished.connect( self._onSeqTasksFinished )

        # create an always existing terminal for localhost commands
        terminal = TerminalWidget.TerminalWidget( True, parent=self.multiTermWidget )
        terminal.setToolTip( 'localhost' )
        terminal.setWindowTitle('localhost')

        self.terminals[ 'localhost' ] = terminal
        self.multiTermWidget.addTerminal( terminal )

        BST_localPaths     = tuple( ToolBOSConf.getConfigOption( 'BST_localPaths' ) )
        localHostname      = socket.gethostname()
        sshPossible        = SSH.guessRemoteAccessIsPossible()
        sshToolTip         = 'Remote compilation not possible as SSH authorized keys are not configured'
        onLocaldiskToolTip = 'Remote compilation not possible as project is on local disc'
        projectOnLocaldisk = self.projectRoot.startswith( BST_localPaths )
        remoteCompilation  = sshPossible and not projectOnLocaldisk
        xcmpPlatforms      = []
        crossCompileHosts  = self._toolBOSConf.getConfigOption( 'BST_crossCompileHosts' )


        Any.requireIsDictNonEmpty( crossCompileHosts )

        for platformName, compileHost in crossCompileHosts.items():
            if compileHost:
                xcmpPlatforms.append( platformName )

        xcmpPlatforms.sort()

        # platform selection in right pane,
        # create terminals for all other platforms (hide disabled ones)
        nativePlatforms  = Platforms.getPlatformNames()
        defaultNative    = CrossCompilation.getNativeCompilationList()
        defaultXcmp      = CrossCompilation.getCrossCompilationList()

        for platform in nativePlatforms:
            checkbox = QCheckBox( platform )
            checkbox.setChecked( platform in defaultNative )
            checkbox.stateChanged.connect( self._onPlatformSelectionChange )
            compileHost = CrossCompilation.getNativeCompileHost( platform )
            natHost = 'Natively compile for "%s" on "%s"' % (platform, compileHost)
            checkbox.setToolTip( natHost )

            self.platformCBs_nat[ platform ] = checkbox
            self.platformCBs_natLayout.addWidget( checkbox )

            if remoteCompilation or compileHost == localHostname:
                checkbox.setEnabled( True )

            else:
                checkbox.setEnabled( False )
                checkbox.setChecked( False )
                if projectOnLocaldisk:
                    checkbox.setToolTip( onLocaldiskToolTip )

                elif not sshPossible:
                    checkbox.setToolTip( sshToolTip )


            try:
                compileHost = CrossCompilation.getNativeCompileHost( platform )

                if compileHost:
                    logging.debug( 'native compile-host for platform=%s: %s',
                                   platform, compileHost )

                    fullPlatformString = Platforms.getFullPlatformString( platform )

                    infoText = 'Console output for %s (%s)' % ( platform, fullPlatformString )

                    terminal = TerminalWidget.TerminalWidget( False, parent=self.multiTermWidget )
                    terminal.setHostname( compileHost )
                    terminal.setToolTip( infoText )
                    terminal.setWindowTitle( infoText )

                    terminal.isNative = True

                    terminal.hostChanged.connect( functools.partial(
                                                        self._onHostChange,
                                                        terminal ) )

                    terminal.closeRequest.connect( functools.partial(
                                                        self._closeTerminal,
                                                        terminal,
                                                        checkbox ) )

                    self.terminals[ 'nativ_' + platform ] = terminal

                else:
                    logging.debug( 'no native compile-host for platform=%s',
                                   platform )
                    checkbox.setEnabled( False )
                    checkbox.hide()         # skip non-working platforms

            except KeyError:
                logging.error( "No native compile-host for platform=%s",
                               platform )
                return False


        for platform in xcmpPlatforms:
            checkbox = QCheckBox( platform )
            compileHost = CrossCompilation.getCrossCompileHost(platform)
            xcmp = 'Cross-compile for "%s" on "%s"' % ( platform, compileHost )
            checkbox.setToolTip( xcmp )
            checkbox.setChecked( platform in defaultXcmp )
            checkbox.stateChanged.connect( self._onPlatformSelectionChange )

            self.platformCBs_xcmp[ platform ] = checkbox
            self.platformCBs_xcmpLayout.addWidget( checkbox )

            if remoteCompilation or compileHost == localHostname:
                checkbox.setEnabled( True )

            else:
                checkbox.setEnabled( False )
                checkbox.setChecked( False )
                if projectOnLocaldisk:
                    checkbox.setToolTip( onLocaldiskToolTip )

                elif not sshPossible:
                    checkbox.setToolTip( sshToolTip )

            try:
                compileHost = CrossCompilation.getCrossCompileHost( platform )

                if compileHost:
                    logging.debug( 'cross-compile host for platform=%s: %s',
                                   platform, compileHost )

                    fullPlatformString = Platforms.getFullPlatformString(platform)
                    infoText = 'Console output for %s (%s)' % ( platform, fullPlatformString )
                    terminal = TerminalWidget.TerminalWidget( False, parent=self.multiTermWidget )
                    terminal.setHostname( compileHost )
                    terminal.setToolTip( infoText )
                    terminal.setWindowTitle(infoText)

                    terminal.isNative = False

                    terminal.hostChanged.connect( functools.partial(
                                                        self._onHostChange,
                                                        terminal ) )

                    terminal.closeRequest.connect( functools.partial(
                                                        self._closeTerminal,
                                                        terminal,
                                                        checkbox ) )

                    self.terminals[ 'xcomp_' + platform ] = terminal

                else:
                    logging.debug( 'no cross-compile host for platform=%s',
                                   platform )
                    checkbox.setEnabled( False )
                    checkbox.hide()         # skip non-working platforms

            except KeyError:
                logging.error( "No cross-compile host for platform=%s",
                               platform )
                return False

            self.terminals[ 'xcomp_' + platform ] = terminal


        # do this once to get initial grid configuration right
        # (localhost + platform terminals)

        self._onPlatformSelectionChange()

        self.externalTools = ExternalToolsWidget.ExternalToolsWidget( self.model, self.window )

        self.model.updatesAvailable.connect( self.externalTools.showUpdateIndicator )

        # build options in right pane
        self.rightPaneLayout.setContentsMargins( 0, 0, 0, 0 )
        self.platformCBs_natWidget.setLayout( self.platformCBs_natLayout )
        self.platformCBs_xcmpWidget.setLayout( self.platformCBs_xcmpLayout )
        self.rightPaneWidget.setLayout( self.rightPaneLayout )
        self.rightPaneLayout.addWidget( self.externalTools )
        self.rightPaneLayout.addWidget( self.platformCBs_natWidget )
        self.rightPaneLayout.addWidget( self.platformCBs_xcmpWidget )
        self.rightPaneLayout.addWidget( self.optionsWidget )


        self.console.localCommand.connect( self._onLocalShellInput )
        self.console.remoteCommand.connect( self._onRemoteShellInput )

        self.controlsLayout.addWidget( self.metaInfo )
        self.controlsLayout.addWidget( self.console )

        # self.terminalWidget.setLayout( self.terminalLayout )
        self.controlsWidget.setLayout( self.controlsLayout )
        self.controlsLayout.setContentsMargins( 0, 0, 0, 0 )

        self.taskButtons.clean.connect( self.clean )
        self.taskButtons.build.connect( self.build )
        self.taskButtons.proxyInstall.connect( self.proxyInstall )
        self.taskButtons.globalInstall.connect(self.globalInstall)
        self.taskButtons.test.connect( self.test )
        self.taskButtons.quit.connect( self.quit )

        self.menuBar.clean.connect( self.clean )
        self.menuBar.build.connect( self.build )
        self.menuBar.proxyInstall.connect( self.proxyInstall )
        self.menuBar.globalInstall.connect(self.globalInstall)
        self.menuBar.test.connect( self.test )


        try:
            Any.requireIsDir( self.projectRoot )
            FastScript.changeDirectory( self.projectRoot  )
            BuildSystemTools.requireTopLevelDir()
            self.openPackage( self.projectRoot )

        except ( AssertionError, OSError, RuntimeError ):
            self.projectRoot = None
            self.taskButtons.setEnabled( False )


        # main window configuration
        self.mainLayout.setColumnStretch( 0, 5 )
        self.mainLayout.addWidget( self.multiTermWidget,  0, 0 )
        self.mainLayout.addWidget( self.rightPaneWidget, 0, 1 )
        self.mainLayout.addWidget( self.controlsWidget,  1, 0 )
        self.mainLayout.addWidget( self.taskButtons,   1, 1 )
        self.mainWidget.setLayout( self.mainLayout )

        screen = QDesktopWidget().availableGeometry()

        self.window.setWindowIcon( IconProvider.getIcon( 'ToolBOS' ) )
        self.window.setWindowTitle( 'BST.py (zen build mode)' )
        self.window.setMenuBar( self.menuBar )
        self.window.setCentralWidget( self.mainWidget )
        self.window.resize( screen.width() / 5 * 4, screen.height() / 5 * 4 )
        self.window.move( screen.center() - self.window.rect().center() )
        self.window.show()

        self.menuBar.openPackage.connect( self.openPackage )
        self.menuBar.quit.connect( self.quit )

        if not self.projectRoot:
            self.menuBar.fileOpen()

        self.app.aboutToQuit.connect( self.quit )

        return self.app.exec_()


    def openPackage( self, topLevelDir ):
        topLevelDir = str(topLevelDir)
        oldcwd      = os.getcwd()

        try:
            Any.requireIsTextNonEmpty( topLevelDir )
            FastScript.changeDirectory( topLevelDir )
            BuildSystemTools.requireTopLevelDir()
        except ( AssertionError, OSError, RuntimeError ) as details:
            FastScript.changeDirectory( oldcwd )
            logging.error( details )

            QMessageBox().critical( self.window, "Error", str(details), "OK" )
            return

        logging.debug( 'opening package: %s', topLevelDir )

        try:
            self.model.open( topLevelDir )
            self.projectRoot = topLevelDir

        except ( NameError, SyntaxError, ValueError ) as details:
            logging.error( 'unable to read-in pkgInfo.py:' )
            logging.error( details )
            return

        self.taskButtons.setEnabled( True )

        for terminal in self.terminals.values():
            terminal.setPath( topLevelDir )
            terminal.clear()

            self._runDependencyCheck( terminal )


    def proxyInstall( self ):
        FastScript.setEnv( 'MAKEFILE_FASTINSTALL', 'TRUE' )

        if self.optionsWidget.getVerboseValue():
            command = 'BST.py -vx'
        else:
            command = 'BST.py -x'

        self._focusLocalTerminal()
        self._execProgram( self.terminals[ 'localhost' ], command )


    def test( self ):
        if self.optionsWidget.getVerboseValue():
            command = 'BST.py -vt'
        else:
            command = 'BST.py -t'

        self.console.addCommandToHistory_remote( command )
        self._focusRemoteTerminals()
        self._execProgramParallel( command, nativeOnly=True )


    def _closeTerminal( self, terminal, checkbox ):
        terminal.hide()
        self._onPlatformSelectionChange()

        checkbox.setChecked( False )


    def _disableButtons( self ):
        self.taskButtons.setEnabled( False )
        self.console.setEnabled( False )
        self.optionsWidget.setEnabled( False )

        for checkbox in list( self.platformCBs_nat.values() ) + \
                        list( self.platformCBs_xcmp.values() ):

            if checkbox.isEnabled():
                self.enabledCBs.append( checkbox )
                checkbox.setEnabled( False )


    def _enableButtons( self ):
        self.taskButtons.setEnabled( True )
        self.console.setEnabled( True )
        self.optionsWidget.setEnabled( True )

        for checkbox in self.enabledCBs:
            checkbox.setEnabled( True )


    def _execProgram( self, terminal, command, showCmd=None ):
        Any.requireIsTextNonEmpty( command )

        self.console.clear()

        if not showCmd:
            showCmd = command

        terminal.setCommand( command, showCmd )

        procExecutor = terminal.setup( )
        procExecutor.started.connect( lambda: self._onProgramStarted( ) )
        procExecutor.finished.connect( lambda: self._onProgramFinished( ) )

        terminal.run()

        # return reference so that the caller may also connect to signals
        return procExecutor


    def _execProgramParallel( self, command, showCmd=None, nativeOnly=False ):
        """
            Launches the given command in parallel in each terminal.
        """
        Any.requireIsTextNonEmpty( command )

        self.console.clear()

        if not showCmd:
            showCmd = command

        if command.startswith( 'cd' ):
            path = shlex.split( command )[1]

            for platform, terminal in self.terminals.items():
                if platform != 'localhost' and terminal.isVisible():
                    terminal.setPath( path )
                    terminal.writeCommand( 'cd %s' % path )

        else:
            for platform, terminal in self.terminals.items():
                if platform != 'localhost' and terminal.isVisible():

                    if ( nativeOnly and terminal.isNative ) or not nativeOnly:
                        self._execProgram( terminal, command, showCmd )
                    else:
                        terminal.writeText( '[Skipped on cross-compilation host]' )


    def _execProgramSequential( self, command, showCmd=None ):
        """
            Launches the given command one after the other in each
            terminal.

            total execution time = command execution time *
                                   number of enabled platforms
        """
        Any.requireIsTextNonEmpty( command )
        self.console.clear()

        if not showCmd:
            showCmd = command


        localhostTerminal = self.terminals[ 'localhost' ]


        # process in exact visual appearance sequence (starting at top-left),
        # therefore querying the terminal list from MultiTermWidget instead
        # of iterating over self.terminals

        for terminal in self.multiTermWidget.getTerminals():
            Any.requireIsInstance( terminal, TerminalWidget.TerminalWidget )

            platform = None

            for candPlatform, candTerminal in self.terminals.items():
                Any.requireIsTextNonEmpty( candPlatform )
                Any.requireIsInstance( candTerminal, TerminalWidget.TerminalWidget )

                if terminal == candTerminal:
                    platform = candPlatform

                    # remove "xcomp_" or "nativ_" prefixes
                    platform = platform.replace( 'xcomp_', '' )
                    platform = platform.replace( 'nativ_', '' )

            Any.requireIsTextNonEmpty( platform )

            finalCommand = command.replace( '<MAKEFILE_PLATFORM>', platform )
            finalShowCmd = showCmd.replace( '<MAKEFILE_PLATFORM>', platform )

            if terminal != localhostTerminal:
                self._seqTasks.append( ( terminal, finalCommand, finalShowCmd ) )


        # kick-off the full queue
        self._seqTasksRun.emit()


    def _focusLocalTerminal( self ):
        for platform, terminal in self.terminals.items():
            if platform == 'localhost':
                terminal.setEnabled( True )
            else:
                terminal.setEnabled( False )


    def _focusRemoteTerminals( self ):
        for platform, terminal in self.terminals.items():
            if platform == 'localhost':
                terminal.setEnabled( False )
            else:
                terminal.setEnabled( True )


    def _onDependencyCheckFinished( self, terminal, output ):
        Any.requireIsInstance( terminal, TerminalWidget.TerminalWidget )
        Any.requireIsInstance( output, QByteArray )

        missingDeps = []
        utf8Output  = output.data()
        strOutput   = utf8Output.decode( 'utf-8' )
        lines       = strOutput.splitlines()

        for line in lines:
            if ProjectProperties.isURL( line ):
                missingDeps.append( line )
            else:
                logging.debug( 'unexpected output: %s', line )


        self._depCheckers[ terminal ] = None

        if missingDeps:
            logging.debug( 'found missing deps: %s', missingDeps )
            self._reportMissingDependencies( terminal, missingDeps )


    def _onHostChange( self, terminal, hostname ):
        Any.requireIsInstance( terminal, TerminalWidget.TerminalWidget )
        Any.requireIsText( hostname )

        logging.debug( 'terminal %s: changed to host "%s"', terminal, hostname )


        # remove terminal from existing depCheckers so that it gets
        # checked again by _runDependencyCheck()
        del self._depCheckers[ terminal ]


        self._runDependencyCheck( terminal )


    def _onLocalShellInput( self, command ):
        if not command:
            # f.i. just RETURN pressed
            terminal = self.terminals[ 'localhost' ]
            terminal.writeCommand( '' )
            terminal.setColor( 'grey' )

        elif command.startswith( 'cd' ):
            # 'cd' is not a command but a shell built-in,
            # f.i. there is no /bin/cd executable

            path = shlex.split( command )[1]

            # show original path typed by user
            terminal = self.terminals[ 'localhost' ]
            terminal.writeCommand( 'cd %s' % path )

            # proceed with full path
            path = os.path.expanduser( path )

            if os.path.exists( path ):
                terminal.setColor( 'green' )
                terminal.setPath( path )
                FastScript.changeDirectory( path )
            else:
                terminal.setColor( 'red' )
                terminal.writeText( '%s: No such directory' % path )

        elif command == 'exit' or command == 'quit':
            self.quit()

        else:
            # execute real executable
            self._focusLocalTerminal()
            self._execProgram( self.terminals[ 'localhost' ], command )


    def _onPlatformSelectionChange( self ):

        # if no platform is selected, disable the 'Build' button
        anySelected = False

        self.multiTermWidget.clear()
        self.multiTermWidget.addTerminal( self.terminals[ 'localhost' ] )


        for platform, checkbox in self.platformCBs_nat.items():

            try:
                terminal = self.terminals[ 'nativ_' + platform ]

                if checkbox.isChecked():
                    self.multiTermWidget.addTerminal( terminal )
                    anySelected = True

            except KeyError:
                pass


        for platform, checkbox in self.platformCBs_xcmp.items():

            try:
                terminal = self.terminals[ 'xcomp_' + platform ]

                if checkbox.isChecked():
                    self.multiTermWidget.addTerminal( terminal )
                    anySelected = True

            except KeyError:
                pass


        if self.projectRoot:
            self.taskButtons.setEnabled( anySelected, 'build' )


    def _onProblemIndicatorPressed( self, hostname, missingDeps ):
        Any.requireIsTextNonEmpty( hostname )
        Any.requireIsListNonEmpty( missingDeps )

        title = 'Missing dependencies'
        msg   = "The following packages are missing on host '" + \
                hostname + "'. Build and/or execution might fail!\n\n"

        for packageURL in missingDeps:
            msg += packageURL + "\n"

        dialog = QMessageBox()
        dialog.warning( self.parent(), title, msg, QMessageBox.Ok )
        dialog.show()


    def _onProgramStarted( self ):
        self._programCounter_increment()

        for terminal in self.terminals.values():
            terminal.setReadOnly( True )


    def _onProgramFinished( self ):
        self._programCounter_decrement()
        self.console.setFocus()


    def _onRemoteShellInput( self, command ):
        if not command:
            # f.i. just RETURN pressed
            for terminal in self.visibleRemoteTerminals:
                terminal.writeCommand( '' )
                terminal.setColor( 'grey' )

        elif command.startswith( 'cd' ):
            # 'cd' is not a command but a shell built-in,
            # f.i. there is no /bin/cd executable

            try:
                path = shlex.split( command )[1]
            except IndexError:
                # no directory specified, falling back to home directory
                path = os.path.expanduser( '~' )

            # show original path typed by user
            for terminal in self.visibleRemoteTerminals:
                terminal.writeCommand( 'cd %s' % path )
                terminal.setColor( 'green' )       # but unsure if exists
                terminal.setPath( path )

        elif command == 'exit' or command == 'quit':
            self.quit()

        else:
            # execute real executable
            self._focusRemoteTerminals()
            self._execProgramParallel( command )


    def _onSeqTasksRun( self ):
        count = len( self._seqTasks )

        logging.debug( 'processing %d sequential task(s)', count )

        if count == 0:
            self._seqTasksFinished.emit()
            return


        terminal, command, showCmd = self._seqTasks.pop( 0 )

        Any.requireIsInstance( terminal, TerminalWidget.TerminalWidget )
        Any.requireIsTextNonEmpty( command )
        Any.requireIsTextNonEmpty( showCmd )

        procExecutor = self._execProgram( terminal, command, showCmd )
        procExecutor.finished.connect( self._onSeqTasksRun )


    def _onSeqTasksFinished( self ):
        logging.debug( 'processing sequential tasks finished' )


    def _onUpdatesAvailable( self ):
        self._extTools.showUpdateIndicator()


    def _programCounter_increment( self, ):
        self.lock.acquire()
        self.runningProcesses += 1
        logging.debug( 'running processes: %d', self.runningProcesses )
        self.lock.release()

        self._disableButtons()


    def _programCounter_decrement( self, ):
        self.lock.acquire()

        self.runningProcesses -= 1
        logging.debug( 'running processes: %d', self.runningProcesses )

        if self.runningProcesses <= 0:
            self._enableButtons()

            # enable all terminals for interactive usability
            for terminal in self.terminals.values():
                terminal.setEnabled( True )

        self.lock.release()


    def _reportMissingDependencies( self, terminal, missingDeps ):
        Any.requireIsInstance( terminal, TerminalWidget.TerminalWidget )
        Any.requireIsList( missingDeps )

        count = len( missingDeps )

        if count == 0:
            # all dependencies installed
            return

        elif count == 1:
            tmp = missingDeps[0]
            msg = 'Dependency "%s" not installed, build or execution might fail!' % tmp

        elif count < 4:
            tmp = '"' + '", "'.join( missingDeps ) + '"'
            msg = 'Dependencies %s not installed, build or execution might fail!' % tmp

        else:
            tmp = '"' + '", "'.join( missingDeps[0:3] ) + '"'
            msg = 'Dependencies %s (and others) not installed, build or execution might fail!' % tmp


        logging.debug( '%s: %s', terminal.hostname, msg )

        onIndicatorPress = lambda: self._onProblemIndicatorPressed( terminal.hostname,
                                                                    missingDeps )

        indicator = terminal.problemIndicator
        indicator.pressed.connect( onIndicatorPress )
        indicator.setIcon( IconProvider.getIcon( 'dialog-warning' ) )
        indicator.setToolTip( msg )
        indicator.show()


    def _runDependencyCheck( self, terminal ):
        Any.requireIsInstance( terminal, TerminalWidget.TerminalWidget )

        host = terminal.hostname
        path = terminal.path


        if not terminal in self._depCheckers:
            logging.debug( 'checking if all dependencies are installed (host=%s, path=%s)',
                           host, path )

            depChecker = DependencyChecker.DependencyChecker( host, path )
            self._depCheckers[ terminal ] = depChecker

            onFinish   = functools.partial( self._onDependencyCheckFinished, terminal )
            depChecker.finished.connect( onFinish )
            depChecker.run()


# EOF
