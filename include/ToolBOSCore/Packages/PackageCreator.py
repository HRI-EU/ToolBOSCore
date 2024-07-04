# -*- coding: utf-8 -*-
#
#  Functions to create a new package
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
import random
import shutil

from ToolBOSCore.Packages.PackageDetector   import PackageDetector
from ToolBOSCore.Packages.ProjectProperties import requireIsCanonicalPath
from ToolBOSCore.Storage                    import SIT
from ToolBOSCore.Storage.BashSrc            import BashSrcWriter
from ToolBOSCore.Storage.PackageVar         import PackageVarCmakeWriter
from ToolBOSCore.Storage.PkgInfoWriter      import PkgInfoWriter
from ToolBOSCore.Util                       import FastScript


def makeShellfiles( projectRoot ):
    """
        Creates all the various BashSrc, pkgInfo.py etc. files.

        If <topLevelDir>/<fileName> exists it will be copied instead of
        auto-generated. This allows writing fully handcrafted files if
        necessary.

        'topLevelDir' is assumed to be a source code working copy
        (including the version, e.g. "/home/foo/mycode/Spam/42.0")

    """
    FastScript.requireIsDir( projectRoot )

    oldcwd = os.getcwd()
    FastScript.changeDirectory( projectRoot )


    # collect package details once (this function is internally multi-threaded)

    try:
        details = PackageDetector( projectRoot )
        details.retrieveMakefileInfo()
        details.retrieveVCSInfo()
    except AttributeError:
        raise ValueError( 'Unable to create shellfiles in path="%s", is this '
                          'a package directory?' % projectRoot )
    except ValueError as details:
        raise ValueError( details )

    FastScript.mkdir( './install' )

    if os.path.exists( 'BashSrc' ):
        logging.info( 'cp BashSrc ./install/' )
        shutil.copy2( 'BashSrc', './install/BashSrc' )
    else:
        BashSrcWriter( details ).write( './install/BashSrc'    )

    # Note: pkgInfo.py is always generated (merged)
    PkgInfoWriter( details ).write( './install/pkgInfo.py' )

    if os.path.exists( 'packageVar.cmake' ):
        logging.info( 'cp packageVar.cmake ./install/' )
        shutil.copy2( 'packageVar.cmake', './install/packageVar.cmake' )
    else:
        # try to generate a reasonable file (put explicitly under ./install/
        # to indicate it's a installation-temporary file
        #
        # if the user wants to handcraft it, he could move this
        # auto-generated file to ./packageVar.cmake and add it to VCS
        PackageVarCmakeWriter( details ).write( './install/packageVar.cmake' )

    FastScript.changeDirectory( oldcwd )


def uninstall( canonicalPath, cleanGlobalInstallation, dryRun=False ):
    """
         Delete a package from SIT, this includes:

            * Proxy SIT directory
            * Global SIT installation

        If 'cleanGlobalInstallation=True' the package will also be
        uninstalled from global SIT (if applicable). If False it
        will only be uninstalled from the proxy SIT.
    """
    from ToolBOSCore.Platforms  import Platforms

    requireIsCanonicalPath( canonicalPath )

    FastScript.requireIsBool( dryRun )

    sitProxyPath       = SIT.getPath()
    sitRootPath        = SIT.getRootPath()
    FastScript.requireIsTextNonEmpty( sitProxyPath )
    FastScript.requireIsTextNonEmpty( sitRootPath )

    installRoot_proxy  = os.path.join( sitProxyPath, canonicalPath )
    installRoot_root   = os.path.join( sitRootPath, canonicalPath )

    logging.info( 'uninstalling %s', canonicalPath )

    logging.info( 'cleaning proxy-installation' )
    FastScript.remove( installRoot_proxy, dryRun )

    if cleanGlobalInstallation:
        logging.info( 'cleaning global-installation' )
        FastScript.remove( installRoot_root, dryRun )


def randomizeValidityFlags():
    """
        Randomizes valid-/invalid-flags to be used as C-defines, e.g.:

        #define FOO_VALID    ( 0x998877 )
        #define FOO_INVALID  ( 0x112233 )

        Returns a tuple of two strings containing the hexvalues.
    """
    valid      = random.randint( 0x00000000, 0xFFFFFFFF )
    invalid    = random.randint( 0x00000000, 0xFFFFFFFF )

    if valid == invalid:
        valid, invalid = randomizeValidityFlags()


    # format int as hex-string with padding
    # (e.g. 0x00000000 so ten chars in total)
    #
    # {   # Format identifier
    # 0:  # first parameter
    # #   # use "0x" prefix
    # 0   # fill with zeroes
    # {1} # to a length of n characters (including 0x), defined by the second parameter
    # x   # hexadecimal number, using lowercase letters for a-f
    # }   # End of format identifier
    #
    validStr   = "{0:#0{1}x}UL".format( valid,   10 )
    invalidStr = "{0:#0{1}x}UL".format( invalid, 10 )

    FastScript.requireIsTextNonEmpty( validStr )
    FastScript.requireIsTextNonEmpty( invalidStr )

    return validStr, invalidStr


# EOF
