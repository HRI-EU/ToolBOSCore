#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Aux.scripts around JetBrains CLion IDE (www.jetbrains.com/clion)
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
import subprocess

from ToolBOSCore.BuildSystem               import BuildSystemTools
from ToolBOSCore.Packages.PackageCreator import PackageCreator_JetBrains_CLion_Config
from ToolBOSCore.Packages                  import ProjectProperties
from ToolBOSCore.Settings                  import ProcessEnv
from ToolBOSCore.Settings                  import ToolBOSConf
from ToolBOSCore.Util                      import Any


#----------------------------------------------------------------------------
# Public functions
#----------------------------------------------------------------------------


def createProject():
    """
        Turns a software package into CLion project.

        For this some files within ".idea" are created.
    """
    BuildSystemTools.requireTopLevelDir()

    configDir = '.idea'
    logging.info( 'creating config in %s', configDir )

    projectRoot    = ProjectProperties.detectTopLevelDir()
    packageName    = ProjectProperties.getPackageName( projectRoot )
    packageVersion = ProjectProperties.getPackageVersion( projectRoot )

    Any.requireIsTextNonEmpty( packageName )
    Any.requireIsTextNonEmpty( packageVersion )


    template = PackageCreator_JetBrains_CLion_Config( packageName,
                                                      packageVersion,
                                                      outputDir=configDir )
    template.run()


def startGUI():
    """
        Launches the CLion IDE.

        Note that the program will be opened in background in order not to
        block the caller.
    """
    ProcessEnv.source( ToolBOSConf.getConfigOption( 'package_clion' ) )

    try:
        cmd = 'clion.sh'
        logging.debug( 'executing: %s', cmd )
        subprocess.Popen( cmd )
    except ( subprocess.CalledProcessError, OSError ) as details:
        logging.error( details )


# EOF
