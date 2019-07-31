# -*- coding: utf-8 -*-
#
#  Decorator for QProcess which uses SSH to execute a process on a remote host
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
import shlex
import socket

from PyQt5.QtCore import pyqtSignal, QByteArray, QObject, QProcess,\
                         QProcessEnvironment

from ToolBOSCore.Util import Any


class ProcessExecutor( QObject, object ):

    started   = pyqtSignal()
    finished  = pyqtSignal( int )
    newStdOut = pyqtSignal( QByteArray )
    newStdErr = pyqtSignal( QByteArray )


    def __init__( self ):
        super( ProcessExecutor, self ).__init__()

        self._env        = QProcessEnvironment.systemEnvironment()
        self._origCmd    = None
        self._finalExe   = None
        self._finalArgs  = []
        self._hostname   = 'localhost'
        self._localHost  = socket.gethostname()
        self._process    = QProcess()
        self._detached   = False
        self._withX11    = False
        self._workingDir = None

        self._process.started.connect( self.started.emit )
        self._process.finished.connect( self.finished.emit )
        self._process.readyReadStandardOutput.connect( self._onNewStdOut )
        self._process.readyReadStandardError.connect( self._onNewStdErr )


    def __del__( self ):
        self._process.terminate()
        self._process.waitForFinished( -1 )      # -1: block if necessary


    def setCommand( self, cmd ):
        cmd = cmd.strip()
        Any.requireIsTextNonEmpty( cmd )

        self._origCmd = cmd


    def setDetached( self, detached ):
        """
            Set to True if the process shall continue to run after the
            current process terminates, effectively turning the executed
            process into a daemon.
        """
        Any.requireIsBool( detached )

        self._detached = detached


    def setEnv( self, name, value ):
        Any.requireIsTextNonEmpty( name )
        Any.requireIsTextNonEmpty( value )
        Any.requireIsInstance( self._env, QProcessEnvironment )

        logging.debug( 'export %s=%s', name, value )
        self._env.insert( name, value )


    def setHostname( self, hostname ):
        hostname = hostname.strip()
        Any.requireIsTextNonEmpty( hostname )

        self._hostname = hostname


    def setWorkingDirectory( self, workingDir ):
        Any.requireIsTextNonEmpty( workingDir )

        self._workingDir = workingDir


    def setWithX11Tunnel( self, withX11 ):
        """
            Use SSH's X11 forwarding when executing commands on remote
            hosts?
        """
        Any.requireIsBool( withX11 )

        self._withX11 = withX11


    def start( self ):
        self._assembleCommandLine()
        self._process.setProcessEnvironment( self._env )
        self._start()


    def state( self ):
        return self._process.state()


    def terminate( self ):
        self._process.terminate()


    def unsetEnv( self, name ):
        Any.requireIsTextNonEmpty( name )
        Any.requireIsInstance( self._env, QProcessEnvironment )

        self._env.remove( name )


    def waitForFinished( self, msecs=0 ):
        self._process.waitForFinished( msecs )


    def waitForStarted( self, msecs=0 ):
        self._process.waitForStarted( msecs )


    def _assembleCommandLine( self ):
        Any.requireIsTextNonEmpty( self._origCmd )

        if self._hostname in ( self._localHost, 'localhost', '127.0.0.1', '::1' ):
            tokens          = shlex.split( self._origCmd )
            self._finalExe  = tokens[0]
            self._finalArgs = tokens[1:]

        else:
            # tunnel command via SSH to remote host
            self._finalExe  = 'ssh'
            self._finalArgs = []

            if self._withX11:
                self._finalArgs.append( '-X' )

            # disable fingerprint check to avoid interactive prompt
            # in case the hostkey has changed
            self._finalArgs.append( '-o' )
            self._finalArgs.append( 'BatchMode=yes' )
            self._finalArgs.append( '-o' )
            self._finalArgs.append( 'StrictHostKeyChecking=no' )


            # SSH's double-t option enforces allocation of Pseudo-TTY.
            # With the help of this child-processes will receive EOD upon
            # SSH connection loss or terminating. The EOD usually results
            # in the command to exit.

            self._finalArgs.append( '-t' )
            self._finalArgs.append( '-t' )


            self._finalArgs.append( self._hostname )

            if self._workingDir:
                remoteCmd = 'cd %s && %s' % ( self._workingDir, self._origCmd )
            else:
                remoteCmd = self._origCmd

            self._finalArgs.append( remoteCmd )

        Any.requireIsTextNonEmpty( self._finalExe )
        Any.requireIsList( self._finalArgs )


    def _start( self ):
        logging.debug( 'starting process (exe=%s, args=%s)',
                       self._finalExe, self._finalArgs )

        if self._workingDir:
            self._process.setWorkingDirectory( self._workingDir )

        if self._detached:
            self._process.startDetached( self._finalExe, self._finalArgs )
        else:
            self._process.start( self._finalExe, self._finalArgs )


    def _onNewStdErr( self ):
        output = self._process.readAllStandardError()

        self.newStdErr.emit( output )


    def _onNewStdOut( self ):
        output = self._process.readAllStandardOutput()

        self.newStdOut.emit( output )


def runXterm( hostname='localhost', path=None ):
    if path:
        Any.requireIsTextNonEmpty( path )
        cmd = 'xterm -geometry 150x40 -e "cd %s && /bin/bash"' % path
    else:
        cmd = 'xterm -geometry 150x40'

    process = ProcessExecutor()
    process.setCommand( cmd )
    process.setDetached( True )
    process.setWithX11Tunnel( True )

    if hostname:
        Any.requireIsTextNonEmpty( hostname )
        process.setHostname( hostname )

    process.start()


# EOF
