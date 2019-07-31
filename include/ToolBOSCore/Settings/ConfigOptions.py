# -*- coding: utf-8 -*-
#
#  fundamental settings / config options
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

from ToolBOSCore.Util import Any
from ToolBOSCore.Util import FastScript


class ConfigOptions( object ):

    def __init__( self, appName , appRoot ):
        Any.requireIsTextNonEmpty( appName )
        Any.requireIsDir( appRoot )

        self._addPaths        = []
        self._appName         = appName
        self._appRoot         = appRoot
        self._settingsFile    = appName + '.conf'

        defaultConfDir        = os.path.join( self._appRoot, 'etc' )
        userConfDir           = os.path.join( os.path.expanduser( '~' ), '.HRI', self._appName )
        cwdConfDir            = os.getcwd()
        machineConfDir        = '/etc'

        self._defaultConfPath = os.path.join( defaultConfDir, self._settingsFile )
        self._userConfPath    = os.path.join( userConfDir,    self._settingsFile )
        self._machineConfPath = os.path.join( machineConfDir, self._settingsFile )
        self._cwdConfPath     = os.path.join( cwdConfDir,     self._settingsFile )


    def addPath( self, path ):
        Any.requireIsTextNonEmpty( path )

        filePath = os.path.join( path, self._settingsFile )
        logging.debug( 'registering add. config file: %s', filePath )

        self._addPaths.append( filePath )


    def getConfigOptions( self ):
        """
            Returns a dict with all config options and their values.

            The master-list of available config options is defined in
            etc/ToolBOS.conf (the fallback list shipped with ToolBOS SDK).

            To search in non-standard locations provide a list 'addPaths'.
            Its path entries will be searched right after ./ToolBOS.conf.
        """
        allSymbols = {}

        # do in reverse order (starting from default), and update step-by-step
        # with the higher-priority settings
        order = self._getEvalOrder( )
        order.reverse()

        for fileName in order:
            try:
                fileSymbols = FastScript.execFile( fileName )
                logging.debug( 'evaluating %s', fileName )
            except( AssertionError, IOError, OSError ):
                fileSymbols = {}

            allSymbols.update( fileSymbols )

        result = {}
        for key, value in allSymbols.items():
            if Any.isTextNonEmpty( key ) and not Any.isCallable( value ):
                result[ key ] = value

        return result


    def getConfigOption( self, varName ):
        """
            This function searches for a variable 'varName' in the ToolBOS
            configfile(s) named 'ToolBOS.conf'.

            Such configfiles are searched by priority:

              1) within the current working directory
              2) entries from additional search-paths if provided
              3) within ~/.HRI (user's home directory)
              4) within /etc (set by the system administrator)
              5) within the ToolBOSCore package itself (default / fallback)

            To search in non-standard locations provide a list 'addPaths'.
            Its path entries will be searched right after ./ToolBOS.conf.

            If none of the files contains the specified variable,
            a key error will be thrown.
        """
        Any.requireIsTextNonEmpty( varName )

        for fileName in self._getEvalOrder( ):
            try:
                result = self._getConfigOptionFromFile( varName, fileName )

                return result

            except( AssertionError, IOError, KeyError, OSError ):
                pass

        # nowhere found
        raise KeyError( "Config option '%s' is nowhere set." % varName )


    def getUserConfigOptions( self ):
        """
            Returns a dict with the settings from the user's configfile (if any).

            Unlike getConfigOptions() it does not look-up all the other files
            like in the current working directory or the system-wide or default
            configs.
        """
        # read current settings (if any)
        try:
            config = FastScript.execFile( self._userConfPath )
        except IOError as e:                     # no such file
            logging.info( e )
            config = {}

        return config


    def setUserConfigOption( self, varName, value ):
        """
            Write a user-preference to the user's configfile.

            Note: 'key' must be a string, value should be a string or iterable.

            Use delConfigOption() to remove a setting.
        """
        Any.requireIsTextNonEmpty( varName )
        Any.requireMsg( varName[0].isalpha(),
                        'varName parameter must start with a letter' )

        # update setting
        config = self.getUserConfigOptions()
        config[ varName ] = value
        logging.debug( 'setting config option: %s=%s', varName, str(value) )

        self._setUserConfigOptions( config )


    def delUserConfigOption( self, varName ):
        """
            Removes a certain config option from the user's configfile.
        """
        Any.requireIsTextNonEmpty( varName )

        # read current settings (if any)
        config = self.getUserConfigOptions()

        # remove setting
        try:
            del config[ varName ]
            logging.debug( 'deleted config option: %s', varName )

            # delete entire file if there are no settings left
            if config:
                self._setUserConfigOptions( config )
            else:
                fileName =self._userConfPath
                logging.debug( 'deleting empty configfile' )
                logging.debug( 'rm %s', fileName )
                FastScript.remove( fileName )

        except KeyError:
            logging.debug( '%s: No such user config option', varName )


    def _getConfigOptionFromFile( self, varName, fileName ):
        """
            This function attempts to find a variable 'varName' defined in
            the file 'fileName'.
        """
        Any.requireIsTextNonEmpty( varName )
        Any.requireIsFileNonEmpty( fileName )

        value = FastScript.execFile( fileName )[varName]

        return value


    def _getEvalOrder( self ):

        try:
            tmpList = [ self._cwdConfPath,
                        self._userConfPath,
                        self._machineConfPath,
                        self._defaultConfPath ]

        except OSError as e:
            logging.error( e )
            logging.error( 'Problem with current working directory detected!' )
            raise SystemExit()

        if self._addPaths:
            resultList = [ tmpList[0] ]

            for path in self._addPaths:
                resultList.append( path )

            resultList.append( tmpList[1:] )
            resultList = FastScript.flattenList( resultList )

            logging.debug( 'full list: %s', resultList )
        else:
            resultList = tmpList

        return resultList


    def _setUserConfigOptions( self, config ):
        """
            Writes the dict 'config' in ASCII yet Pythonic style to the user's
            configfile, so that it can be edited manually and read-in using
            FastScript.execFile().
        """
        from ToolBOSCore.Packages.CopyrightHeader import getCopyrightHeader

        Any.requireIsDict( config )

        content = getCopyrightHeader( 'python', 'User-preferences for ToolBOS SDK' )

        for key, value in config.items():
            if Any.isText( value ):
                value = "'%s'" % value      # write Python string, not just value

            content += '%s = %s\n\n' % ( key, str( value ) )

        content += '\n# EOF\n'

        dirName  = os.path.dirname( self._userConfPath )

        FastScript.mkdir( dirName )
        FastScript.setFileContent( self._userConfPath, content )


#EOF
