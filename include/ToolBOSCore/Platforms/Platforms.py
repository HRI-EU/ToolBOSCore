# -*- coding: utf-8 -*-
#
#  Functions to query host platform
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


from ToolBOSCore.Util import FastScript
from ToolBOSCore.Util import Any


#----------------------------------------------------------------------------
# Public functions
#----------------------------------------------------------------------------


def getHostPlatform():
    """
        Returns a short phony identifier for the current system platform.

        On Linux this is typically a combination of O.S. release name
        and CPU wordsize. On Windows also the compiler name is encoded.
    """
    # possible to override with environment variable
    forcedPlatform = FastScript.getEnv( 'MAKEFILE_PLATFORM' )

    if forcedPlatform:
        hostPlatform = forcedPlatform

    else:
        from ToolBOSCore.Settings.ToolBOSConf import getConfigOption
        hostPlatform = getConfigOption( 'hostPlatform' )

    Any.requireIsTextNonEmpty( hostPlatform )

    return hostPlatform


def getHostArch():
    """
        Returns a short phony identifier for the current system architecture.
        On PCs this is typically either 'i686' (32 bit) or 'amd64' (64 bit).
    """
    from platform import machine
    from ToolBOSCore.Settings.ToolBOSConf import getConfigOption

    # check configfile
    try:
        hostArch = getConfigOption( 'hostArch' )
        Any.requireIsTextNonEmpty( hostArch )
        return hostArch

    except ( IOError, KeyError ):
        pass


    # fallback
    arch   = machine()
    system = getSystemType()
    result = arch

    if system == 'linux':

        if arch == 'i386':
            result = 'i686'

        elif arch == 'x86_64':
            result = 'amd64'

        elif arch == 'armv7l':
            result = 'armv7'

    return result


def getHostOS():
    """
        Returns the short lowercase form of the general operating system
        type of the host machine, e.g. 'linux' or 'win'.
    """
    # check configfile
    try:
        from ToolBOSCore.Settings.ToolBOSConf import getConfigOption
        hostOS = getConfigOption( 'hostOS' )
        Any.requireIsTextNonEmpty( hostOS )

        return hostOS

    except ( IOError, KeyError ):
        pass


    # fallback
    return getSystemType()


def getPlatformList():
    """
        Returns a tuple with individual information about each platform:
           [0]  full platform string (equivalent of former $MAKEFILE_PLATFORM)
           [1]  short name of O.S. class, e.g. "linux" or "windows"
           [2]  CPU word size, most often either 32 or 64 bit
           [3]  default compiler, e.g. "gcc" or "msvc"
    """
    return (
             ( 'bionic64',              'linux',     64, 'gcc',    'Ubuntu 18.04 LTS (64 bit)' ),
             ( 'focal64',               'linux',     64, 'gcc',    'Ubuntu 20.04 LTS (64 bit)' ),
             ( 'jammy64',               'linux',     64, 'gcc',    'Ubuntu 22.04 LTS (64 bit)' ),
             ( 'peakcan',               'peakcan',   32, 'gcc',    'PeakCAN Router' ),
             ( 'phyboardwega',          'phyboard',  32, 'gcc',    'phyboardwega' ),
             ( 'windows-amd64-vs2017',  'windows',   64, 'vs2017', 'Visual Studio 2017 on Microsoft Windows (64 bit)' )
            )


def getPlatformNames():
    """
        This function returns all possible platforms one could build for
        using this infrastructure, in other words all possible values of
        the $MAKEFILE_PLATFORM environment variable.
    """
    resultList = []
    for platform in getPlatformList():
        resultList.append( platform[0] )

    resultList.sort()

    return resultList


def getFullPlatformString( platformName ):
    """
        Returns a human-readable string for the given platform name, e.g.:

          getFullPlatformString( 'focal64' )

        will return:

          'Ubuntu 20.04 LTS (64 bit)'

    """
    Any.requireIsTextNonEmpty( platformName )
    Any.requireIsIn( platformName, getPlatformNames() )


    for platform in getPlatformList():

        if platform[0] == platformName:
            return platform[4]

    raise KeyError( 'invalid platform name: %s' % platformName )


def getSystemType( platformName = '' ):
    """
        If you want to lookup what O.S. type (e.g. Linux or Windows) the
        'squeeze64' platform is, this function is the right one for you.
        It returns the general operating system class of the platform.
    """
    from platform import system

    if platformName == '':
        sys = system().lower()
        if sys == 'windows':
            return 'win'
        else:
            return sys

    for entry in getPlatformList():
        if entry[0] == platformName:
            return entry[1]

    msg = "'%s' is not a supported platform, must be one out of: %s" % \
          ( platformName, ', '.join( getPlatformNames() ) )
    raise KeyError( msg )


# EOF
