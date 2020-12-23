#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Aux.scripts around JetBrains PyCharm IDE (www.jetbrains.com/pycharm)
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


import glob
import io
import logging
import os
import subprocess
import xml.etree.ElementTree

from ToolBOSCore.BuildSystem               import BuildSystemTools
from ToolBOSCore.Settings                  import ProcessEnv
from ToolBOSCore.Settings                  import ToolBOSConf
from ToolBOSCore.Packages                  import ProjectProperties
from ToolBOSCore.Packages.PackageCreator import PackageCreator_JetBrains_PyCharm_Config
from ToolBOSCore.Util                      import Any
from ToolBOSCore.Util                      import FastScript


#----------------------------------------------------------------------------
# Public functions
#----------------------------------------------------------------------------


def getConfigDir():
    """
        #Returns the path to the IDE settings directory, or raises
        AssertionError if not set.
    """
    configDir = FastScript.getEnv( 'PYCHARM_CONFIGDIR' )
    Any.requireMsg( configDir, 'Environment variable PYCHARM_CONFIGDIR not set' )

    return configDir


def createProject():
    """
        Turns a software package into PyCharm project.

        For this some files within ".idea" are created.
    """
    BuildSystemTools.requireTopLevelDir()

    configDir = '.idea'
    logging.info( 'creating config in %s', configDir )

    projectRoot    = ProjectProperties.detectTopLevelDir()

    if projectRoot is None:
        raise RuntimeError( 'unable to detect top-level-directory of package' )

    packageName    = ProjectProperties.getPackageName( projectRoot )
    packageVersion = ProjectProperties.getPackageVersion( projectRoot )

    Any.requireIsTextNonEmpty( packageName )
    Any.requireIsTextNonEmpty( packageVersion )


    template = PackageCreator_JetBrains_PyCharm_Config( packageName,
                                                        packageVersion,
                                                        outputDir=configDir )
    template.run()


def codeCheck():
    """
        Performs a static source code analysis using PyCharm's built-in
        code inspector.

        The default inspection profile of the project is used, which unless
        modified by the developer will be the common HRI-EU profile coming
        from CreatePyCharmProject.py

        If there is no ".idea" directory in the current directory, it will
        be temporarily created and deleted when finished.

        @returns: defects as list of XML strings

        @see: parseCodeCheckResult()

    """
    ProcessEnv.source( ToolBOSConf.getConfigOption( 'package_pycharm' ) )

    output   = io.StringIO()
    FastScript.execProgram( 'ps aux', stdout=output, stderr=output )

    if output.getvalue().find( 'pycharm' ) > 0:
        raise RuntimeError( 'PyCharm already running, unable to invoke code checker' )

    # create project files if not existing
    if os.path.exists( '.idea' ):
        created = False
    else:
        created = True
        #createUserConfig()
        createProject()

    resultsDir = 'build/PY05'
    FastScript.remove( resultsDir )
    FastScript.mkdir( resultsDir )

    output.truncate( 0 )

    cmd = 'inspect.sh . HRI-EU %s' % resultsDir

    try:
        logging.info( 'running analysis...' )
        FastScript.execProgram( cmd, stdout=output, stderr=output )

        if Any.getDebugLevel() > 3:
            logging.info( '\n%s', output.getvalue() )

    except subprocess.CalledProcessError:
        if output.getvalue().find( 'No valid license found' ) > 0:
            raise RuntimeError( 'PyCharm: No valid license found' )
        else:
            raise RuntimeError( output.getvalue() )


    # delete project files if we have created them
    if created:
        FastScript.remove( '.idea' )


    resultList = []

    for filePath in glob.glob( 'build/PY05/*.xml' ):
        Any.requireIsFile( filePath )
        content = FastScript.getFileContent( filePath )

        resultList.append( content )

    return resultList


def parseCodeCheckResult( xmlList ):
    """
        Extracts the location and issue description from the list of XML
        strings returned by codeCheck().

        @param xmlList: raw output from codeCheck()
        @return: List of tuples of form ( filename, lineNo, issue description )
    """
    Any.requireIsList( xmlList )

    resultList = []
    cwd        = os.getcwd()


    for xmlString in xmlList:
        Any.requireIsTextNonEmpty( xmlString )

        e = xml.etree.ElementTree.fromstring( xmlString )

        for problem in e.findall( 'problem' ):
            fileName = os.path.relpath( problem.find( 'file' ).text, cwd )
            lineNo   = problem.find( 'line' ).text
            desc     = problem.find( 'description' ).text

            # turn specific URL-style into relative path
            fileName = fileName.replace( 'file://$PROJECT_DIR$/', '' )
            fileName = fileName.replace( 'file:/$PROJECT_DIR$/', '' )

            Any.requireIsTextNonEmpty( fileName )
            Any.requireIsTextNonEmpty( lineNo )
            Any.requireIsTextNonEmpty( desc )

            resultList.append( [ fileName, lineNo, desc ] )

    return resultList


def startGUI():
    """
        Launches the PyCharm IDE.

        Note that the program will be opened in background in order not to
        block the caller.
    """
    ProcessEnv.source( ToolBOSConf.getConfigOption( 'package_pycharm' ) )

    try:
        cmd = 'pycharm.sh'
        logging.debug( 'executing: %s', cmd )
        subprocess.Popen( cmd )
    except ( subprocess.CalledProcessError, OSError ) as details:
        logging.error( details )


# EOF
