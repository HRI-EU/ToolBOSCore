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


#----------------------------------------------------------------------------
# Includes
#----------------------------------------------------------------------------


import logging
import os

from ToolBOSCore.Util import Any
from ToolBOSCore.Util import FastScript


#----------------------------------------------------------------------------
# Constants
#----------------------------------------------------------------------------


packageName    = 'ToolBOSCore'
packageVersion = '3.3'
canonicalPath  = 'DevelopmentTools/ToolBOSCore/3.3'

settingsFile   = 'ToolBOS.conf'


#----------------------------------------------------------------------------
# Public functions
#----------------------------------------------------------------------------


def getSettingsFile_user():
    """
       Returns the path of the user's ToolBOS config file.
    """
    path = os.path.join( os.path.expanduser( '~' ), '.HRI',
                         'ToolBOS', settingsFile )

    return path


def getSettingsFile_default():
    """
       Returns the path of the config file shipped with the ToolBOSCore
       package itself, which is used as last fallback of all cases.
    """
    path = os.path.join( FastScript.getEnv( 'TOOLBOSCORE_ROOT' ),
                         'etc', settingsFile )

    return path


def getSettingsFile_machine():
    """
       Returns the path of the config file stored in the system's
       configuration directory (on Linux under "/etc").

       Settings there are typically only changed by the administrator.
    """
    path = os.path.join( '/etc', settingsFile )

    return path


def getSettingsFile_cwd():
    """
       Returns the path of the config file within the current working
       directory.
    """
    path = os.path.join( os.getcwd(), settingsFile )

    return path


def getConfigOptions( addPaths=None ):
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
    order = _getEvalOrder( addPaths )
    order.reverse()

    for fileName in order:
        try:
            fileSymbols = FastScript.execFile( fileName )
            logging.debug( 'evaluating %s', fileName )
        except( AssertionError, IOError, OSError ):
            fileSymbols = {}

        allSymbols.update( fileSymbols )

    # remove Python modules, callables etc. from dict
    result = {}
    for key, value in allSymbols.items():
        if Any.isTextNonEmpty( key ) and not Any.isCallable( value ):
            result[ key ] = value

    return result


def getConfigOption( varName, addPaths=None ):
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

    for fileName in _getEvalOrder( addPaths ):
        # logging.debug( 'evaluating %s', fileName )
        try:
            result = _getConfigOptionFromFile( varName, fileName )
            # logging.debug( 'found "%s" in %s', varName, fileName )

            return result

        except( AssertionError, IOError, KeyError, OSError ):
            pass

    # nowhere found
    raise KeyError( "Config option '%s' is nowhere set." % varName )


def getUserConfigOptions():
    """
        Returns a dict with the settings from the user's configfile (if any).

        Unlike getConfigOptions() it does not look-up all the other files
        like in the current working directory or the system-wide or default
        configs.
    """
    fileName = getSettingsFile_user()

    # read current settings (if any)
    try:
        config = FastScript.execFile( fileName )
    except IOError:                     # no such file
        config = {}

    return config


def getUserConfigOption( varName ):
    """
        This function searches for a variable 'varName' in the user's
        ToolBOS configfile named 'ToolBOS.conf'.

        Unlike getConfigOption() it does not look-up all the other files
        like in the current working directory or the system-wide or default
        configs.

        If the user has no ToolBOS.conf or the specified variable is not set,
        a key error will be thrown.
    """
    return getUserConfigOptions()[ varName ]


def setUserConfigOption( varName, value ):
    """
        Write a user-preference to the user's configfile.

        Note: 'key' must be a string, value should be a string or iterable.

        Use delConfigOption() to remove a setting.
    """
    Any.requireIsTextNonEmpty( varName )
    Any.requireMsg( varName[0].isalpha(),
                    'varName parameter must start with a letter' )

    # update setting
    config = getUserConfigOptions()
    config[ varName ] = value
    logging.debug( 'setting config option: %s=%s', varName, str(value) )

    _setUserConfigOptions( config )


def delUserConfigOption( varName ):
    """
        Removes a certain config option from the user's configfile.
    """
    Any.requireIsTextNonEmpty( varName )

    # read current settings (if any)
    config = getUserConfigOptions()


    # remove setting
    try:
        del config[ varName ]
        logging.debug( 'deleted config option: %s', varName )

        # delete entire file if there are no settings left
        if config:
            _setUserConfigOptions( config )
        else:
            fileName = getSettingsFile_user()
            logging.debug( 'deleting empty configfile' )
            logging.debug( 'rm %s', fileName )
            FastScript.remove( fileName )

    except KeyError:
        logging.debug( '%s: No such user config option', varName )


#----------------------------------------------------------------------------
# Private functions
#----------------------------------------------------------------------------


def _getConfigOptionFromFile( varName, fileName ):
    """
        This function attempts to find a variable 'varName' defined in
        the file 'fileName'.
    """
    Any.requireIsTextNonEmpty( varName )
    Any.requireIsFileNonEmpty( fileName )

    value = FastScript.execFile( fileName )[varName]

    return value


def _getEvalOrder( addPaths=None ):
    """
        Returns an ordered list with paths to configfiles (in search order).
        First element: Highest priority (user's home dir.)
        Last element:  Lowest priority (default shipped with ToolBOS SDK)

        To search in non-standard locations provide a list 'addPaths'.
        Its path entries will be searched right after ./ToolBOS.conf.
    """
    if addPaths is not None:
        Any.requireIsListNonEmpty( addPaths )

    try:
        tmpList = [ getSettingsFile_cwd(),
                    getSettingsFile_user(),
                    getSettingsFile_machine(),
                    getSettingsFile_default() ]

    except OSError as details:
        # may be raised by os.getcwd() if there is a problem with the CWD
        # e.g. NFS problem or directory deleted by another process
        #
        # continuing to work in such situation is dangerous, we really should
        # stop in such case
        logging.error( details )
        logging.error( 'Problem with current working directory detected!' )
        raise SystemExit()


    if addPaths:
        resultList = [ tmpList[0] ]

        for path in addPaths:
            resultList.append( [ os.path.join( path, settingsFile ) ] )

        resultList.append( tmpList[1:] )
        resultList = FastScript.flattenList( resultList )

        # logging.debug( 'full list: %s', resultList )
    else:
        resultList = tmpList

    return resultList


def _setUserConfigOptions( config ):
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

    fileName = getSettingsFile_user()
    dirName  = os.path.dirname( fileName )

    FastScript.mkdir( dirName )
    FastScript.setFileContent( fileName, content )


# EOF
