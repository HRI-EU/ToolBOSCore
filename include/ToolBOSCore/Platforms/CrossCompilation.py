# -*- coding: utf-8 -*-
#
#  Everything related to cross-compilation
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


import os
import re

from ToolBOSCore.Platforms import Platforms
from ToolBOSCore.Settings  import ToolBOSConf
from ToolBOSCore.Util      import FastScript
from ToolBOSCore.Util      import Any


#----------------------------------------------------------------------------
# Public functions
#----------------------------------------------------------------------------


def switchEnvironment( toPlatform ):
    """
        Modifies the environment variables to appear as if this was another
        operating system. This is primary used for cross-compilations.

        If you would like to later restore the original settings, make sure
        to call "origEnv = FastScript.getEnv()" before invoking this
        function. When you are done, you can then reset the whole environment
        by calling "FastScript.setEnv( origMap )".
    """
    Any.requireIsTextNonEmpty( toPlatform )

    fromPlatform = Platforms.getHostPlatform()
    src          = fromPlatform.replace( '-', '' )
    dst          = toPlatform.replace( '-', '' )
    funcName     = "_switchEnv_%s_to_%s" % ( src, dst )

    if fromPlatform == toPlatform:
        return

    try:
        func = globals()[funcName]
    except KeyError:
        msg = "requested platform switch (%s to %s) is not supported" % \
              ( fromPlatform, toPlatform )
        raise NotImplementedError( msg )

    func()
    FastScript.setEnv( 'MAKEFILE_PLATFORM', toPlatform )


def getSwitchEnvironmentList( fromPlatform=None ):
    """
        This function can be used to fetch a list of platforms to which
        the <fromPlatform> can be switched to. Example:

           getSwitchEnvironmentList( 'focal64' )

        If <fromPlatform> is None, all possible cross-compilation platforms
        are returned.
    """
    if fromPlatform is None:
        xcmpHosts = ToolBOSConf.getConfigOption( 'BST_crossCompileHosts' )

        # only return those which are not None
        result    = filter( bool, xcmpHosts.keys() )
        result.sort()

        return result


    Any.requireIsTextNonEmpty( fromPlatform )

    if fromPlatform not in Platforms.getPlatformNames():
        raise ValueError( '%s: unsupported platform name' % fromPlatform )


    # get list of all functions in this module, then filter it by name
    # (function-name convention allows us to filter-out the supported target
    # platforms)

    allSymbols = globals().keys()
    criteria   = lambda s: s.startswith( '_switchEnv_' )
    candidates = filter( criteria, allSymbols )

    regexp     = re.compile( '^_switchEnv_%s_to_(.*)$' % fromPlatform )
    resultList = []

    for candidate in candidates:
        tmp = regexp.search( candidate )

        if tmp is not None:
            targetPlatform = tmp.group(1)
            Any.requireIsTextNonEmpty( targetPlatform )

            # Windows-platforms are named e.g. 'windows-amd64-vs2017'.
            # However names with dashes can't be used as function names
            # thus the above candidates don't contain such dashes.
            #
            # As a hack I'm replacing such well-known names here by hand.
            # Better solutions are highly appreciated.
            #
            if targetPlatform == 'windowsamd64vs2017':
                targetPlatform = 'windows-amd64-vs2017'

            resultList.append( targetPlatform )

    resultList.sort()

    return resultList


def getNativeCompilationList():
    """
        Returns the value of the ToolBOS config option
        'BST_defaultPlatforms_native', defaulting to the current
        host platform if not overwritten by the user.
    """
    platformList = list( ToolBOSConf.getConfigOption( 'BST_defaultPlatforms_native' ) )

    if not platformList:
        platformList = [ Platforms.getHostPlatform() ]

    platformList.sort()

    return platformList


def getCrossCompilationList():
    """
        Returns the value of the ToolBOS config option
        'BST_defaultPlatforms_xcmp'.
    """
    platformList = list( ToolBOSConf.getConfigOption( 'BST_defaultPlatforms_xcmp' ) )

    platformList.sort()

    return platformList


def getNativeCompileHost( platform ):
    """
        Returns the hostname or IP address of the compile host responsible
        for natively compiling on 'platform', None if not defined.

        Such values are site-specific and hence need to be configured via
        ToolBOS.conf.
    """
    Any.requireIsTextNonEmpty( platform )


    hosts = ToolBOSConf.getConfigOption( 'BST_userCompileHosts' )

    try:
        return hosts[ platform ]
    except ( KeyError, TypeError ):
        # not found in user's configfile
        pass


    hosts = ToolBOSConf.getConfigOption( 'BST_compileHosts' )

    try:
        return hosts[ platform ]
    except KeyError:
        return None


def getCrossCompileHost( platform ):
    """
        Returns the hostname or IP address of the compile host responsible
        for cross-compiling for 'platform', None if not defined.

        Such values are site-specific and hence need to be configured via
        ToolBOS.conf.
    """
    Any.requireIsTextNonEmpty( platform )

    hosts = ToolBOSConf.getConfigOption( 'BST_userCrossCompileHosts' )

    try:
        return hosts[ platform ]
    except (KeyError, TypeError):
        # not found in user's configfile
        pass

    hosts = ToolBOSConf.getConfigOption( 'BST_crossCompileHosts' )

    try:
        return hosts[ platform ]
    except KeyError:
        return None


#----------------------------------------------------------------------------
# Private functions
#----------------------------------------------------------------------------


# Change the environment so it appears to the build system as if we would
# run on another platform, e.g. Windows with Visual Studio installed.


def _switchEnv_bionic64_to_windowsamd64vs2017():
    _switchEnv_linuxToWindows( 'windows-amd64-vs2017' )


def _switchEnv_focal64_to_windowsamd64vs2017():
    _switchEnv_linuxToWindows( 'windows-amd64-vs2017' )


def _switchEnv_jammy64_to_windowsamd64vs2017():
    _switchEnv_linuxToWindows( 'windows-amd64-vs2017' )


def _switchEnv_bionic64_to_peakcan():
    _switchEnv_linuxIntelToARM( 'peakcan' )


def _switchEnv_bionic64_to_phyboardwega():
    _switchEnv_linuxIntelToARM( 'phyboardwega' )


def _switchEnv_linuxToWindows( targetPlatform ):
    import logging

    from ToolBOSCore.Settings import ProcessEnv
    from ToolBOSCore.Settings import UserSetup
    from ToolBOSCore.Settings import ToolBOSConf

    Any.requireIsTextNonEmpty( targetPlatform )

    def _set_msvc_2017_conf():
        UserSetup.ensureMSVCSetup( sdk, postfix = '.' + targetPlatform )
        Any.requireMsg( FastScript.getEnv( 'WINEPREFIX' ), '$WINEPREFIX not set' )

        msvcBasePath          = r'c:\BuildTools\VC'
        msvcToolsBasePath     = r'{}\Tools\MSVC\14.13.26128'.format( msvcBasePath )
        msvcAuxiliaryBasePath = r'{}\Auxiliary\VS'.format( msvcBasePath )
        wkitBasePath          = r'c:\Program Files\Windows Kits\10'
        wsdkBasePath          = r'c:\Program Files\Microsoft SDKs\Windows\v10.0A'
        wkitVersion           = '10.0.16299.0'
        cpu                   = 'x64' if targetArch == 'amd64' else 'x86'

        FastScript.setEnv( 'TARGETOS', 'windows' )
        FastScript.setEnv( 'TARGETARCH', targetArch )
        FastScript.setEnv( 'COMPILER', 'vs2017' )
        FastScript.setEnv( 'INCLUDE', r'{}\include'.format( msvcBasePath ) )
        FastScript.setEnv( 'LIB', r'{0}\lib\{3};{0}\lib\onecore\{3};{1}\Lib\{4}\um\{3};{1}\Lib\{4}\ucrt\{3};{2}\Lib'.format( msvcToolsBasePath,
                                                                                                                             wkitBasePath,
                                                                                                                             wsdkBasePath,
                                                                                                                             cpu,
                                                                                                                             wkitVersion ) )
        FastScript.setEnv( 'CL', r'/I"{0}\UnitTest\include" /I"{0}\include" /I"{1}\atlmfc\include" /I"{1}\include" /I"{2}\Include\{3}\ucrt" /I"{2}\Include\{3}\um" /I"{2}\Include\{3}\shared"'.format( msvcAuxiliaryBasePath,
                                                                                                                                                                                                       msvcToolsBasePath,
                                                                                                                                                                                                       wkitBasePath,
                                                                                                                                                                                                       wkitVersion ) )
        FastScript.setEnv( 'CL_CMD', r'{0}\bin\Host{1}\{1}\cl.exe'.format( msvcToolsBasePath, cpu ) )
        FastScript.setEnv( 'LINK_CMD', r'{0}\bin\Host{1}\{1}\link.exe'.format( msvcToolsBasePath, cpu ) )
        FastScript.setEnv( 'LIB_CMD', r'{0}\bin\Host{1}\{1}\lib.exe'.format(msvcToolsBasePath, cpu) )
        FastScript.setEnv( 'RC_CMD', r'{0}\bin\{1}\rc.Exe'.format( wkitBasePath, cpu ) )
        FastScript.setEnv( 'MT_CMD', r'{0}\bin\{1}\mt.Exe'.format( wkitBasePath, cpu ) )
        FastScript.setEnv( 'DUMPBIN_CMD', r'{0}\bin\Host{1}\{1}\dumpbin.exe'.format( msvcToolsBasePath, cpu ) )
        FastScript.setEnv( 'WindowsLibPath', r'{0}\UnionMetadata\{1};{0}\References\{1}'.format( wkitBasePath,
                                                                                                 wkitVersion ) )
        FastScript.setEnv( 'LIBPATH', r'{0}\atlmfc\lib\{2};{0}\lib\{2};{0}\lib\{2}\store\references;{1}\UnionMetadata\{3};{1}\References\{3}'.format( msvcToolsBasePath,
                                                                                                                                                      wkitBasePath,
                                                                                                                                                      cpu,
                                                                                                                                                      wkitVersion ) )

        if cpu == 'x86':
            compilerBasePath  = r'{0}\bin\Hostx86\x86'.format( msvcToolsBasePath )
            compilerBasePath += r';{0}\bin\Hostx86\x86;{0}\bin\Hostx86\x64\1033;{0}\bin\Hostx86\x86\1033'.format( msvcToolsBasePath )
        else:
            compilerBasePath  = r'{0}\bin\Hostx64\x64'.format( msvcToolsBasePath )
            compilerBasePath += r';{0}\bin\Hostx64\x64\1033'.format( msvcToolsBasePath )

        FastScript.setEnv( 'Path', compilerBasePath )

    def _set_msvc_legacy_conf():
        if sdk == 2008:
            compilerSuite = 'msvc'
            pdkVersion    = 'v6.1'
        else:
            compilerSuite = 'vs%d' % sdk
            pdkVersion    = 'v7.1'

        UserSetup.ensureMSVCSetup( sdk, postfix = '.' + targetPlatform )
        Any.requireMsg( FastScript.getEnv( 'WINEPREFIX' ), '$WINEPREFIX not set' )

        basePath          = '''c:\\msvc-sdk\\''' + compilerSuite + '''\\'''
        compilerBasePath  = basePath + '''VC\\'''
        pdkBasePath       = '''c:\\msvc-sdk\\Windows\\''' + pdkVersion + '''\\'''
        compilerCrossPath = ''
        x64               = ''
        amd64             = ''

        if targetArch == 'amd64':
            compilerCrossPath = '''\\x86_amd64'''
            x64               = '''\\x64'''
            amd64             = '''\\amd64'''

        FastScript.setEnv( 'TARGETOS', 'windows' )
        FastScript.setEnv( 'TARGETARCH' , targetArch )
        FastScript.setEnv( 'COMPILER', compilerSuite )
        FastScript.setEnv( 'Include', pdkBasePath + '''Include;''' + compilerBasePath + '''include''' )
        FastScript.setEnv( 'Lib', compilerBasePath + '''lib''' + amd64 + ''';''' + pdkBasePath + '''Lib''' + x64 )
        FastScript.setEnv( 'Path', compilerBasePath + '''bin''' + compilerCrossPath + ''';''' +
                           compilerBasePath + '''bin''' + compilerCrossPath + '''\\1033;''' +
                           compilerBasePath + '''bin;''' +
                           basePath + '''Common7\\IDE;''' +
                           pdkBasePath + '''Bin''' )
        FastScript.setEnv( 'CL_CMD', compilerBasePath + '''bin''' + compilerCrossPath + '''\\cl.exe''' )
        FastScript.setEnv( 'LINK_CMD', compilerBasePath + '''bin''' + compilerCrossPath + '''\\link.exe''' )
        FastScript.setEnv( 'LIB_CMD', compilerBasePath + '''bin''' + compilerCrossPath + '''\\lib.exe''')
        FastScript.setEnv( 'RC_CMD', pdkBasePath + '''Bin\\RC.Exe''' )
        FastScript.setEnv( 'MT_CMD', pdkBasePath + '''Bin\\mt.exe''' )
        FastScript.setEnv( 'DUMPBIN_CMD', compilerBasePath + '''Bin\\dumpbin.exe''' )

    tmp        = re.match( r"^(\S+)-(\S+)-vs(\d+)$", targetPlatform )
    targetArch = tmp.group(2)
    sdk        = int(tmp.group(3))

    Any.requireIsTextNonEmpty( targetArch )
    Any.requireIsIntNotZero( sdk )

    # source "ToolBOSPluginWindows" if not already done

    bspMap     = ToolBOSConf.getConfigOption( 'BST_crossCompileBSPs' )
    Any.requireIsDictNonEmpty( bspMap )

    neededBSP  = bspMap[ targetPlatform ]
    Any.requireIsTextNonEmpty( neededBSP )
    ProcessEnv.source( neededBSP )

    logging.debug( 'using wine from: %s', ProcessEnv.which( 'wine' ) )

    # setup Wine

    if not FastScript.getEnv( 'WINEDEBUG' ):
        FastScript.setEnv( 'WINEDEBUG', '-all' )

    if sdk == 2017:
        _set_msvc_2017_conf()
    else:
        _set_msvc_legacy_conf()

    # setup arguments which will be passed to CMake

    fileName = os.path.join( FastScript.getEnv( 'TOOLBOSCORE_ROOT' ),
                             'include/CMake/Platform/Linux-MSVC.cmake' )
    Any.requireIsFileNonEmpty( fileName )

    oldOptions = FastScript.getEnv( 'BST_CMAKE_OPTIONS' )

    if oldOptions:
        newOptions = '-Wno-dev -DCMAKE_TOOLCHAIN_FILE=%s %s' % ( fileName, oldOptions )
    else:
        newOptions = '-Wno-dev -DCMAKE_TOOLCHAIN_FILE=%s' % fileName
    FastScript.setEnv( 'BST_CMAKE_OPTIONS', newOptions )

    FastScript.unsetEnv( 'GLIBC_ALIAS' )
    FastScript.unsetEnv( 'GLIBC_VERSION' )


def _switchEnv_linuxIntelToARM( targetPlatform ):
    from ToolBOSCore.Settings import ProcessEnv
    from ToolBOSCore.Settings import ToolBOSConf

    Any.requireIsTextNonEmpty( targetPlatform )


    # source cross-compiler package if not already done

    bspMap     = ToolBOSConf.getConfigOption( 'BST_crossCompileBSPs' )
    Any.requireIsDictNonEmpty( bspMap )

    neededBSP  = bspMap[ targetPlatform ]
    Any.requireIsTextNonEmpty( neededBSP )
    ProcessEnv.source ( neededBSP )


    # setup arguments which will be passed to CMake

    if targetPlatform == 'peakcan':

        fileName = os.path.join( FastScript.getEnv( 'TOOLBOSCORE_ROOT' ),
                                 'include/CMake/Peakcan-cross.cmake' )

        Any.requireIsFileNonEmpty( fileName )

        FastScript.setEnv( 'TARGETOS',   'peakcan' )
        FastScript.setEnv( 'TARGETARCH', 'peakcan' )
        FastScript.setEnv( 'COMPILER',   'gcc'     )
        FastScript.setEnv( 'BST_CMAKE_OPTIONS', '-DCMAKE_TOOLCHAIN_FILE=%s' % fileName )

    elif targetPlatform == 'phyboardwega':

        fileName = os.path.join( FastScript.getEnv( 'TOOLBOSCORE_ROOT' ),
                                 'include/CMake/phyBOARD-WEGA-cross.cmake' )

        Any.requireIsFileNonEmpty( fileName )

        FastScript.setEnv( 'TARGETOS', 'phyboardwega' )
        FastScript.setEnv( 'TARGETARCH', 'phyboardwega' )
        FastScript.setEnv( 'COMPILER', 'gcc' )
        FastScript.setEnv( 'BST_CMAKE_OPTIONS',
                           '-DCMAKE_TOOLCHAIN_FILE=%s' % fileName )

    else:

        fileName = os.path.join( FastScript.getEnv( 'TOOLBOSCORE_ROOT' ),
                                 'include/CMake/Linux-ARMv7-cross.cmake' )

        Any.requireIsFileNonEmpty( fileName )

        FastScript.setEnv( 'TARGETOS',   'linux'   )
        FastScript.setEnv( 'TARGETARCH', 'armv7'   )
        FastScript.setEnv( 'COMPILER',   'gcc'     )
        FastScript.setEnv( 'BST_CMAKE_OPTIONS', '-DCMAKE_TOOLCHAIN_FILE=%s' % fileName )


# EOF
