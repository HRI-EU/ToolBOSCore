# -*- coding: utf-8 -*-
#
#  fundamental settings / config options for ToolBOS SDK
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

from ToolBOSCore.Util import Any, FastScript
from ToolBOSCore.Settings import AppConfig


# global singleton for easy use
_cache = None

packageName    = 'ToolBOSCore'
packageVersion = '4.3'
canonicalPath  = 'DevelopmentTools/ToolBOSCore/4.3'

settingsFile   = 'ToolBOS.conf'


class ToolBOSConf( AppConfig.AppConfig ):

    def __init__( self ):

        appName    = 'ToolBOS'
        tcRoot     = FastScript.getEnv( 'TOOLBOSCORE_ROOT' )
        defaultDir = os.path.join( tcRoot, 'etc' )
        userDir    = os.path.join( os.path.expanduser( '~' ), '.HRI', appName )
        addFiles   = []


        # integrate settings from other ToolBOS and user specified packages, if present

        mwRoot           = FastScript.getEnv( 'TOOLBOSMIDDLEWARE_ROOT' )
        toolBOSConfPaths = FastScript.getEnv( 'TOOLBOSCONF_PATH' )

        if mwRoot:
            Any.requireIsDirNonEmpty( mwRoot )
            mwFile = os.path.join( mwRoot, 'etc', 'ToolBOS-Middleware.conf' )

            if os.path.exists( mwFile ):
                logging.debug( 'found ToolBOS Middleware in %s', mwRoot )
                addFiles.append( mwFile )

        if toolBOSConfPaths:
            Any.requireIsText( toolBOSConfPaths )
            toolBOSConfDirs = toolBOSConfPaths.split( ':' )

            for path in toolBOSConfDirs:
                filePath = os.path.join( path, 'ToolBOS.conf' )

                if os.path.exists( filePath ):
                    logging.debug( 'found %s', filePath )
                    addFiles.append( filePath )

        if not addFiles:
            addFiles = None

        super( ToolBOSConf, self ).__init__( appName, defaultDir, userDir,
                                             addFiles=addFiles )


def getGlobalToolBOSConf():
    """
        Return a ToolBOSConf singleton, with lazy loading.
    """
    global _cache

    if _cache is None:
        logging.debug( 'populating ToolBOS.conf cache' )
        _cache = ToolBOSConf()

    return _cache


def getConfigOption( name ):
    cache = getGlobalToolBOSConf()

    Any.requireIsTextNonEmpty( name )
    Any.requireIsInstance( cache, ToolBOSConf )

    return cache.getConfigOption( name )


# EOF
