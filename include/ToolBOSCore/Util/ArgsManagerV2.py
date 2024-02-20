# -*- coding: utf-8 -*-
#
#  tiny decorator for Python's argparse class
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


import argparse
import logging
import sys
import textwrap

from ToolBOSCore.Settings import AppConfig, ToolBOSConf
from ToolBOSCore.Util     import Any, FastScript


class ArgsManager( argparse.ArgumentParser ):
    """
        Tiny decorator for Python's argparse class, customizations:

          * always have "-v|--verbose" option defined which sets
            the debug level in case the option was given on
            commandline (btw. it also considers VERBOSE=TRUE in
            the environment)

          * show examples

          * show bugtracker URL at the end of the help message
    """
    def __init__( self, description ):
        Any.requireIsTextNonEmpty( description )

        wrappedDescr = '\n'.join( textwrap.wrap( description ) )

        super( ArgsManager, self ).__init__()

        self.description     = wrappedDescr
        self.epilog          = ''
        self.formatter_class = argparse.RawDescriptionHelpFormatter

        self._allowUnknown   = False
        self._config         = None
        self._examples       = []
        self._supportInfo    = None
        self._unhandled      = None

        # provide a camel-case alternative for consistent codestyle
        self.addArgument     = self.add_argument


    def addExample( self, example ):
        Any.requireIsTextNonEmpty( example )

        self._examples.append( example )


    def getUnhandledArguments( self ):
        Any.requireMsg( self._allowUnknown,
                        'Please first call setAllowUnknownArgs(True)!' )

        return self._unhandled


    def run( self, argv=None ):
        # preparation
        self._addVerboseOption()
        self._addVersionOption()
        self._setBugtrackerURL()
        self._setEpilog()

        # commandline parsing
        self._handleVersionOption()
        self._main( argv )

        # post-processing
        self._setDebugLevel()

        return self._result


    def setAllowUnknownArgs( self, boolean ):
        """
            By default an error message will be displayed when an unknown
            option is passed. With setAllowUnknownArgs( True ) you allow
            such options, e.g. for later passing to another program.
        """
        Any.requireIsBool( boolean )

        self._allowUnknown = boolean


    def setAppConfig( self, config ):
        """
            You may provide an 'AppConfig' instance that the parser shall
            use to obtain the bugtrack URL.

            If omitted, the global ToolBOSCore AppConfig-instance is used.
        """
        Any.requireIsInstance( config, AppConfig.AppConfig )

        self._config = config


    def _addVerboseOption( self ):
        self.add_argument( '-v', '--verbose',
                           action='store_true',
                           help='show debug messages' )


    def _addVersionOption( self ):
        self.add_argument( '-V', '--version',
                           action='store_true',
                           help='show version info and exit' )


    def _main( self, argv=None ):
        if self._allowUnknown:
            self._result, self._unhandled = self.parse_known_args( argv )
        else:
            self._result = self.parse_args( argv )


    def _handleVersionOption( self ):
        args = sys.argv

        if '--version' in args or '-V' in args:
            self._showVersionInfo()
            raise SystemExit()


    def _setBugtrackerURL( self ):
        config = self._config if self._config else ToolBOSConf.getGlobalToolBOSConf()

        try:
            bugtrackName      = config.getConfigOption( 'bugtrackName' )
            bugtrackURL       = config.getConfigOption( 'bugtrackURL' )
            self._supportInfo = f'\nPlease report bugs on {bugtrackName} ({bugtrackURL}).'

        except AttributeError:
            # This happens within ToolBOS-Setup.py: In a brand-new user
            # environment TOOLBOSCORE_ROOT is not defined, yet.
            # Hence we are not able to determine the location of the
            # fallback ToolBOS.conf.
            #
            # In such case do not show the bugtrackURL.
            pass

        except KeyError:
            # In CIA the CIA-Start.sh script sets TOOLBOSCORE_ROOT to point
            # into the new SIT location which does not exist, yet.
            # In this case, its etc/ToolBOS.conf won't be found.
            #
            # The same applies while debugging incomplete setups.
            # Fine to not show bugtrackURL in such cornercases, too.
            pass


    def _setDebugLevel( self ):
        """
            Free scripts from redundant verbose-flag handling.

            Mind to set VERBOSE=TRUE within this process, so that
            child processes (incl. CMake) operate in verbose mode.
        """
        if self._result.verbose or FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( logging.DEBUG )
            FastScript.setEnv( 'VERBOSE', 'TRUE' )
        else:
            Any.setDebugLevel( logging.INFO )


    def _setEpilog( self ):
        """
            Assembles footer-information shown below the options in the
            help dialog. Depends on previous calls to addExample() and
            _setBugtrackerURL().
        """
        if self._examples:
            self.epilog += 'examples:\n'

        for example in self._examples:
            self.epilog += '  %s\n' % example

        if self._examples and self._supportInfo:
            self.epilog += '\n'

        if self._supportInfo:
            self.epilog += self._supportInfo


    def _showVersionInfo( self ):
        """
            Retrieves the program's filepath, locates the package's
            top-level-directory, and makes use of PackageDetector to get
            version numbers, patchlevels, and Git commit IDs (if possible).

            Then these information are displayed on the console.
        """
        from ToolBOSCore.Packages import AppDetector, ProjectProperties

        scriptPath  = sys.argv[0]
        Any.requireIsTextNonEmpty( scriptPath )

        projectRoot = ProjectProperties.detectTopLevelDir( scriptPath )
        Any.requireIsDirNonEmpty( projectRoot )

        print( AppDetector.getAppVersion( projectRoot ) )


# EOF
