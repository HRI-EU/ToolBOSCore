#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Checks if all package dependencies are present
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


from PyQt5.QtCore import QByteArray, QObject
from PyQt5.QtCore import pyqtSignal

from ToolBOSCore.GenericGUI import ProcessExecutor
from ToolBOSCore.Util       import Any


class DependencyChecker( QObject, object ):

    finished = pyqtSignal( QByteArray )

    def __del__(self):
        if self._process:
            self._process = None


    def __init__( self, hostname, topLevelDir ):
        QObject.__init__( self )

        Any.requireIsTextNonEmpty( hostname )
        Any.requireIsTextNonEmpty( topLevelDir )

        self._hostname    = hostname
        self._output      = QByteArray()
        self._process     = None
        self._topLevelDir = topLevelDir


    def run( self ):
        cmd = 'ListDependencies.py --missing-only .'

        self._process = ProcessExecutor.ProcessExecutor()
        self._process.newStdOut.connect( self._onOutput )
        self._process.finished.connect( self._onFinish )
        self._process.setCommand( cmd )
        self._process.setHostname( self._hostname )
        self._process.setWorkingDirectory( self._topLevelDir )
        self._process.start()


    def _onFinish( self ):
        self._process.terminate()           # should be already dead
        self._process = None

        self.finished.emit( self._output )


    def _onOutput( self, data ):
        self._output.append( data )


# EOF
