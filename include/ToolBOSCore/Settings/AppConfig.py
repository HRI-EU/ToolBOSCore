# -*- coding: utf-8 -*-
#
#  fundamental settings / application config options
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


class AppConfig( object ):

    def __init__( self, appName, defaultDir, userDir, machineDir='/etc',
                  addFiles=None ):

        Any.requireIsDirNonEmpty( defaultDir )
        Any.requireIsTextNonEmpty( machineDir )
        Any.requireIsTextNonEmpty( userDir )

        if addFiles is not None:
            Any.requireIsListNonEmpty( addFiles )

            for filePath in addFiles:
                Any.requireIsText( filePath )   # check for existence later

        fileName              = appName + '.conf'

        self._defaultFile     = os.path.join( defaultDir,  fileName )
        self._machineFile     = os.path.join( machineDir,  fileName )
        self._userFile        = os.path.join( userDir,     fileName )
        self._cwdFile         = os.path.join( os.getcwd(), fileName )
        self._addFiles        = addFiles if addFiles is not None else []

        Any.requireIsFileNonEmpty( self._defaultFile )

        self._defaultSettings = {}
        self._machineSettings = {}
        self._userSettings    = {}
        self._cwdSettings     = {}
        self._allSettings     = {}

        # load all settings into memory
        self._readFiles()


    def getConfigOption( self, name ):
        """
            This function searches for a variable 'name' within all merged
            settings.
        """
        Any.requireIsTextNonEmpty( name )

        try:
            return self._allSettings[ name ]
        except KeyError:
            raise KeyError( "Config option '%s' is nowhere set." % name )


    def getConfigOptions( self ):
        """
            Returns a dict of all settings.
        """
        return self._allSettings


    def getDefaultConfigOption( self, name ):
        """
            Returns the default value of the given config option as
            specified in the default (fallback) file.
        """
        Any.requireIsTextNonEmpty( name )

        return self._defaultSettings[ name ]


    def getNormalValue( self, name ):
        """
            Returns the value of the given config option without any
            *user* modifications.

            Hence with default we mean the values shipped by either the
            application itself or settings overridden by the machine-admin.

            Note that these are not the same as the default values.
        """
        Any.requireIsTextNonEmpty( name )

        try:
            return self._machineSettings[ name ]
        except KeyError:
            return self._defaultSettings[ name ]


    def getUserConfigOption( self, name ):
        """
            This function searches for a variable 'varName' in the user's
            custom configfile.

            Unlike getConfigOption() it does not look-up all the other files
            like in the current working directory or the system-wide or default
            configs.

            If the user has no such file or the specified variable is not
            set, a key error will be thrown.
        """
        Any.requireIsTextNonEmpty( name )

        return self._userSettings[ name ]


    def getUserConfigOptions( self ):
        """
            Returns a dict with the settings from the user's configfile (if any).

            Unlike getConfigOptions() it does not look-up all the other files
            like in the current working directory or the system-wide or default
            configs.
        """
        return self._userSettings


    def setUserConfigOption( self, name, value ):
        """
            Write a user-preference to the user's configfile.

            Note: 'name' must be a string, value should be a string or iterable.

            Use delUserConfigOption() to remove a setting.
        """
        Any.requireIsTextNonEmpty( name )
        Any.requireMsg( name[0].isalpha(),
                        'name parameter must start with a letter' )

        # update setting
        logging.debug( 'setting config option: %s=%s', name, value )
        self._userSettings[ name ] = value
        self._allSettings[  name ] = value
        self.save()


    def delUserConfigOption( self, name ):
        """
            Removes a certain config option from the user's configfile.
        """
        Any.requireIsTextNonEmpty( name )

        try:
            del self._userSettings[ name ]
            self._allSettings[ name ] = self.getNormalValue( name )

            logging.debug( 'deleted config option: %s', name )

        except KeyError:
            logging.debug( '%s: No such user config option', name )

        self.save()


    def save( self ):
        """
            Writes the user-settings in ASCII yet Pythonic style to the user's
            configfile, so that it can be edited manually and read-in using
            FastScript.execFile().

            If there are no user-settings at all the fill be removed
            (if present).
        """
        if self._userSettings:

            from ToolBOSCore.Packages.CopyrightHeader import getCopyrightHeader

            content = getCopyrightHeader( 'python', 'User preferences' )

            for key, value in sorted( self._userSettings.items() ):
                value = repr( value )          # write object as Python code

                content += '%s = %s\n\n' % ( key, value )

            content += '\n# EOF\n'

            logging.debug( 'writing %s', self._userFile )
            FastScript.setFileContent( self._userFile, content )

        else:
            # delete entire file if there are no settings left

            logging.debug( 'deleting empty configfile' )
            FastScript.remove( self._userFile )


    def _getEvalOrder( self ):
        """
            Returns an ordered list with paths to configfiles (in search order).
            First element: Highest priority (user's home dir.)
            Last element:  Lowest priority (default shipped with application)
        """
        Any.requireIsList( self._addFiles )

        resultList = []

        try:
            resultList.append( self._cwdFile )
        except OSError as details:
            # may be raised by os.getcwd() if there is a problem with the CWD
            # e.g. NFS problem or directory deleted by another process
            #
            # continuing to work in such situation is dangerous, we really should
            # stop in such case
            logging.error( details )
            logging.error( 'Problem with current working directory detected!' )
            raise SystemExit()


        resultList.append( self._userFile )
        resultList.append( self._machineFile )

        for addFile in self._addFiles:
            resultList.append( addFile )

        resultList.append( self._defaultFile )

        return resultList


    def _readFile( self, filePath ):
        if os.path.exists( filePath ):

            if os.path.isfile( filePath ):
                try:
                    logging.debug( 'evaluating %s', filePath )

                    result     = {}
                    allSymbols = FastScript.execFile( filePath )


                    # remove Python modules, callables etc. from dict
                    for key, value in allSymbols.items():
                        if Any.isTextNonEmpty( key ):
                            result[ key ] = value

                except( AssertionError, IOError, OSError ) as e:
                    logging.error( e )
                    result = {}

            else:
                logging.error( '%s: Not a regular file', filePath )
                result = {}
        else:
            # logging.debug( '%s: No such file', filePath )
            result = {}

        return result


    def _readFiles( self ):
        """
            Reads the config files into memory.

            The master-list of available config options is defined in
            the fallback list shipped with the application.
        """
        self._allSettings = {}

        # do in reverse order (starting from default), and update step-by-step
        # with the higher-priority settings
        order = self._getEvalOrder()
        order.reverse()

        for filePath in order:
            fileSettings = self._readFile( filePath )
            Any.requireIsDict( fileSettings )


            # merge settings into overall dict
            self._allSettings.update( fileSettings )


            if filePath is self._cwdFile:
                self._cwdSettings     = fileSettings

            elif filePath is self._userFile:
                self._userSettings    = fileSettings

            elif filePath is self._machineFile:
                self._machineSettings = fileSettings

            elif filePath is self._defaultFile:
                self._defaultSettings = fileSettings

            elif filePath in self._addFiles:
                logging.debug( 'merging default settings from: %s', filePath )
                self._defaultSettings.update( fileSettings )

            else:
                logging.warning( 'unexpected config file: %s', filePath )


        Any.requireIsDictNonEmpty( self._allSettings )


class AppConfigFactory( AppConfig ):

    def __init__( self, appName:str ):
        Any.requireIsTextNonEmpty( appName )

        envName    = appName.upper() + '_ROOT'
        pkgRoot    = FastScript.getEnv( envName )
        defaultDir = os.path.join( pkgRoot, 'etc' )
        userDir    = os.path.join( os.path.expanduser( '~' ), '.HRI', appName )

        super( AppConfigFactory, self ).__init__( appName, defaultDir, userDir )


# EOF
