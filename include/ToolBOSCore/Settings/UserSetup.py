# -*- coding: utf-8 -*-
#
#  settings of the user's shell environment
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


import glob
import logging
import os
import shutil
import subprocess

from ToolBOSCore.Packages import ProjectProperties
from ToolBOSCore.Settings import ProcessEnv
from ToolBOSCore.Settings import ToolBOSConf
from ToolBOSCore.Util     import FastScript
from ToolBOSCore.Util     import Any


def silentUpgrade():
    """
        Upgrade the user's environment settings if certain settings or
        file locations change.
    """
    dirName = os.path.expandvars( '${HOME}/.HRI' )


    # clean-up no longer needed files / directories
    FastScript.remove( os.path.join( dirName, 'DTBOS' ) )
    FastScript.remove( os.path.join( dirName, 'ToolBOSCore' ) )


    # move settings file to new location
    oldFile = os.path.join( dirName, 'LocalSettings.py' )
    newDir  = os.path.join( dirName, 'ToolBOS' )
    newFile = os.path.join( newDir,  'ToolBOS.conf' )

    if os.path.exists( oldFile ) and not os.path.exists( newFile ):
        logging.debug( 'mv %s %s', oldFile, newFile )
        FastScript.mkdir( newDir )
        os.rename( oldFile, newFile )


def setupShell():
    """
        Configures the user's shell environment to use the ToolBOS SDK.

        It tries to detect if the shell was already once configured
        (by this script or manually) and attempts to reset it to the
        default state.
    """
    fileName = os.path.expanduser( '~/.bash_login' )
    content  = '''if [ `basename -- "$0"` != Xsession ] ; then
  source .bashrc
fi
'''

    # remove it, because could be an existing file / symlink
    FastScript.remove( fileName )

    logging.info( 'creating %s', fileName )
    FastScript.setFileContent( fileName, content )


def setupProxy( sitRootPath=None, sitProxyPath=None ):
    """
        Convenience-wrapper to create a default proxy directory.

        WARNING: If a proxy already exists, it will be DELETED !

        You may specify the absolute paths for the SIT root- and/or
        proxy directories. If omitted, typical defaults will be used.
    """
    from ToolBOSCore.Storage import ProxyDir
    from ToolBOSCore.Storage import SIT

    if not sitRootPath:
        sitRootPath  = SIT.getDefaultRootPath()

    if not sitProxyPath:
        sitProxyPath = SIT.getDefaultProxyPath()

    Any.requireIsTextNonEmpty( sitRootPath )
    Any.requireIsTextNonEmpty( sitProxyPath )
    Any.requireIsDir( sitRootPath )


    # delete existing proxy if it exists, it might be screwed up
    if os.path.exists( sitProxyPath ):
        logging.info( 'cleaning existing proxy in %s', sitProxyPath )
        FastScript.remove( sitProxyPath )

    logging.info( 'creating proxy directory... (this may take some time)' )
    logging.info( 'SIT Root:  %s', sitRootPath )
    logging.info( 'SIT Proxy: %s', sitProxyPath )
    ProxyDir.createProxyDir( sitRootPath, sitProxyPath, verbose=False )


def getWineConfigDir( postfix='' ):
    configDir = FastScript.getEnv( 'WINEPREFIX' )

    if not configDir:
        configDir = os.path.expandvars( '${HOME}/.HRI/ToolBOS/wine%s' % postfix )

    return configDir

def baseSetupWine( configDir, msvc, stdout, stderr, postfix ):
    if not configDir:
        configDir = getWineConfigDir( postfix )

    # safety check: exit if we are within CIA and configdir points to
    # home directories!
    if FastScript.getEnv( 'CIA' ) == 'TRUE' and configDir.startswith( '/home' ):
        raise SystemExit( 'SAFETY GUARD: Do not touch home directory within CIA!' )

    sourceWindowsBSP( msvc )
    ProcessEnv.requireCommand( 'winecfg' )

    FastScript.setEnv( 'WINEPREFIX', configDir )
    FastScript.mkdir( configDir )

    logging.info( 'setting up Wine in %s', configDir )

    # temporarily unset the DISPLAY variable so that the 'winecfg'
    # utility does not show up
    oldDisplay = FastScript.getEnv( 'DISPLAY' )
    FastScript.unsetEnv( 'DISPLAY' )
    FastScript.execProgram( 'winecfg', stdout=stdout, stderr=stderr )

    # wait for wineserver shutdown (default: 3 seconds)
    waitWineServerShutdown( configDir, postfix )

    if oldDisplay:
        FastScript.setEnv( 'DISPLAY', oldDisplay )

    logging.info( 'Microsoft .NET support enabled' )


def setupLegacyMSVC( configDir ):
    from ToolBOSCore.Storage.SIT import getPath

    sitRootPath = getPath()
    packageName = 'Data/wine.net/0.1'
    handmadeDir = os.path.join( sitRootPath, packageName, 'config' )
    userName    = FastScript.getCurrentUserName()

    if not os.path.exists( handmadeDir ):
        raise AssertionError( '%s: No such package in SIT' % packageName )

    if not userName:
        raise AssertionError( 'Unable to query username :-(' )


    # replace 'Program Files' and 'windows' directories in configDir by
    # symlinks to handmade directories in SIT

    for item in ( 'Program Files', 'windows' ):
        path = os.path.join( configDir, 'drive_c', item )
        Any.requireIsDir( path )
        FastScript.remove( path )

        target = os.path.join( handmadeDir, 'drive_c', item )
        FastScript.link( target, path )


    # copy all the handmade *.reg files
    regFiles = glob.glob( "%s/*.reg" % handmadeDir )
    Any.requireIsListNonEmpty( regFiles )

    for srcFilePath in regFiles:
        fileName    = os.path.basename( srcFilePath )
        dstFilePath = os.path.join( configDir, fileName )

        logging.debug( 'cp %s %s', srcFilePath, dstFilePath )
        shutil.copyfile( srcFilePath, dstFilePath )
        Any.requireIsFileNonEmpty( dstFilePath )

        # replace occurrences of 'roberto' by username
        oldContent = FastScript.getFileContent( dstFilePath )
        newContent = oldContent.replace( 'roberto', userName )
        FastScript.setFileContent( dstFilePath, newContent )


def setupWineDotNet( configDir=None, stdout=None, stderr=None, postfix='', msvc=2012 ):
    """
        Configures WINE ("Wine Is Not an Emulator", see www.winehq.com)
        plus settings for Microsoft .NET framework.

        You may provide a path to the directory where to create the config
        files. If omitted, the path returned from getWineConfigDir() will be
        used.
    """

    baseSetupWine( configDir, msvc, stdout, stderr, postfix )

    # TODO: Consider moving this function call in the proper MSVC 2012 setup
    #       routine.
    if msvc in (2010, 2012):
        setupLegacyMSVC( configDir )


def setupMSVC( configDir, sdk ):
    Any.requireMsg( sdk in ( 2008, 2010, 2012, 2017 ),
                    'SDK version must be "2008", "2010", "2012" or "2017" (not "%s")' % sdk )

    logging.debug( 'SDK=%s', sdk )

    if sdk == 2008:
        raise ValueError( 'SDK 2008 is no longer supported' )
    else:
        if sdk in (2010, 2012):
            setupMSVC2012( configDir )      # 2010 and 2012 use the same setup
        elif sdk == 2017:
            setupMSVC2017( configDir )
        else:
            # Realistically no chance to get here
            raise RuntimeError('setupMSVC: unsupported MSVC version: %s' % sdk)


def setupMSVC2017( configDir ):
    """
        Configures the Microsoft Visual Compiler to be used with Wine
        from the ToolBOS build system.

        You may provide a path to the directory where your Wine
        configuration is. If omitted, the path returned from getWineConfigDir()
        will be used.
    """
    from ToolBOSCore.Storage.SIT import getPath

    if not os.path.exists( os.path.join( configDir, 'user.reg' ) ):
        setupWineDotNet( configDir, msvc=2017 )

    Any.requireIsDir( configDir )

    logging.info( 'Setting up Visual Studio...' )

    sitPath     = getPath()
    packageName = 'Data/wine.net/1.1'
    msvcDir     = os.path.join( sitPath, packageName, 'config' )

    linkPath   = os.path.join( configDir, 'drive_c', 'BuildTools' )
    linkTarget = os.path.join( msvcDir, 'drive_c', 'BuildTools')
    FastScript.remove( linkPath )
    FastScript.link( linkTarget, linkPath )

    linkPath   = os.path.join( configDir, 'drive_c', 'Program Files', 'Microsoft SDKs'  )
    linkTarget = os.path.join( msvcDir, 'drive_c', 'Program Files', 'Microsoft SDKs' )
    FastScript.remove( linkPath )
    FastScript.link( linkTarget, linkPath )

    linkPath   = os.path.join( configDir, 'drive_c', 'Program Files', 'Windows Kits'  )
    linkTarget = os.path.join( msvcDir, 'drive_c', 'Program Files', 'Windows Kits' )
    FastScript.remove( linkPath )
    FastScript.link( linkTarget, linkPath )


def setupMSVC2012( configDir ):
    """
        Configures the Microsoft Visual Compiler to be used with Wine
        from the ToolBOS build system.

        You may provide a path to the directory where your Wine
        configuration is. If omitted, the path returned from getWineConfigDir()
        will be used.
    """
    from ToolBOSCore.Storage.SIT import getPath

    if not os.path.exists( os.path.join( configDir, 'user.reg' ) ):
        setupWineDotNet( configDir )

    Any.requireIsDir( configDir )

    if not os.path.exists( os.path.join( configDir, 'dosdevices' ) ):
        setupWineDotNet( configDir )

    logging.info( 'setting up Visual Studio...' )

    linkPath   = os.path.join( configDir, 'dosdevices', 'c:' )
    linkTarget = '../drive_c'
    FastScript.remove( linkPath )
    FastScript.link( linkTarget, linkPath )

    linkPath   = os.path.join( configDir, 'dosdevices', 'z:' )
    linkTarget = '/'
    FastScript.remove( linkPath )
    FastScript.link( linkTarget, linkPath )

    # create temp. directories
    driveC      = os.path.join( configDir, 'drive_c' )
    userName    = FastScript.getCurrentUserName()
    userTempDir = os.path.join( driveC, 'users', userName, 'Temp' )
    sysTempDir  = os.path.join( driveC, 'temp' )
    logging.debug( 'userTempDir=%s', userTempDir )
    FastScript.mkdir( userTempDir )
    FastScript.mkdir( sysTempDir )

    # ensure to NOT have the "h:" link, else wine would not find some links
    FastScript.remove( os.path.join( configDir, 'dosdevices', 'h:' ) )

    # replace "C:\Program Files" by symlink into SIT
    FastScript.remove( os.path.join( configDir, 'drive_c', 'Program Files' ) )

    sitPath    = getPath()

    linkPath   = os.path.join( configDir, 'drive_c', 'msvc-sdk' )
    linkTarget = os.path.join( sitPath, 'External/MSVC/10.0/msvc-sdk' )
    FastScript.remove( linkPath )
    FastScript.link( linkTarget, linkPath )

    linkPath   = os.path.join( configDir, 'drive_c', 'Program Files' )
    linkTarget = os.path.join( sitPath, 'External/MSVC/10.0/Program Files' )
    FastScript.remove( linkPath )
    FastScript.link( linkTarget, linkPath )

    # copy a hancrafted system.reg
    srcFile = os.path.join( sitPath, 'External/MSVC/10.0/otherstuff/winevs2012/system.reg' )
    dstFile = os.path.join( configDir, 'system.reg' )
    shutil.copyfile( srcFile, dstFile )

    # force wine to use the MSVC native library
    userReg = os.path.join( configDir, 'user.reg' )

    Any.requireIsFileNonEmpty( userReg )
    content = FastScript.getFileContent( userReg )

    if content.find( '1413877490' ) == -1:
        content += \
'''

[Software\\\\Wine\\\\DllOverrides] 1413877490
"mscoree"="native"
"msvcr110"="native"

'''
        logging.debug( 'updating %s', userReg )
        FastScript.setFileContent( userReg, content )


def sourceWindowsBSP(msvc):
    """
        Loads the necessary ToolBOSPluginWindows so that Wine and MSVC
        will be found in PATH etc.
    """
    allBSPs       = ToolBOSConf.getConfigOption( 'BST_crossCompileBSPs' )
    Any.requireIsDictNonEmpty( allBSPs )

    if msvc in (2010, 2012):
        canonicalPath = allBSPs[ 'windows-amd64-vs2012' ]
    elif msvc == 2017:
        canonicalPath = allBSPs[ 'windows-amd64-vs2017' ]
    else:
        raise RuntimeError('sourceWindowsBSP: unsupported MSVC version: %s' % msvc)

    ProjectProperties.requireIsCanonicalPath( canonicalPath )

    ProcessEnv.source( canonicalPath )


def ensureMSVCSetup( sdk, postfix='' ):
    """
        Verifies that the Wine / MSVC installation is present and correct.

        If WINEPREFIX is set, this will be used, otherwise fallback to
        default wine location.

        An optional 'postfix' might be specified to separate several Wine
        config directories for different purposes.
    """

    def _msvc2012SpecificChecks():
        if not os.path.exists( os.path.join( configDir, 'user.reg' ) ):
            setupWineDotNet( configDir, postfix )


        linkPath = os.path.join( configDir, 'drive_c', 'msvc-sdk' )

        if not os.path.exists( linkPath ):    # considers broken links
            logging.debug( '%s not found', linkPath )
            setupMSVC( configDir, sdk )

        # sometimes it happens that the registry gets screwed up
        userReg = os.path.join( configDir, 'user.reg' )
        Any.requireIsFileNonEmpty( userReg )
        content = FastScript.getFileContent( userReg )

        if content.find( '1413877490' ) == -1:
            logging.debug( 'found broken registry: rebuilding %s', configDir )
            setupMSVC( configDir, sdk )

    def _msvc2017SpecificChecks():

        linkPath = os.path.join( configDir, 'drive_c', 'BuildTools' )

        if not os.path.exists( linkPath ):
            logging.debug( '%s not found', linkPath )
            setupMSVC( configDir, sdk )

    configDir = FastScript.getEnv( 'WINEPREFIX' )

    if not configDir:
        configDir = getWineConfigDir( postfix )
        FastScript.setEnv( 'WINEPREFIX', configDir )

    waitWineServerShutdown( configDir, postfix )

    if sdk in (2010, 2012):
        _msvc2012SpecificChecks()
    elif sdk == 2017:
        _msvc2017SpecificChecks()
    else:
        raise RuntimeError('ensureMSVCSetup: unsupported MSVC version: %s' % sdk)


def startWineServer( configDir=None, postfix='' ):
    """
        Start Winserver

        You may provide a path to the Wine config directory and/or a
        config name postfix. If omitted, the path returned from
        getWineConfigDir() will be used.
    """
    if not configDir:
        configDir = getWineConfigDir( postfix )
        FastScript.setEnv( 'WINEPREFIX', configDir )

    FastScript.execProgram( 'wineserver' )


def waitWineServerShutdown( configDir=None, postfix='' ):
    """
        Wait Winserver shutdown

        You may provide a path to the Wine config directory and/or a
        config name postfix. If omitted, the path returned from
        getWineConfigDir() will be used.
    """

    if not configDir:
        configDir = getWineConfigDir( postfix )
        FastScript.setEnv( 'WINEPREFIX', configDir )

    # wait for wineserver shutdown (default: 3 seconds)
    logging.debug( 'waiting for wineserver to shut down...' )

    try:
        FastScript.execProgram( 'wineserver -k' )
    except subprocess.CalledProcessError:
        pass


# EOF
