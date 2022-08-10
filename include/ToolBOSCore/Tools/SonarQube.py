#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  run SonarQube scans on given project
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
import subprocess

from typing import Union

from ToolBOSCore.Settings import ProcessEnv, ToolBOSConf
from ToolBOSCore.Util     import Any, FastScript


def runScan( token: str ) -> Union[ None, bool ]:
    """
        Run SonarQube scan for packages with programming language Python,
        C, C++, JS, Go, PHP etc.

        Args:
            token : user token provided via commandline
    """
    logging.info( 'running SonarQube scanner...' )

    token = token if token else FastScript.getEnv( 'SONAR_TOKEN' )

    if not token:
        logging.error( 'no SonarQube user token provided' )
        return False

    ProcessEnv.source( ToolBOSConf.getConfigOption( 'package_sonarscanner' ) )
    ProcessEnv.requireCommand( 'sonar-scanner' )

    sonarQubeServer = ToolBOSConf.getConfigOption( 'sonarQubeServer' )

    cmd = 'sonar-scanner -Dsonar.host.url=%s -Dsonar.login=%s' % ( sonarQubeServer, token )

    try:
        FastScript.execProgram( cmd )
    except subprocess.CalledProcessError as e:
        logging.debug( e )
        raise AssertionError() from e


def runBuildWrapper( buildCommand: str ) -> None:
    """
        Run SonarQube build wrapper for packages that
        requires a build step

        Args:
            buildCommand : build command provided via commandline
    """
    Any.requireIsText( buildCommand )

    ProcessEnv.source( ToolBOSConf.getConfigOption( 'package_sonarwrapper' ) )
    ProcessEnv.requireCommand( 'build-wrapper-linux-x86-64' )

    logging.debug( 'PATH: %s', FastScript.getEnv( 'PATH' ) )

    _cleanup()

    cmd = 'build-wrapper-linux-x86-64 --out-dir bw-output' + ' ' + buildCommand

    try:
        FastScript.execProgram( cmd )
    except subprocess.CalledProcessError as e:
        logging.debug( e )
        raise AssertionError() from e


def _cleanup():
    """
        Clean the build artifacts before executing the SonarQube build wrapper
    """
    FastScript.remove( 'build' )
    FastScript.remove( 'bw-output' )


# EOF