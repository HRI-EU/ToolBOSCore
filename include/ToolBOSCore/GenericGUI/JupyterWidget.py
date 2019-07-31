#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  IPython console widget with Jupyter kernel
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
from PyQt5.QtCore import QMargins, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout

try:
    from qtconsole.rich_jupyter_widget import RichJupyterWidget
    from qtconsole.inprocess           import QtInProcessKernelManager


    class JupyterWidget( QWidget ):

        _defaultWidth  = 900
        _defaultHeight = 450


        def __init__( self ):
            super( JupyterWidget, self ).__init__()

            self._kernel_manager = QtInProcessKernelManager()
            self._kernel_manager.start_kernel( show_banner=True )

            self._kernel_client = self._kernel_manager.client()
            self._kernel_client.start_channels()

            self._kernel = self._kernel_manager.kernel
            self._kernel.gui = 'qt4'

            self._console = RichJupyterWidget()
            self._console.kernel_manager = self._kernel_manager
            self._console.kernel_client  = self._kernel_client

            self._layout = QHBoxLayout()
            self._layout.addWidget( self._console )
            self._layout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )

            self.setLayout( self._layout )

            self.resize( self._defaultWidth, self._defaultHeight )

        def push( self, name, value ):
            self._kernel.shell.push( { name: value } )

except ImportError:
    from PyQt5.QtWidgets import QLabel

    class JupyterWidget( QLabel ):

        def __init__( self ):
            super( JupyterWidget, self ).__init__()
            self.resize( 400, 200 )
            self.setAlignment( Qt.AlignCenter )
            self.setText( '''No suitable Jupyter Qt console installed.

The required packages can be installed with pip or conda:
        $ pip install qtconsole
        $ conda install qtconsole''' )
            self.setWindowTitle( 'Error' )

        def push( self, *args ):
            pass



# EOF
