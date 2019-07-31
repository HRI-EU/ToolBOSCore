#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  run Klocwork tool on this project
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
import re
import os
import shlex
import subprocess
import tempfile

from ToolBOSCore.Packages  import PackageCreator
from ToolBOSCore.Platforms import Platforms
from ToolBOSCore.Settings  import ProcessEnv
from ToolBOSCore.Settings  import ToolBOSSettings
from ToolBOSCore.Util      import FastScript
from ToolBOSCore.Util      import Any


def isWithinTmpDir():
    """
        Returns whether or not the current working directory is within
        the location for temporary files, f.i. "/tmp" on Linux.

        Background: Klocwork ignores sources files in such directories,
                    effectively making it impossible to scan packages
                    in such location.

        @:returns True or False
    """
    return os.getcwd().startswith( tempfile.gettempdir() )


def requireOutsideTmpDir():
    """
        Decorator for isWithinTmpDir() which throws an AssertionError
        if the result is True.
    """
    Any.requireMsg( not isWithinTmpDir(),
                    'Klocwork can not be run within %s' % tempfile.gettempdir() )


def createLocalProject( klocworkDir='klocwork', stdout=None, stderr=None ):
    """
        Creates a local .kwlp directory so that the analysis can be performed.

        @Retuns: nothing.

        Throws an RuntimeError in case of problems.
    """
    Any.requireIsTextNonEmpty( klocworkDir )

    requireOutsideTmpDir()

    kwPackage         = ToolBOSSettings.getConfigOption( 'package_klocwork' )
    buildSpec         = os.path.join( klocworkDir, 'kwinject.out' )
    kwlpDir           = os.path.join( klocworkDir, '.kwlp' )  # KW local project
    kwpsDir           = os.path.join( klocworkDir, '.kwps' )  # KW project settings
    hostPlatform      = Platforms.getHostPlatform()
    licenseServerHost = ToolBOSSettings.getConfigOption( 'kwLicenseServerHost' )
    licenseServerPort = ToolBOSSettings.getConfigOption( 'kwLicenseServerPort' )

    Any.requireIsTextNonEmpty( kwPackage )
    Any.requireIsTextNonEmpty( hostPlatform )

    ProcessEnv.source( kwPackage )
    FastScript.mkdir( klocworkDir )         # ensure this exists
    FastScript.remove( kwlpDir )            # but those should not exist
    FastScript.remove( kwpsDir )            # but those should not exist

    if ProcessEnv.which( 'kwinject' ) is None:
        msg = '%s not installed for platform=%s' % ( kwPackage, hostPlatform )

        raise EnvironmentError( msg )


    # inspect the build process to capture source files, defines, flags,...
    cmd = 'kwinject -o %s %s' % ( buildSpec, 'BST.py -dsb' )
    FastScript.execProgram( cmd, stdout=stdout, stderr=stderr )
    Any.requireIsFileNonEmpty( buildSpec )


    # create Klocwork project directory
    cmd = 'kwcheck create --license-host %s --license-port %d -pd %s -sd %s %s' % \
          ( licenseServerHost, licenseServerPort, kwlpDir, kwpsDir, buildSpec )
    FastScript.execProgram( cmd, stdout=stdout, stderr=stderr )
    Any.requireIsDir( kwlpDir )
    Any.requireIsDir( kwpsDir )


    # import the build specification into project directory
    cmd = 'kwcheck import -pd %s %s' % ( kwlpDir, buildSpec )
    FastScript.execProgram( cmd, stdout=stdout, stderr=stderr )


    # install the HIS-Subset taxonomy so that the user may select it
    tcRoot   = FastScript.getEnv( 'TOOLBOSCORE_ROOT' )
    fileName = 'HIS_Subset_MISRA_C_1.0.2.tconf'
    srcFile  = os.path.join( tcRoot, 'external/emenda.com', fileName )
    dstDir   = os.path.join( kwpsDir, 'servercache' )
    dstFile  = os.path.join( dstDir, fileName )

    Any.requireIsFileNonEmpty( srcFile )
    FastScript.mkdir( dstDir )
    FastScript.copy( srcFile, dstFile )


    # auto-detect source code directories (exclude some blacklisted ones)
    dirList = []
    cwd     = os.getcwd()

    for dirName in FastScript.getDirsInDir():
        if dirName not in ( 'build', 'doc', 'external', 'lib' ):
            dirList.append( os.path.join( cwd, dirName ) )


    # create workingset
    values  = { 'dirList': dirList }
    creator = PackageCreator.PackageCreator( 'dummy', '1.0', values )
    srcDir  = os.path.join( creator.templateDir, 'KlocworkProject' )
    dstDir  = kwlpDir

    creator.templatize( os.path.join( srcDir, 'workingsets.xml' ),
                        os.path.join( dstDir, 'workingsets.xml' ) )


def codeCheck( klocworkDir='klocwork', stdout=None, stderr=None ):
    """
        Performs a CLI-analysis of the project.

        Note that the Klocwork-project must have been created before,
        e.g. using createLocalProject().
    """
    Any.requireIsDirNonEmpty( klocworkDir )

    requireOutsideTmpDir()

    ProcessEnv.source( ToolBOSSettings.getConfigOption( 'package_klocwork' ) )

    kwlpDir = os.path.join( klocworkDir, '.kwlp' )
    Any.requireIsDirNonEmpty( kwlpDir )

    cmd     = 'kwcheck run -pd %s' % kwlpDir
    FastScript.execProgram( cmd, stdout=stdout, stderr=stderr )


def parseCodeCheckResult( output ):
    """
        Extracts the location and issue description from the console
        output. Example:

            output = StringIO()
            Klocwork.codeCheck( stdout=output, stderr=output )
            issues = Klocwork.parseCodeCheckResult( output.getvalue() )

        @return: List of tuples of form ( filename, lineNo,
                                          issue description, kwRuleID )
    """
    Any.requireIsTextNonEmpty( output )

    #Any.requireMsg( output.find( 'Build contains errors' ) == -1,
                    #'Klocwork analysis failed (build contained errors)' )


    # Alternatively kwcheck can produce XML output which could be more robust
    # to parse. Consider this when working again on this topic.
    #
    # Example:
    #   $ kwcheck run -pd ... -F xml --report


    resultList = []
    regexp     = re.compile( '^\d+\s\([A-Za-z]+\)\s(.*?):(\d+)\s(.+?)\s' )
    lines      = output.splitlines()
    cwd        = os.getcwd()

    # issues are spread over two lines in the output, hence we need the
    # output line number for parsing

    for i, line in enumerate( lines ):
        tmp = regexp.match( line )

        if tmp:
            fileName = os.path.relpath( tmp.group(1), cwd )
            lineNo   = tmp.group(2)
            kwRule   = tmp.group(3)
            desc     = lines[ i + 1 ]

            Any.requireIsTextNonEmpty( fileName )
            Any.requireIsTextNonEmpty( lineNo )
            Any.requireIsTextNonEmpty( desc )

            resultList.append( ( fileName, lineNo, desc, kwRule ) )

    return resultList


def startGUI( options='', blocking=False ):
    """
        Launches the Klocwork Desktop GUI.

        The program can be opened blocking or non-blocking, f.i. in
        background in order not to block the caller.
    """
    requireOutsideTmpDir()

    ProcessEnv.source( ToolBOSSettings.getConfigOption( 'package_klocwork' ) )

    try:
        cmd = 'kwgcheck %s' % options
        logging.debug( 'executing: %s', cmd )

        if blocking:
            FastScript.execProgram( cmd )
        else:
            subprocess.Popen( shlex.split( cmd ) )

    except ( subprocess.CalledProcessError, OSError ) as details:
        logging.error( details )


# EOF
