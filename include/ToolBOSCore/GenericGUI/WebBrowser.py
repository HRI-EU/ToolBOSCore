#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  simple browser widget
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

from PyQt5.QtCore             import QUrl, Qt
from PyQt5.QtNetwork          import QNetworkReply, QNetworkProxy
from PyQt5.QtWidgets          import QApplication, QWidget, QLabel, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from ToolBOSCore.Settings import ToolBOSConf
from ToolBOSCore.Util     import Any


class WebPage( QWebEnginePage ):

    def certificateError( self, e ):
        logging.debug( 'ignoring SSL errors for now' )

        return True


class WebBrowser( QDialog ):

    def __init__( self, windowTitle, parent=None ):
        super( WebBrowser, self ).__init__( parent=parent )

        screen = QApplication.desktop().screenGeometry()

        self._setupProxy()

        self._page = WebPage()

        self._browser = QWebEngineView( parent=self )
        self._browser.setPage( self._page )
        self._browser.resize( screen.width( ) / 4 * 3,
                              screen.height() / 4 * 3 )

        self._browser.setWindowTitle( windowTitle )


    def open( self, url ):
        logging.info( 'opening %s', url )

        self._page.load( QUrl( url ) )

        self.show()


    def _setupProxy( self ):
        # TODO: move proxy settings to ToolBOS.conf

        proxy = QNetworkProxy( )
        proxy.setType( QNetworkProxy.HttpProxy )
        proxy.setHostName( 'hri-proxy.honda-ri.de' )
        proxy.setPort( 3128 )

        QNetworkProxy.setApplicationProxy( proxy )


if __name__ == '__main__':
    app    = QApplication( [] )
    app.setStyle( 'fusion' )

    browser = WebBrowser( 'Test' )
    browser.open( 'https://www.honda-ri.de' )

    app.exec_()


# EOF
