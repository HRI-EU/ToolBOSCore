# -*- coding: utf-8 -*-
#
#  Rules and related check functions of Software Quality Guideline
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


import ast
import collections
import inspect
import logging
import os
import re
import shlex
import subprocess
import sys
import tempfile

import six

from ToolBOSCore.BuildSystem                      import BuildSystemTools
from ToolBOSCore.BuildSystem.DocumentationCreator import DocumentationCreator
from ToolBOSCore.Packages.PackageDetector         import PackageDetector
from ToolBOSCore.Platforms.Platforms              import getHostPlatform
from ToolBOSCore.Settings.ToolBOSSettings         import getConfigOption
from ToolBOSCore.SoftwareQuality.Common           import *
from ToolBOSCore.Tools                            import CMake, Klocwork,\
                                                         Matlab, PyCharm,\
                                                         Valgrind
from ToolBOSCore.Util                             import Any, FastScript, \
                                                         VersionCompat


C_CPP_FILE_EXTENSIONS = ( '.c', '.cpp', '.h', '.hpp' )


class AbstractQualityRule( object ):

    ruleID      = None
    brief       = None
    description = None
    goodExample = None
    badExample  = None
    seeAlso     = {}
    sqLevel     = None


    def __init__( self ):
        self.details    = None
        self.files      = None
        self.passed     = 0
        self.failed     = 0


    def getRuleID( self ):

        className = type(self).__name__
        ruleID    = className.split('_')[-1]

        return ruleID


class QualityRule_GEN01( AbstractQualityRule ):

    brief       = '''All comments, documentation, identifier names (types,
variables, functions, classes) and filenames must be English.'''
    description = '''Even if intended for personal use only, you never know
who might be using your source code in the future.

English as corporate language should be reflected in the source code as well.
Other languages such as German or Japanese should be avoided.'''

    goodExample = '''\tint result = 123;'''

    badExample  = '''\tint ergebnis = 123;'''

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Look for specific characters such as German Umlauts, French
            accents, or Japanese characters.
        """
        logging.debug( 'checking files for Non-English characters...' )
        passed = 0
        failed = 0

        whitelist      = ( '.c', '.cpp', '.h', '.hpp', '.inc', '.java', '.m',
                           '.py' )

        for filePath in files:
            if os.path.splitext( filePath )[-1] in whitelist:

                logging.debug( 'checking %s', filePath )

                passedInFile, failedInFile = findNonAsciiCharacters( filePath, 'GEN01' )
                passed += passedInFile
                failed += failedInFile

        if failed == 0:
            result = ( OK, passed, failed,
                       'all identifiers and comments OK' )
        else:
            result = ( FAILED, passed, failed,
                       'files with Non-ASCII characters found' )

        return result


class QualityRule_GEN02( AbstractQualityRule ):

    brief       = '''Source code should be in ASCII or UTF-8 files.
Filenames should only contain alphanumeric characters.'''

    description = '''For exchanging text files between countries with
different character sets the modern UTF-8 file encoding should be used.
Otherwise, with traditional region-dependent language settings such as
ISO-8859-1 (Germany) or ISO-2022-JP (Japan) most likely the Non-ASCII
characters will not be correctly displayed on the receiver side.
Furthermore, saving such file will destroy special characters.

Note: On recent Linux and Windows versions UTF-8 is standard. Nevertheless
please check the encoding. Most often it can be found in the "Save as"
dialog.'''

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Attempts to find special characters in source files. According
            to GEN-02 only ASCII- or UTF-8 files shall be used, and German
            Umlauts or Japanese characters must be avoided.
        """
        import chardet

        logging.debug( 'checking files for ASCII or UTF-8 charset' )
        passed = 0
        failed = 0

        for filePath in files:
            content  = FastScript.getFileContent( filePath, asBinary=True )

            encoding = chardet.detect( content )['encoding']

            if encoding in ( 'ascii', 'utf-8' ):
                logging.debug( '%s: %s', filePath, encoding )
                passed += 1
            else:
                logging.info( 'GEN02: %s: invalid file encoding (%s)',
                              filePath, encoding )
                failed += 1

        if failed == 0:
            result = ( OK, passed, failed,
                       'all files with ASCII or UTF-8 encoding' )
        else:
            result = ( FAILED, passed, failed,
                       'files with invalid encoding found' )

        return result


class QualityRule_GEN03( AbstractQualityRule ):

    brief       = '''Stick to 80 characters per line. Exceptions are fine
when increasing readability.'''

    description = '''Limiting to 80 characters eases editing / viewing:

  * IDEs show add. widgets at left / right side
  * xterm defaults to 80x25
  * merging sources (side-by-side view)'''

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Detects the max. line length of each source file. Ideally all
            files should have a line length of < 80 characters.
        """
        logging.debug( 'checking line length of files' )
        failed    = 0
        limit     = 80
        grace     = 40
        maxWidth  = limit + grace        # we only search for really long lines
        threshold = 5

        for filePath in files:
            longLines = 0
            maxLen    = 0
            lines     = FastScript.getFileContent( filePath, splitLines=True )

            for line in lines:
                length = len( line.rstrip() )

                if length > maxWidth:       # long line found
                    longLines += 1

                if length > maxLen:         # found an ever-longer line
                    maxLen   = length       # than known so far

            logging.debug( '%s: longLines=%d, maxLen=%d',
                           filePath, longLines, maxLen )


            # a few exceptions might be OK for readability reasons
            if longLines > threshold:
                logging.info( 'GEN03: %s: found %d lines with more than %d chars',
                              filePath, longLines, maxWidth )
                failed += 1

        passed = len(files) - failed

        if failed == 0:
            result = ( OK, passed, failed,
                       'all source files within length limit' )
        else:
            result = ( FAILED, passed, failed,
                       'source files exceeding width limit of %d (grace=%d)' % \
                       ( limit, maxWidth ) )

        return result


class QualityRule_GEN04( AbstractQualityRule ):

    brief       = '''All source code files and related artefacts, such as
configfiles or documentation, must start with the HRI-EU copyright header.'''

    description = '''The standardized copyright header contains both copyright
claim and address of the company.

Please add it to all source code files and related artefacts resulting from
work for HRI-EU.

This copyright header must also be applied by contractors and students working
for HRI-EU.

This rule does not need to be applied to auto-generated files, such as doxygen
HTML documentation or generated SWIG code.

*Header for C / C++ / Java files:*

    /*
     * <description>
     *
     * Copyright (C)
     * Honda Research Institute Europe GmbH
     * Carl-Legien-Str. 30
     * 63073 Offenbach/Main
     * Germany
     *
     * UNPUBLISHED PROPRIETARY MATERIAL.
     * ALL RIGHTS RESERVED.
     *
     */

*Header for Python files:*

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    #
    # <description>
    #
    # Copyright (C)
    # Honda Research Institute Europe GmbH
    # Carl-Legien-Str. 30
    # 63073 Offenbach/Main
    # Germany
    #
    # UNPUBLISHED PROPRIETARY MATERIAL.
    # ALL RIGHTS RESERVED.
    #
    #

*Header for shell script files:*

    #!/bin/sh
    #
    # <description>
    #
    # Copyright (C)
    # Honda Research Institute Europe GmbH
    # Carl-Legien-Str. 30
    # 63073 Offenbach/Main
    # Germany
    #
    # UNPUBLISHED PROPRIETARY MATERIAL.
    # ALL RIGHTS RESERVED.
    #
    #

*Header for Matlab script files:*

    %
    % <description>
    %
    % Copyright (C)
    % Honda Research Institute Europe GmbH
    % Carl-Legien-Str. 30
    % 63073 Offenbach/Main
    % Germany
    %
    % UNPUBLISHED PROPRIETARY MATERIAL.
    % ALL RIGHTS RESERVED.
    %
    %

*Example for Windows `.bat` scripts:*

    ::
    :: <description>
    ::
    :: Copyright (C)
    :: Honda Research Institute Europe GmbH
    :: Carl-Legien-Str. 30
    :: 63073 Offenbach/Main
    :: Germany
    ::
    :: UNPUBLISHED PROPRIETARY MATERIAL.
    :: ALL RIGHTS RESERVED.
    ::

*Example for HTML / XML files:*

    <!--
    #
    # <description>
    #
    # Copyright (C)
    # Honda Research Institute Europe GmbH
    # Carl-Legien-Str. 30
    # 63073 Offenbach/Main
    # Germany
    #
    # UNPUBLISHED PROPRIETARY MATERIAL.
    # ALL RIGHTS RESERVED.
    #
    #-->

Please replace *description* by a very short summary what this file is about.

Note: Author names are not part of the header. Instead they should be listed
in the documentation.'''

    seeAlso     = { 'rule DOC-04': None }

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks if the HRI-EU copyright header is present.
        """
        from ToolBOSCore.Packages.CopyrightHeader import getCopyright

        logging.debug( 'checking files for copyright header' )
        failed = 0

        copyrightLines = getCopyright()
        whitelist      = ( '.c', '.cpp', '.h', '.hpp', '.inc', '.java', '.m',
                           '.py', '.bat' )

        for filePath in files:
            if os.path.splitext( filePath )[-1] in whitelist:
                logging.debug( 'checking %s', filePath )
                content = FastScript.getFileContent( filePath )

                for line in copyrightLines:
                    if content.find( line ) == -1:
                        logging.info( 'GEN04: copyright header missing in %s',
                                      filePath )
                        failed += 1
                        break
            # else:
            #     logging.debug( 'not checking %s', filePath )

        passed = len(files) - failed

        if failed == 0:
            result = ( OK, passed, failed,
                       'copyright header found everywhere' )
        else:
            result = ( FAILED, passed, failed,
                       'copyright header missing' )

        return result


class QualityRule_GEN05( AbstractQualityRule ):

    brief       = '''No type abbreviations must be added to identifiers
("Hungarian notation"), because types may change without updating the
identifier name possibly leading to wrong assumptions later.'''

    description = '''The intention of putting the typename into the variable
name (""Hungarian notation"") is to make obvious for the reader that the
variable is of a certain type.

However this is considered a bad practice because sooner or later the actual
type might be changed without updating the variable name everywhere else.
Hence this can cause datatype mis-interpretation which then may lead to
rounding- or range-errors. These can manifest in really longstanding
hard-to-track bugs.'''

    goodExample = '''\tdouble x = 0.0;'''

    badExample  = '''\tdouble dblX = 0.0;'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class QualityRule_GEN06( AbstractQualityRule ):

    brief       = 'Do not use tabs in code.'

    description = '''Only use **spaces** (blanks) for indentation in source code
files. The tabwidth is not defined and hence may screw up the source code
formatting.

For some languages such as Python the formatting is crucial. Wrong usage of
tabs may lead to undesired behavior.

Note: Non-sourcecode files, such as **Makefiles**, may require the usage of
tabs.'''

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks if source files contain tabs.
        """
        logging.debug( 'searching for tabs in source code' )
        passed = 0
        failed = 0

        for fileName in files:
            content = FastScript.getFileContent( fileName )

            if content.find( '\t' ) == -1:
                passed += 1
            else:
                lines  = content.splitlines()
                lineNo = 1
                reported = 0

                for line in lines:
                    pos = line.find( '\t' )

                    if pos != -1:
                        logging.info( 'GEN06: tab found in %s:%d',
                                      fileName, lineNo )

                        reported += 1

                    if reported > 10:
                        logging.info( 'GEN06: tab found in %s:[...]',
                                      fileName )
                        break

                    lineNo += 1

                failed += 1


        if failed == 0:
            result = ( OK, passed, failed,
                       'source files do not contain tabs' )
        else:
            result = ( FAILED, passed, failed,
                       'source files contain tabs' )

        return result


class QualityRule_GEN07( AbstractQualityRule ):

    brief       = 'Libraries and applications should contain a unittest.'

    description = '''Even if covering just a small part, some unittests make
you sleep better: When executed automatically (during nightly builds) they
show:

  * the code is compilable (f.i. on multiple platforms)
  * no broken dependencies, such as API changes
  * executables are runnable (no undefined symbols, missing files,...)
  * tested code somehow behaves as expected'''

    seeAlso     = { 'Unittest HowTo': 'ToolBOS_Util_BuildSystemTools_Unittesting' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks if the package provides a unittest.
        """
        logging.debug( 'looking for unittest.{sh,bak}' )
        found = False

        for fileName in ( 'unittest.sh', 'unittest.bat' ):
            if os.path.exists( fileName ):
                logging.debug( '%s found', fileName )
                found = True

        if found:
            result = ( OK, 1, 0, 'unittest found' )
        else:
            result = ( FAILED, 0, 1, 'unittest not found' )

        return result


class QualityRule_GEN08( AbstractQualityRule ):

    brief       = '''Any 3rd party code must be clearly separated to avoid
any intellectual property conflicts. Mind to put relevant license information
if needed.'''

    description = '''Closely integrating 3rd party software such as compiling
foreign source code into the own application very likely will violate the
license of the 3rd party software. This can result in severe legal problems.
(There are some licenses which permit such usage, f.i. BSD License).

Even putting 3rd party libraries into the own source code repository is within
a questionable grey zone. At least create a sub-directory named
*external* and put all 3rd party modules inside. This makes obvious that you
do not claim ownership on this material.

Best approach is to install 3rd party software independently into SIT, and
interface with it.'''

    goodExample = '''\tMyPackage
\t\t1.0
\t\t\texternal
\t\t\t\tcmake.org
\t\t\t\t\t[...]
\t\t\t\tgnome.org
\t\t\t\t\t[...]
\t\t\t\tmathworks.com
\t\t\t\t\t[...]
\t\t\t\tsubversion.apache.org
\t\t\t\t\t[...]
\t\t\tsrc
\t\t\t\tMyPackage.c
\t\t\t\tMyPackage.h'''

    seeAlso     = { 'Source tree conventions':
                    'ToolBOS_Concept_SourceTreeConventions',

                    'Installation conventions':
                    'ToolBOS_Concept_InstallationConventions' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class QualityRule_GEN09( AbstractQualityRule ):

    brief       = '''If any 3rd party software is involved in the project,
its usage or interfacing must be compliant with its license terms.'''

    description = '''Before attempting to use or interface with any 3rd party
software, make sure that its license permits both current and also foreseeable
use case(s). Regularly re-check validity of license terms against your use
cases.

If in doubt, get in contact with its authors and / or lawyers, and do not use
or interface with that software until the license situation has been clarified.

Try to design and implement your application in a way that you could migrate
it with reasonable effort to an alternative software.'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class QualityRule_GEN10( AbstractQualityRule ):

    brief       = '''Put package under version control system (Git/SVN).'''

    description = '''A version control system serves several purposes:

  * preserve individual source code states over time
  * track or rollback modifications
  * agreed "master" location
  * avoids chaos of various copies + patchfiles
  * central backup

Note: HRI-EU permits to use Git or Subversion (SVN).'''

    seeAlso     = { 'SVN HowTo': 'ToolBOS_HowTo_SVN',
                    'Git HowTo': 'ToolBOS_HowTo_Git' }

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks if the package is managed via SVN.
        """
        logging.debug( 'looking for VCS repository information' )


        if details.gitFound:
            logging.debug( 'Git found: %s', details.gitRepositoryRoot )
            result = ( OK, 1, 0, 'Git repository found' )

        elif details.svnFound:
            logging.debug( 'SVN found: %s', details.svnRepositoryURL )
            result = ( OK, 1, 0, 'SVN repository found' )

        else:
            result = ( FAILED, 0, 1, 'no VCS information found' )

        return result


class QualityRule_GEN11( AbstractQualityRule ):

    brief       = '''Consider managing bugs and feature requests via JIRA
issue tracker.'''

    sqLevel     = frozenset()

    def __init__( self ):
        super( AbstractQualityRule, self ).__init__()

        url = getConfigOption( 'bugtrackURL' )

        self.description = '''Instead of sending bug reports and feature requests via
e-mails please consider using JIRA.

It helps tracking issues, allows leaving comments and posting files, so that
all involved people have the same knowledge about the issue.

Within HRI-EU JIRA is reachable at:
[%(url)s](%(url)s)

Remote access is also possible upon request, please contact system
administration in this case.''' % { 'url': url }


class QualityRule_GEN12( AbstractQualityRule ):

    brief       = '''Applications and library functions should have a
deterministic mode, i.e. the possiblity to start with a defined random
state.'''

    description = '''A deterministic runtime behavior simplifies debugging,
and might be necessary for precise benchmarking.

Therefore non-deterministic functions (those which do not return the same
result for equal input data) should be set into a deterministic mode. For
example, when random numbers are involved, there should be a possibility to
predefine the seed or to assign some fixed value that should be taken instead.
'''

    sqLevel     = frozenset()


class QualityRule_C01( AbstractQualityRule ):

    brief       = '''Prefer returning status codes (or throwing exceptions
in C++) over `exit()` within the code.'''

    description = '''As a rule of thumb, C/C++ functions should hardly
directly terminate the application. Prefer returning a status code indicating
the error, or throw an exception in C++, so that the caller at least has a
chance to appropriately handle it.

Mind that the caller might be a 3rd party application such as *Matlab*.
In such case the `exit()` will terminate the whole application, potentially
causing data loss or inconsistent states.'''

    goodExample = '''
    int doSomething( x, y )
    {
        if( x < 0 || y < 0 )
        {
            return -1;
        }
        else
        {
            return x * y;
        }
    }
'''

    badExample  = '''
    int doSomething( x, y )
    {
        if( x < 0 || y < 0 )
        {
            printf( "Invalid input values!\\n" );
            exit( -1 );
        }
        else
        {
            return x * y;
        }
    }
'''

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks if exit() and friends are used.
        """
        logging.debug( 'looking for direct exit() in code' )
        failed = 0
        passed = 0

        regexpExit1 = re.compile( '\sexit\s*\(' )
        regexpExit2 = re.compile( '\s_exit\s*\(' )
        regexpAbort = re.compile( '\sabort\s*\(' )

        for filePath in files:
            if filePath.find( '/bin/' ) != -1 or \
               filePath.find( '/examples/' ) != -1 or \
                filePath.find( '/test/' ) != -1:

                logging.debug( '%s: exit() in main programs permitted', filePath  )
                continue

            if filePath.endswith( '.c' ) or filePath.endswith( '.cpp' ) or \
               filePath.endswith( '.hpp' ) or filePath.endswith( '.inc' ):

                content = FastScript.getFileContent( filePath )

                if regexpExit1.search( content ):
                    logging.info( 'C01: exit() found in %s:1', filePath )
                    failed += 1
                elif regexpExit2.search( content ):
                    logging.info( 'C01: _exit() found in %s:1', filePath )
                    failed += 1
                elif regexpAbort.search( content ):
                    logging.info( 'C01: abort() found in %s:1', filePath )
                    failed += 1
                else:
                    passed += 1


        if failed == 0:
            result = ( OK, passed, failed,
                       'no usage of exit() or abort() found' )
        else:
            result = ( FAILED, passed, failed,
                       'exit() and/or abort() found' )

        return result


class QualityRule_C02( AbstractQualityRule ):

    brief       = 'C header files should ensure C++ linkage compatibility.'

    description = '''For compatibility with C++, all function prototypes in C
header files should be surrounded by macros to ensure C linkage in case of C++.

This pro-actively enables using this header file in a possible future C++
context, without any sideeffects.

Without these macros the code will not link in C++ context.'''

    goodExample = '''
*plain C:*

    #ifdef __cplusplus
    extern "C" {
    #endif
    ...
    #ifdef __cplusplus
    }
    #endif

*using macros from ToolBOS SDK:*

    ANY_BEGIN_C_DECLS
    ...
    ANY_END_C_DECLS
'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        logging.debug( 'checking C header files for linkage guards' )

        binDir            = os.path.join( details.topLevelDir, 'bin' )
        ifdefExpr         = r'#\s*if\s+defined\(\s*__cplusplus\s*\)\s+extern\s+"C"\s+\{\s+#\s*endif'
        ifdefinedExpr     = r'#\s*ifdef\s+__cplusplus\s+extern\s+"C"\s+\{\s+#\s*endif'
        toolbosMacroExpr  = r'ANY_BEGIN_C_DECLS.*ANY_END_C_DECLS'
        ifdefRegex        = re.compile( ifdefExpr )
        ifDefinedRegex    = re.compile( ifdefinedExpr )
        toolbosMacroRegex = re.compile( toolbosMacroExpr )
        passed            = 0
        failed            = 0

        patterns          = { ifdefExpr       : ifdefRegex,
                              ifdefinedExpr   : ifDefinedRegex,
                              toolbosMacroExpr: toolbosMacroRegex }

        platform = getHostPlatform()
        headerAndLanguageMap = CMake.getHeaderAndLanguageMap( platform )

        if details.isCppPackage():
            result = ( NOT_APPLICABLE, passed, failed,
                       'C++ package does not need linkage guards' )
            return result

        try:

            for filePath in files:
                fname, fext = os.path.splitext( filePath )

                if fext == '.h' and not filePath.startswith( binDir ):

                    contents = FastScript.getFileContent( filePath )
                    found    = False

                    logging.debug( 'checking: %s', filePath )

                    for expr, regex in patterns.items():
                        if regex.search( contents ):
                            logging.debug( 'pattern found: %s', expr )
                            found = True
                        else:
                            logging.debug( 'pattern not found: %s', expr )


                    if found:
                        logging.debug( 'passed: %s', filePath )
                        passed += 1
                    else:
                        logging.info( 'failed: %s', filePath )
                        failed += 1

        except EnvironmentError as e:
            logging.error( e )
            return FAILED, passed, failed, e


        if failed == 0:
            result = ( OK, passed, failed,
                       'all headers contain proper linkage guards' )
        else:
            result = ( FAILED, passed, failed,
                       'invalid C header files found' )

        return result


class QualityRule_C03( AbstractQualityRule ):

    brief       = '''Macro names must be uppercase and prefixed by the package
name. The expression must be put in parentheses.'''

    description = '''Macros traditionally are written `UPPERCASE` to clearly
identify them to be compile-time resolved.

Each macro should be prefixed with the package name, f.i. `MYPACKAGE_XY`
(or the module name). Defining a macro as just XY may lead to clashes.

Words in long macro names should be splitted by underscore (`_`), e.g.
`MYPACKAGE_MAX_ITERATIONS`.

Expressions should be put in parentheses so that the operator precedence is
clear. Otherwise using the macro may have sideeffects:

    #define MYPACKAGE_MACRO(a) a * 11
    [...]
    int b = MYPACKAGE_MACRO( 1 + 2 );

b, instead of being 33 like it should, would actually be replaced with
`int b = 1 + 2 * 11` which is 23 and not 33.'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks that C/C++ macros are prefixed with the package or
            module name (for scoping), e.g.:

                good:
                #define BERKELEYSOCKET_BUFFLEN_DEFAULT ( 255 )

                bad:
                #define BUFFLEN_DEFAULT ( 255 )

            Macros from the Standard Library and other toolkits usually do not
            fit to such conventions. Therefore we define a whitelist for such
            known macros here.
        """
        logging.debug( 'checking C/C++ macro prefixes' )
        passed               = 0
        failed               = 0
        whitelist            = frozenset( [ '__CL_ENABLE_EXCEPTIONS' ] )
        platform             = getHostPlatform( )

        # ensure the package has been built
        bst = BuildSystemTools.BuildSystemTools()

        if not os.path.exists( bst.getBuildDir() ):
            logging.debug( 'build dir. not found, performing build configuration' )
            bst.compile()

        headerAndLanguageMap = CMake.getHeaderAndLanguageMap( platform )
        logging.debug( 'language map: %s', headerAndLanguageMap )

        try:
            for filePath in files:
                _, ext = os.path.splitext( filePath )
                if ext.lower( ) in ('.h', '.hpp', 'hh', 'hxx'):
                    basename     = os.path.basename( filePath )
                    module       = os.path.splitext( basename )[0]
                    moduleUpper  = module.upper()
                    packageUpper = details.packageName.upper()

                    parser = createCParser( filePath, details, headerAndLanguageMap )

                    if not parser:
                        continue

                    for define in parser.localMacros:

                        if define in whitelist:
                            logging.debug( 'found whitelisted: %s', define )
                            continue

                        # ignore underscores (this could be made more strict in
                        # future --> remove this replacement)
                        defineShort = define.replace( '_', '' )


                        # defines must start uppercase
                        if not defineShort[0].isupper():
                            logging.info( 'C03: %s: define "%s" is not uppercase',
                                          filePath, define )
                            failed += 1

                        # check if define starts with package or module name
                        elif define.find( moduleUpper ) == -1 and \
                             define.find( packageUpper ) == -1:

                            if moduleUpper == packageUpper:
                                logging.info( 'C03: %s: define "%s" not prefixed with "%s"',
                                              filePath, define, packageUpper )
                            else:
                                logging.info( 'C03: %s: define "%s" not prefixed with "%s" or "%s"',
                                              filePath, define, packageUpper, moduleUpper )

                            failed += 1
                        else:
                            passed += 1

            if failed == 0:
                result = ( OK, passed, failed,
                           'all C/C++ macros prefixed with module name' )
            else:
                result = ( FAILED, passed, failed,
                           'invalid C/C++ macro names found' )

        except EnvironmentError as e:
            logging.error( e )
            result = ( FAILED, passed, failed, e )


        return result


class QualityRule_C04( AbstractQualityRule ):

    brief       = '''A function without parameters must be declared with a
`void` argument list.'''

    description = '''A `void` argument list indicates that the function does
not take arguments. Hence the compiler can check for invalid calls where
unexpected parameters are supplied.

If `void` isn't specified, the compiler does not make any assumptions.
Hence the function could accidently be called with arguments.

This might lead to error if a function that originally had taken parameters
has been changed (to not take parameters anymore) and the caller was not
updated and still passes parameters.'''

    goodExample = '''   int Foo_run( void );'''

    badExample  = '''   int Foo_run();'''

    seeAlso     = { 'CERT DCL20-C':
                    'https://www.securecoding.cert.org/confluence/display/c/DCL20-C.+Explicitly+specify+void+when+a+function+accepts+no+arguments' }

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        logging.debug( 'looking for function prototypes with no information about the arguments' )
        platform             = getHostPlatform( )
        headerAndLanguageMap = CMake.getHeaderAndLanguageMap( platform )
        failed               = 0
        passed               = 0

        try:

            for filePath in files:
                _, ext = os.path.splitext( filePath )
                if ext in C_CPP_FILE_EXTENSIONS:
                    parser = createCParser( filePath, details, headerAndLanguageMap )

                    if not parser:
                        continue

                    protos = parser.getFunctionPrototypesWithoutParameters( filePath )

                    if protos:
                        failed += 1

                        for proto, line in protos:
                            logging.info( 'C04: %s:%d - function %s declared without information about the arguments',
                                          filePath, line, proto )
                    else:
                        passed += 1

            if failed == 0:
                result = ( OK, passed, failed,
                           'all files OK' )
            else:
                result = ( FAILED, passed, failed,
                           'files with functions declared without parameters found' )

        except EnvironmentError as e:
            logging.error( e )
            result = ( FAILED, passed, failed, e )


        return result


class QualityRule_C05( AbstractQualityRule ):

    brief       = '''Header files must be protected against multiple inclusion
using inclusion guards.'''

    description = '''Keeping track of file inclusions in larger systems
(without any re-ocurrence or cyclic dependencies) might become very difficult.

It is a common practice to pro-actively equip each header file with inclusion
guards so that symbols won't be duplicated.

Repeated header file inclusion may lead to unintended macro redefinition,
and other compile errors.'''

    goodExample = '''
    #ifndef FOO_H
    #define FOO_H
    ...
    #endif
'''

    seeAlso     = { 'CERT PRE06-CPP':
                    'https://www.securecoding.cert.org/confluence/display/cplusplus/PRE06-CPP.+Enclose+header+files+in+an+inclusion+guard' }

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks that C/C++ header files contain inclusion guards, f.i.

                #ifndef BERKELEYSOCKET_H
                #define BERKELEYSOCKET_H
                ...
                #endif
        """
        logging.debug( 'checking header file inclusion guards' )

        blacklist = frozenset( [ 'documentation.h' ] )

        for filePath in files:
            if filePath.endswith( '.h' ) or filePath.endswith( '.hpp' ):
                fileName    = os.path.basename( filePath )
                module      = os.path.splitext( fileName )[0]
                moduleUpper = module.upper()
                content     = FastScript.getFileContent( filePath )

                if fileName in blacklist:
                    # ignore / do not check whitelisted files
                    continue

                # Note that we are searching with regexp for a more relaxed
                # string with possible leading namespace name, but we print
                # a stricter safeguard name in case it was not found,
                # see JIRA ticket TBCORE-918
                #
                # allowed:  #ifndef DOT_PACKAGENAME_H
                #
                # where "DOT_" is an optional namespace prefix

                safeguard   = '#ifndef %s_H' % moduleUpper
                regexp      = re.compile( '#ifndef\s\S*?%s_H' % moduleUpper )

                if regexp.search( content ):
                    self.passed += 1
                else:
                    logging.info( "C05: %s: safeguard '%s' not found",
                                  filePath, safeguard )
                    self.failed += 1


        if self.failed == 0:
            result = ( OK, self.passed, self.failed,
                       'C/C++ header file inclusion guards valid' )
        else:
            result = ( FAILED, self.passed, self.failed,
                       'C/C++ safeguards missing' )

        return result


class QualityRule_C06( AbstractQualityRule ):

    brief       = '''Header files should not expose inline functions as
public interface. The result after changing the implementation is undefined.'''

    description = '''Functions declared as `inline` might (!) be put in-place
by the compiler, rather than invoking a function call. This is a mean to
improve performance when repetitively calling small functions.

Similar to macros, the code gets duplicated in the caller. Therefore public
functions of a library should not be declared as inline otherwise it might
happen that an old binary (that was not recompiled in the meanwhile) still
contains the old logic.

Even worse, inlining is just a request to the compiler which might decide to
inline or not depending on the code situation. This might result in a mixture
of code variants.'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks that public C/C++ functions are not exposed as 'inline'.
        """
        logging.debug( "looking for public functions declared 'inline'" )
        passed = 0
        failed = 0

        for filePath in files:
            if filePath.endswith( '.h' ) or filePath.endswith( '.hpp' ):
                content = FastScript.getFileContent( filePath )

                if content.find( 'inline' ) != -1:
                    logging.info( "C06: %s: public API should not be declared 'inline'",
                                  filePath )
                    failed += 1
                else:
                    passed += 1

        if failed == 0:
            result = ( OK, passed, failed,
                       "no public function declared 'inline'" )
        else:
            result = ( FAILED, passed, failed,
                       'public functions declared "inline"' )

        return result


class QualityRule_C07( AbstractQualityRule ):

    brief       = '''Logging should be done using `ANY_LOG()` macros.'''

    description = '''Logging is essential for tracing progress information,
and often also for debugging.

Applications shall use one consistent way of logging so that the user can
easily read and/or post-process the console output.

Good logging frameworks allow selective enabling of logging for certain
submodules.

Due to usage of the `ANY_LOG()` macro (and friends) throughout ToolBOS and many
HRI-EU libraries, it is highly recommended to stick with it for consistency
reasons. And consistency is a soft skill for good quality software.'''

    goodExample = '''
    #include <Any.h>

    ANY_LOG( 0, "Hello, World!", ANY_LOG_INFO );
    ANY_TRACE( 0, "%d", x );
'''

    seeAlso     = { 'Any.h API documentation':
                    'Any_About',

                    'CERT ERR00-CPP':
                    'https://www.securecoding.cert.org/confluence/display/cplusplus/ERR00-CPP.+Adopt+and+implement+a+consistent+and+comprehensive+error-handling+policy' }

    sqLevel     = frozenset()


class QualityRule_C08( AbstractQualityRule ):

    brief       = '''Use datatypes and functions which support both 32 and
64 bit environments.'''

    description = '''HRI-EU software is used on a wide range of computer
systems, from small ECUs to High-End clusters.

In order to pro-actively support possible future portings to other platforms,
it is a good practice to use architecture-independent datatypes.

For instance, rather than using signed int or long, use appropriate
platform-agnostic type aliases. The ToolBOSCore library defines a set of such
types, f.i. `BaseI16` or `BaseI64`, defined in `Base.h.`'''

    goodExample = '''\t
    #include <Base.h>
    [...]
    BaseUI64 x = 42000000000              // 42 billion;'''

    badExample  = '''\tunsigned long long x = 42000000000;   // 42 billion'''

    seeAlso     = { 'Base.h API documentation':
                    'Base_About',

                    'CERT NUM03-J':
                    'https://www.securecoding.cert.org/confluence/display/java/NUM03-J.+Use+integer+types+that+can+fully+represent+the+possible+range+of++unsigned+data',

                    'CERT INT31-C':
                    'https://www.securecoding.cert.org/confluence/display/c/INT31-C.+Ensure+that+integer+conversions+do+not+result+in+lost+or+misinterpreted+data',

                    'CERT INT08-C':
                    'https://www.securecoding.cert.org/confluence/display/seccode/INT08-C.+Verify+that+all+integer+values+are+in+range' }

    sqLevel     = frozenset()


class QualityRule_C09( AbstractQualityRule ):

    brief       = '''Package can be built using `BST.py.`'''

    description = '''For ensuring that our software is compilable and
unittests pass, HRI-EU software is regularly being rebuilt and unittests get
executed.

As a prerequisite for this, the Nightly Build process must be able to compile
arbitrary packages and invoke their unittests. The `BST.py` serves as generic
interface for both humans and machines.

Hence, please ensure that your package is compatible with `BST.py`.'''

    seeAlso     = { 'BST.py documentation':
                    'ToolBOS_Util_BuildSystemTools',

                    'About Continous Integration':
                    'ToolBOS_UseCases_CIA' }

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks that package can be built using BST.py.
        """
        logging.debug( "check if package can be built using BST.py" )

        oldcwd = os.getcwd()
        output = six.StringIO() if Any.getDebugLevel() <= 3 else None

        FastScript.changeDirectory( details.topLevelDir )

        bst = BuildSystemTools.BuildSystemTools()
        bst.setStdOut( output )
        bst.setStdErr( output )
        status = bst.compile()

        FastScript.changeDirectory( oldcwd )

        if status is True:
            result = ( OK, 1, 0,
                       'package can be built using BST.py' )
        else:
            result = ( FAILED, 0, 1,
                       "package cannot be built using BST.py" )

        return result


class QualityRule_C10( AbstractQualityRule ):

    brief       = '''Use a static source code analyzer (f.i. Klocwork
Insight).'''

    description = '''Compilers do find code issues within functions, such as
using variables that potentially are not initialized. This is referred to as
*intra-functional* checks.

However, static source code analyzers perform much, much more checks. Good
analyzers do *inter-functional* checks and are capable of tracking really
complex code scenarios.

For instance you may find potential `NULL` pointer dereferences, arithmetic
problems (e.g. division by zero), or possible execution paths that lead to
resource leaks.

Such inter-functional checks are complicated and time-consuming, but please
once in a while inspect your code using Klocwork.'''

    seeAlso     = { 'Klocwork HowTo':
                    'ToolBOS_HowTo_Klocwork' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Execute the Klocwork source code analyzer in CLI mode.
        """
        from subprocess import CalledProcessError

        logging.debug( 'performing source code analysis using Klocwork' )
        passed = 0
        failed = 0
        output = six.StringIO()
        error  = False
        kwDir  = tempfile.mkdtemp( prefix='klocwork-' )

        # Klocwork operates on the whole project, hence we cannot compute
        # failed/passed files like this, instead later on we parse the output.

        try:
            Klocwork.createLocalProject( kwDir, output, output )
            Klocwork.codeCheck( kwDir, output, output )

            if Any.getDebugLevel() > 3:
                logging.info( 'output:\n%s', output.getvalue() )

            defects = Klocwork.parseCodeCheckResult( output.getvalue() )

            if defects:
                for item in defects:
                    logging.info( 'C10: %s:%s: %s [%s]', *item )
                    failed += 1

        except ( AssertionError, CalledProcessError, EnvironmentError,
                 RuntimeError ) as details:
            logging.error( 'C10: %s', details )
            failed += 1
            error   = True


        FastScript.remove( kwDir )

        if failed == 0:
            result = ( OK, passed, failed,
                       'no defects found by Klocwork' )
        else:
            if error:
                result = ( FAILED, 0, 1,
                           'unable to run code analysis with Klocwork' )
            else:
                result = ( FAILED, passed, failed,
                           'Klocwork found %d defects' % failed )

        return result


class QualityRule_C11( AbstractQualityRule ):

    brief       = '*removed*'


class QualityRule_C12( AbstractQualityRule ):

    brief       = '''Heap-memory explicitly allocated with `malloc()` or
`new` (or wrappers thereof), must be explicitly released using `free()` or
`delete` (or corresponding wrappers).
'''

    description = '''If resources are not explicitly released then it is
possible for a failure to occur due to exhaustion of those resources.
Releasing resources as soon as possible reduces the possibility that
exhaustion will occur.

The check function for this rule invokes Valgrind on all executables listed
in the SQ_12 variable in pkgInfo.py, e.g.:

    SQ_12 = [ 'bin/${MAKEFILE_PLATFORM}/main',
              'bin/${MAKEFILE_PLATFORM}/main foo --bar' ]

Please specify a list of commands, including arguments (if any), that
shall be analyzed by the check routine.

The paths to the executables are interpreted as relative to the package root.

Specify an empty list if really nothing has to be executed.'''

    seeAlso     = { 'MISRA-2012 rule 22.1': None }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Check for memory leaks.
        """
        if details.hasMainProgram( files ):
            logging.info( 'main program(s) found' )

            # look-up executables bin/<platform>/ directory
            binFiles = self._getBinFiles( details )
            logging.debug( 'executable(s) found in %s directory: %s',
                           details.binDirArch, binFiles )

        else:
            logging.info( 'no main program(s) found' )

            logging.info( '%s: possibly not C/C++ package' % details.canonicalPath )
            result = ( OK, 0, 0,
                       'check not applicable' )

            return result

        # get SQ-settings from pkgInfo.py
        sqSettings = self._getSQSettings( details )
        logging.debug( "'sqCheckExe' settings from pkgInfo.py: %s",sqSettings )

        if sqSettings is None:
            msg    = "no 'sqCheckExe' settings found in pkgInfo.py (please see C12 docs)"
            result = ( FAILED, 0, 1, msg )

            return result

        # verify that we have:
        #     - one executable present for each setting (to check if compilation was forgotten)
        #     - one setting is present for each executable (to check if developer was lazy ;-)

        validityCheck = self._validityCheck( binFiles, sqSettings )

        if validityCheck[0] == FAILED:
            shortText = validityCheck[3]
            logging.debug( shortText )

            return validityCheck

        # finally run Valgrind
        runValgrindResult = self._runValgrind( sqSettings, details )

        return runValgrindResult


    def _getSQSettings( self, details ):
        Any.requireIsInstance( details, PackageDetector )

        try:
            sqSettingsTmp = details.sqCheckExe
            Any.requireIsNotNone( sqSettingsTmp )
            Any.requireIsList( sqSettingsTmp )

            sqSettings = list ( map( FastScript.expandVars, sqSettingsTmp ) )

            return sqSettings

        except ( IOError, ValueError, TypeError, OSError ) as e:
            logging.error( e )
            logging.error( 'issue with retrieving SQ settings from pkgInfo')

            return None

        except AssertionError:
            logging.error( "no 'sqCheckExe' found in pkgInfo.py (please see C12 docs)" )

            return None


    def _getBinFiles( self, details ):
        Any.requireIsInstance( details, PackageDetector )

        binFilesTmp = FastScript.getFilesInDir( details.binDirArch )
        Any.requireIsList( binFilesTmp )
        binFiles = []

        if not binFilesTmp:
            logging.error( 'no executables found in %s, forgot to compile?',
                           details.binDirArch )

            return binFiles

        platform = getHostPlatform()

        for binFile in binFilesTmp:
            tmp = os.path.join( 'bin', platform, binFile )
            binFiles.append(tmp)

        return binFiles


    def _validityCheck( self, binFiles, commandLines ):
        Any.requireIsList( binFiles )
        Any.requireIsList( commandLines )

        commands = []

        for cmdLine in commandLines:

            tmp = shlex.split( cmdLine )
            command = tmp[0]
            commands.append( command )

        # TODO: check matching

        for command in commands:
            if not os.path.exists( command ):
                logging.error( "The path specified in pkgInfo.py 'sqCheckExe' key does not exist: %s'. "
                               "Is the package compiled?", command )

                result = ( FAILED, 0, 1,
                         '%s specified in pkgInfo.py does not exist' % command )

                return result

        for binFile in binFiles:
            if binFile not in commands:
                logging.warning("%s executable was found. "
                                "but no sqCheckExe setting was specified in pkgInfo.py", binFile)

                result = ( FAILED, 0, 1,
                           "sqCheckExe setting for executable '%s' not specified in pkgInfo.py" % binFile )

                return result

        return OK, 0, 0, 'validity check paas'


    def _runValgrind( self, commandLines, details ):
        passedExecutables = 0
        failedExecutables = 0
        errorMessages     = []

        for command in commandLines:

            logging.info( "C12: checking '%s'", command )

            if Any.getDebugLevel() <= 3:
                stdout = VersionCompat.StringIO()
                stderr = VersionCompat.StringIO()
            else:
                stdout = None
                stderr = None

            try:
                failed, errors = Valgrind.checkExecutable( command, details,
                                                           stdout=stdout, stderr=stderr )
            except subprocess.CalledProcessError as e:
                failed = True
                errors = []

            if failed:
                failedExecutables += 1

                for error in errors:
                    errorMessages.append( 'C12: %s:%s - %s'
                                          % ( error.fname, error.lineno, error.description ) )

                logging.info( "C12: '%s' failed (see verbose-mode for details)", command )

            else:
                passedExecutables += 1
                logging.info( "C12: '%s successfully finished", command )

        for error in errorMessages:
            logging.error( error )

        if not passedExecutables and not failedExecutables:
            result = ( OK, passedExecutables, failedExecutables,
                       'no executables were checked with Valgrind' )
        elif not failedExecutables:
            result = ( OK, passedExecutables, failedExecutables,
                       'no defects found by Valgrind' )
        else:
            result = ( FAILED, passedExecutables, failedExecutables,
                       'Valgrind found %d defect%s' % ( failedExecutables,
                                                        's' if failedExecutables > 1 else '' ) )

        return result


class QualityRule_C13( AbstractQualityRule ):

    brief       = '''Code should compile without warnings, even at strict
compiler settings.'''

    description = '''Code should compile without warnings, even at strict
compiler settings.

An exception can be made when casting object-pointers to function-pointers
which is required when working with `dlopen()` and friends. This is not
defined in ISO C99 and thus causes compiler warnings.

A common way to suppress such messages is to cast these pointers to `int*`
and back again. But this does not improve anything substantially. We propose
to either keep the warning so that it is obvious that the code is not strictly
ISO C compliant, or explicitly silence the compiler warning in question.'''

    goodExample = '''
    #if defined(__GNUC__)
    #pragma GCC diagnostic ignored "-pedantic"
    #endif
'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class QualityRule_C14( AbstractQualityRule ):

    brief       = '''Minimize the use of global variables.'''

    description = '''Variables and functions should be declared in the
minimum scope from which all references to the identifier are still possible.

When a larger scope than necessary is used, code becomes less readable,
harder to maintain, and more likely to reference unintended variables.

Avoiding cluttering the global name space prevents the variable from being
accidentally (or intentionally) invoked from another compilation unit.'''

    seeAlso     = { 'CERT DCL19-C':
                    'https://www.securecoding.cert.org/confluence/display/CINT/DCL19-C.+Minimize+the+scope+of+variables+and+functions' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class QualityRule_C15( AbstractQualityRule ):

    brief       = '''Unittests should be runnable under Valgrind without
warnings of any sort.'''

    description = '''**Valgrind** is a tool which runs an executable and
during this searches for memory leaks and other issues with memory management.

No issues shall be found during execution of unittests.'''

    seeAlso     = { 'Valgrind HowTo':
                    'ToolBOS_HowTo_Debugging_Memory',

                    'Valgrind Home':
                    'http://www.valgrind.org' }

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )


class QualityRule_PY01( AbstractQualityRule ):

    brief       = '*removed*'


class QualityRule_PY02( AbstractQualityRule ):

    brief       = '''Private class members and methods (name starting with
underscore) must not be accessed from the outside.'''

    description = '''Unlike C++ or Java, Python has no strong concept of
**private** methods. By convention they start with a leading underscore.

Even though there is no technical protection, private methods should not be
called from the outside. Doing it must be considered as wrong usage.'''

    goodExample = '''
    class Foo( object ):

        # public function
        def run( self, details, files ):
            _showMsg( "Hello, World!" )

        def _showMsg( self, msg ):
            print( msg )


    Foo().run()
'''

    badExample = '''
    class Foo( object ):

        # private function
        def _showMsg( self, msg ):
            print( msg )


    Foo()._showMsg( "Hello, World!" )
'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks for access to private class members from outside.
        """
        logging.debug( "checking for access to private members from outside" )
        found  = 0
        regexp = re.compile( '(\w+)\._(\w+)' )

        for filePath in files:
            if filePath.endswith( '.py' ) and os.path.exists( filePath ):
                content = FastScript.getFileContent( filePath, splitLines=True )

                for line in content:
                    tmp = regexp.search( line )

                    if tmp:
                        # Attention: regexp contains one underscore, so we
                        # must check against "_init__" to match "__init__"
                        if tmp.group(1) != 'self' and tmp.group(2) != '_init__':
                            logging.info( 'PY02: %s: access to private member (%s)',
                                          filePath, tmp.group() )
                            found += 1

        if found == 0:
            result = ( OK, 1, 0,
                       'no access to private members from outside' )
        else:
            result = ( FAILED, 0, 1,
                       'found %d accesses to private members from outside' % found )

        return result


class QualityRule_PY03( AbstractQualityRule ):

    brief       = '''Logging should be done using Python's native `logging`
module, evtl. supported by helpers from `Any.py.`'''

    description = '''Logging is essential for tracing progress and information,
and often also for debugging.

Applications shall use one consistent way of logging so that the user can
easily read and/or post-process the console output.

Python features an excellent logging framework, allowing to selectively
enable logging of certain submodules, and writing to different resource types.

For consistency reasons, log messages should only be issued using Python's
native `logging` module.

Those familar with the `ANY_LOG()` and `ANY_REQUIRE()` macro family from the
ToolBOSCore C library might want to use the corresponding Python equivalents.
They map the `ANY_LOG()` / `ANY_REQUIRE()` terminology and usage to Python's
`logging` framework.'''

    goodExample = '''
    # possibility A (native way):

    import logging
    [...]
    logging.info( "Hello, World!" )
    logging.info( 'x=%d', x )


    # possibility B (ANY-equivalent)

    import ToolBOSCore.Util.Any
    [...]
    Any.setDebugLevel( 3 )
    Any.log( 3, "Hello, World!" )
    Any.requireMsg( x == 123, "Oops..." )
    Any.requireIsDir( '/tmp' )
'''

    seeAlso     = { 'Any.py API documentation':
                    'namespaceToolBOSCore_1_1Util_1_1Any' }

    sqLevel     = frozenset()


class QualityRule_PY04( AbstractQualityRule ):

    brief       = '''Prefer throwing exceptions over sys.exit(), os.exit()
                     and os._exit() within the code.'''

    description = '''As a rule of thumb, Python functions should hardly
directly terminate the application. Prefer throwing an exception
(`SystemExit` if necessary), so that the caller at least has a chance to
appropriately handle it.

Mind that the caller might be a C- or Java-program containing a Python
interpreter. In such case the `sys.exit(0)` will terminate the whole
application, potentially causing data loss or inconsistent states.'''

    goodExample = '''
    if not foo:
        raise AssertionError( '...' )
'''

    badExample  = '''
    if not foo:
        sys.exit( -1 )
'''

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )

    class FuncCallVisitor( ast.NodeVisitor ):
        def __init__( self ):
            self._name  = collections.deque()
            self.lineno = '-'

        @property
        def name( self ):
            return '.'.join( self._name )

        @name.deleter
        def name( self ):
            self._name.clear()

        def visit_Attribute( self, node ):
            if node.attr == 'exit' and node.value.id == 'sys' or \
               node.attr == 'exit' and node.value.id == 'os' or \
               node.attr == '_exit' and node.value.id == 'os':

                self._name.appendleft( node.attr )
                self._name.appendleft( node.value.id )
                self.lineno = node.lineno

    def getExitCalls( self, code ):
        funcCalls = []

        tree = ast.parse( code )
        for node in ast.walk( tree ):
            if isinstance( node, ast.Call ):
                callvisitor = self.FuncCallVisitor()
                callvisitor.visit( node.func )
                if callvisitor.name:
                    funcCalls.append( (callvisitor.name, callvisitor.lineno) )
        return funcCalls

    def run( self, details, files ):
        """
            Checks for call to sys.exit() in files other than bin/*.py
        """
        logging.debug( "checking for calls to sys.exit(), os.exit() and os._exit()" )
        passed    = 0
        failed    = 0
        syntaxErr = 0

        binDir = os.path.join( details.topLevelDir, 'bin' )

        for filePath in files:
            if filePath.endswith( '.py' ) and not filePath.startswith( binDir ):

                code = FastScript.getFileContent( filePath )

                try:
                    exitCalls = self.getExitCalls( code )
                except SyntaxError as e:
                    logging.error( 'PY04: %s: syntax error in line %d',
                                   filePath, e.lineno )
                    syntaxErr += 1
                    continue

                if not exitCalls:
                    passed += 1
                else:
                    # logging.info(exitCalls)
                    for call in exitCalls:
                        logging.info( 'PY04: %s:%s: found %s() call',
                                      filePath, call[1], call[0] )
                    failed += len( exitCalls )



        if syntaxErr:
            msg    = 'syntax error(s) in %d files' % syntaxErr
            status = FAILED

        elif failed:
            msg    = 'found %d exit() calls' % failed
            status = FAILED

        else:
            msg    = 'no exit() calls found'
            status = OK

        return status, passed, failed, msg


class QualityRule_PY05( AbstractQualityRule ):

    brief       = '''Use a static source code analyzer.'''

    description = '''The **PyCharm IDE** contains a static source code
analyzer for Python. The analyzer can also be used separately from commandline.

It reports problems in your Python scripts, such as wrong API usage,
incompatibility with certain Python versions, or questionable coding practics.

Please regularly inspect your scripts using PyCharm. The tool is installed
under `${SIT}/External/PyCharmPro`.'''

    seeAlso     = { 'PyCharm Home':
                    'https://www.jetbrains.com/pycharm' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Execute the PyCharm source code analyzer in batch-mode for each
            *.py file.
        """
        logging.debug( 'performing source code analysis using PyCharm' )
        passed = 0
        failed = 0
        error  = False


        # Shortcut: Ignore if 'pkgInfo.py' is the only Python file in package
        # (e.g. for build- or SQ-settings). This file hardly will contain
        # major flaws, but in contrast the check often fails because of
        # missing license (see TBCORE-1199).

        isPythonFile    = lambda s: s.endswith( '.py' )
        isPkgInfo       = lambda s: os.path.basename( s ) == 'pkgInfo.py'
        numberOfPyFiles = list( map( isPythonFile, files ) ).count( True )
        pkgInfoFound    = filter( isPkgInfo, files )

        if numberOfPyFiles == 1 and pkgInfoFound:
            msg = 'no Python files (besides pkgInfo.py)'
            logging.debug( 'PY05: %s', msg )
            return OK, 1, 0, msg


        # PyCharm's code inspector works on the whole project, hence we
        # cannot compute failed/passed files like this. We can only consider
        # the whole test passed or not depending on if some special output
        # files have been generated or not.

        try:
            rawData = PyCharm.codeCheck()
            defects = PyCharm.parseCodeCheckResult( rawData )

            if defects:
                for item in defects:
                    if not item[0].startswith( 'doc/html' ):
                        logging.info( 'PY05: %s:%s: %s', *item )
                        failed += 1
        except RuntimeError as details:
            logging.error( 'PY05: %s', details )
            failed += 1
            error   = True


        if failed == 0:
            result = ( OK, passed, failed,
                       'no defects found' )
        else:
            if error:
                result = ( FAILED, 0, 1,
                           'unable to run code analysis with PyCharm' )
            else:
                result = ( FAILED, passed, failed,
                           'found %d defects' % failed )

        return result


class QualityRule_PY06( AbstractQualityRule ):

    brief       = '''Mind compatibility with Python versions 2.6 to 3.x'''

    description = '''Python comes in various language versions, featuring
different included packages or language constructs. However the install base
is quite heterogeneous.

Hence developers should pro-actively care that scripts are compatible with a
range of Python versions. At least compatibility with 2.6, 2.7 and 3.4 is
desired.

The **PyCharm IDE** can be configured to annotate code incompatible with
certain versions of Python. The tool is installed under
`${SIT}/External/PyCharmPro`.'''

    seeAlso     = { 'PyCharm Home':
                    'https://www.jetbrains.com/pycharm' }

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )


class QualityRule_MAT01( AbstractQualityRule ):

    brief       = '*removed*'


class QualityRule_MAT02( AbstractQualityRule ):

    brief       = '''Follow the suggestions of the Matlab code-checker. Write
a comment in case you have to diverge from the suggestion.'''

    description = '''Please clearly state why it is not advisable in the
specific case to follow the Matlab code-checker.'''

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Execute the Matlab source code analyzer in batch-mode for each
            *.m file.
        """
        logging.debug( 'performing source code analysis using Matlab' )
        passed = 0
        failed = 0
        cwd    = os.getcwd()
        error  = False

        for filePath in files:
            if filePath.endswith( '.m' ):
                logging.debug( 'checking %s...', filePath )
                defects = None

                try:
                    defects = Matlab.codeCheck( filePath )
                except RuntimeError as details:
                    logging.error( 'MAT02: %s', details )
                    failed += 1
                    error   = True


                relPath = os.path.relpath( filePath, cwd )

                if defects:
                    for item in defects:
                        lineNumber = item[0]
                        message    = item[1]
                        logging.info( 'MAT02: %s:%s: %s', relPath, lineNumber, message )

                    failed += 1

                else:
                    logging.debug( '%s: OK', filePath )
                    passed += 1

        if failed == 0:
            result = ( OK, passed, failed,
                       'no defects found' )
        else:
            if error:
                result = ( FAILED, 0, 1,
                           'unable to run code analysis with Matlab' )
            else:
                result = ( FAILED, passed, failed,
                           'found %d defects' % failed )

        return result


class QualityRule_MAT03( AbstractQualityRule ):

    brief       = '''Avoid unintentional shadowing, i.e. function names should
be unique.'''

    description = '''Shadowing increases the possibility of unexpected
behavior. Check with `which -all` or `exist`.'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class QualityRule_MAT04( AbstractQualityRule ):

    brief       = '''Loop variables should be initialized immediately before
the loop.'''

    description = '''Initializing loop variables just before the loop is a
good practice to avoid massive slow-down and unexpected values in case the
loop does not execute for all possible indices.'''

    goodExample = '''
    result = zeros(nEntries,1);

    for i = 1:nEntries
        result(i) = foo(i)
    end
'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class QualityRule_MAT05( AbstractQualityRule ):

    brief       = '''Function header comments should support the use of
`help` and `lookfor`.
'''

    description = '''The `help` command prints the first contiguous block of
comments; `lookfor` searches the first comment line of all `*.m`-files on the
path.'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class QualityRule_DOC01( AbstractQualityRule ):

    brief       = '''The main functionality (why this package exists) should
be briefly documented.'''

    description = '''Other people should be able to roughly understand what
the package contains, and if it might be of interest for them.

Basic documentation can also programmatically be searched for keywords, e.g.
in case you don't precisely remember the name of a package anymore.

Documentation should be maintained under one of the following locations:

* ./README.md (recommended)
* src/packageName.h
* src/documentation.h
* doc/documentation.h
* doc/Mainpage.dox
* doc/Mainpage.md
'''

    goodExample = '''
    * for C / C++ projects:*
    /*!
     * \mainpage
     *
     * This package contains a coffee machine implemented for various
     * operating systems. On Linux and OS X run "make coffee", on Android
     * just start the MakeCoffee app.
     *
     * \\attention The MakeCoffee Windows GUI may crash at start-up.
     *            In this case please install the latest Microsoft Visual
     *            runtime libraries, the .NET framework (v. 3.0 or later),
     *            Internet Exploder 10.0 and DirectX update KB299764.
     *
     * \\author Bill Gates
     * \\author Linus Torvalds (current maintainer)
     * \\author Steve Jobs
     * \\author Lerry Page
     */

Note that Matlab-packages are documented using `matdoc` instead of `doxygen`.
Hence a doxygen mainpage is not needed in such case.
'''

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks if package has documentation in either of the following locations:
              * ./README.md
              * src/<PackageName>.h
              * src/documentation.h
              * doc/documentation.h
              * doc/Mainpage.md
              * doc/html/index.html
        """
        if details.isMatlabPackage():
            logging.debug( 'Matlab package detected, looking for HTML documentation' )

            # Matlab-packages do not contain a doxygen mainpage, hence only
            # check for existence of index.html after doc-build

            DocumentationCreator( details.topLevelDir ).generate()

            indexPath = os.path.join( details.topLevelDir, 'doc/html/index.html' )
            logging.debug( 'looking for documentation in: %s', indexPath )
            found     = os.path.exists( indexPath )

            if found:
                result = ( OK, 1, 0, 'documentation (index.html) found' )
            else:
                result = ( FAILED, 0, 1, 'documentation (index.html) found' )

        else:
            # search for doxygen mainpage

            found      = False
            docDir     = os.path.join( details.topLevelDir, 'doc' )
            srcDir     = os.path.join( details.topLevelDir, 'src' )

            candidates = ( os.path.join( srcDir, details.packageName, '__init__.py' ),
                           os.path.join( srcDir, '__init__.py' ),
                           os.path.join( srcDir, 'documentation.h' ),
                           os.path.join( srcDir, details.packageName + '.h' ),
                           os.path.join( docDir, 'Mainpage.md' ),
                           os.path.join( docDir, 'Mainpage.dox' ),
                           os.path.join( docDir, 'documentation.h' ),
                           os.path.join( docDir, 'html', 'index.html' ),
                           os.path.join( details.topLevelDir, 'README.md'),)

            search     = 'mainpage'
            fileList = ( os.path.join( docDir, 'Mainpage.md' ),
                         os.path.join( docDir, 'Mainpage.dox' ),
                         os.path.join( docDir, 'documentation.h' ),
                         os.path.join( srcDir, 'documentation.h' ),
                         os.path.join( srcDir, details.packageName + '.h' ) )

            for filePath in candidates:
                logging.debug( 'looking for documentation in: %s', filePath )

                if os.path.exists( filePath ):
                    found = True
                    if filePath in fileList:

                        content = FastScript.getFileContent( filePath )

                        if content.find( search ) != -1:
                            logging.debug( '%s: mainpage section found', filePath )
                            found = True
                            break
                        else:
                            found = False
                            logging.debug( '%s: mainpage section not found', filePath )

            if found:
                result = ( OK, 1, 0, 'documentation found' )
            else:
                result = ( FAILED, 0, 1, 'documentation not found' )

        return result


class QualityRule_DOC02( AbstractQualityRule ):

    brief       = '''All public entities must be documented.'''

    description = '''Each function, class, method, macro, or datatype which
is publicly accessible must contain a basic description / explaination what
it is about.

Preferrably both arguments and return value (if any) should be documented.

For redundant cases, doxygen's `\copydoc` command should be considered. This
command duplicates documentation at other locations, to avoid physical
duplication (for consistency reasons).'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class QualityRule_DOC03( AbstractQualityRule ):

    brief       = '''Provide simple example programs to demonstrate basic
usage.'''

    description = '''Newcomers should quickly be able to understand the basic
concept / usage pattern of the software.

In order to get started, applications may provide some example config file or
testfiles to play around with. C/C++ Libraries and Python modules should
provide small, easy-to-understand example programs / showcases.
'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Looks for example programs to demonstrate basic usage.

            Test passes if there are any Non-SVN files within the
            "examples" subdirectory.
        """
        logging.debug( 'looking for example programs' )
        examplesDir = os.path.join( details.topLevelDir, 'examples' )

        if not os.path.exists( examplesDir ):
            result  = ( FAILED, 0, 1, '"examples" directory not found' )
        else:
            exclude = re.compile( '^.svn' )
            files   = FastScript.getFilesInDir( examplesDir, exclude )
            found   = len(files)

            if found == 0:
                result = ( FAILED, 0, 1,
                           '"examples" subdirectory is empty' )
            elif found == 1:
                result = ( OK, 1, 0,
                           '1 example program found' )
            else:
                result = ( OK, 1, 0,
                           '%d example program(s) found' % len(files) )

        return result


class QualityRule_DOC04( AbstractQualityRule ):

    brief       = '''Original authors and current maintainers should be
documented.'''

    description = '''**Author(s)** are those persons who originally
implemented or later contributed major parts of the code. Authors of a
software should be honored in the documentation. If multiple people modified
the code over time, they should be ranked according to their contribution.

The **maintainer** is the person mainly in charge of the software at the
very moment. He or she may or may not be among the list of authors!
Some maintainer might have taken over responsability without writing a
single line of code.

The filesystem ownership in the SIT is a good indicator who maintains the
package at the moment. However, it is not reliable in case multiple people
installed the package for various reasons (such as holidays) and most likely
will not be preserved when transferring the SIT to other machines or sites.

Therefore, when using BST.py for installing software, the maintainer
information is automatically written into the auto-generated pkgInfo.py
file.
'''

    goodExample = '''
    /*!
     * \mainpage
     *
     * [...]
     *
     * \\author Bill Gates
     * \\author Linus Torvalds (current maintainer)
     * \\author Steve Jobs
     * \\author Lerry Page
     */
'''

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )


class QualityRule_SAFE01( AbstractQualityRule ):

    brief       = '''Only C90 and C99 are allowed.'''

    description = '''MISRA-2012 only talks about C90 and C99, with no
language extensions.'''

    sqLevel     = frozenset( [ 'safety' ] )


class QualityRule_SAFE02( AbstractQualityRule ):

    brief       = '''Functions must check their arguments for validity
(valid pointers, numbers in range, existence of files).'''

    description = '''Problems should be detected as soon as possible, f.i.
invalid sensor data shall be detected instead of computing with wrong data.
Processing invalid data that later lead to some high-level decision might be
very dangerous.

Even in non-critical envrionments, the proper checking for existence of files,
valid pointers, reasonable value ranges etc. catch a lot of typical root
causes for later errors.'''

    goodExample = '''
    #include <Any.h>

    [...]

    ANY_REQUIRE_MSG( condition, message );
'''

    seeAlso     = { 'MISRA-2012 rule 4.11': None }

    sqLevel     = frozenset( [ 'safety' ] )


class QualityRule_SAFE03( AbstractQualityRule ):

    brief       = '''Memory must not be allocated after init phase (startup)
of the application.'''

    description = '''The memory consumption of a program shall be
deterministic, or at least constant at runtime.

It is a common prerequisite for safety-critical applications to allocate
required resources during intialization and do not change this until
termination.'''

    sqLevel     = frozenset( [ 'safety' ] )


class QualityRule_SAFE04( AbstractQualityRule ):

    brief       = '''The `goto`-statement should not be used.'''

    description = '''Unconstrained use of `goto` can lead to programs that
are unstructured and extremely difficult to understand.

Nevertheless, the restricted use of `goto` is allowed if it improves
readability of the code. In such case the `goto` statement shall jump to a
label declared later in the same function.'''

    seeAlso     = { 'MISRA-2012 rule 4.11':
                    None }

    sqLevel     = frozenset( [ 'safety' ] )

    def run( self, details, files ):
        """
            Safety-critical applications shall hardly use 'goto'.
        """
        logging.debug( 'looking for "goto"-statement' )
        found  = 0

        for filePath in files:
            if filePath.endswith( '.c' ) or filePath.endswith( '.cpp' ) or \
               filePath.endswith( '.hpp' ) or filePath.endswith( '.inc' ):

                content = FastScript.getFileContent( filePath )

                if content.find( ' goto ' ) > 0:
                    logging.info( 'SAFE04: goto-statement found: %s', filePath )
                    found += 1

        if found == 0:
            result = ( OK, 1, 0,
                       "'goto' not used" )
        else:
            result = ( FAILED, 0, 1,
                       "found %d 'goto'-statements" % found )

        return result


class QualityRule_SAFE05( AbstractQualityRule ):

    brief       = '''Multi-byte characters (f.i. Unicode) shall not be
used.'''

    description = '''Wide character types (requiring more than 1 Byte per
character, f.i. Unicode) can not be used with traditional string processing
functions and need special treatment when performing pointer arithmetics.

To avoid any risks arising from usage of wide characters multi-byte string
literals their use in safety-critical application is highly discouraged.'''

    seeAlso      = { 'CERT STR38-C':
                     'https://www.securecoding.cert.org/confluence/display/CINT/STR38-C.+Do+not+confuse+narrow+and+wide+character+strings+and+functions' }

    sqLevel      = frozenset( [ 'safety' ] )

    badTypes     = { 'wchar_t', 'wstring' }

    badFunctions = { 'fgetwc', 'fgetws', 'fputwc', 'fputws', 'fwide',
                     'fwprintf', 'fwscanf', 'getwc', 'getwchar', 'putwc',
                     'putwchar', 'swprintf', 'swscanf', 'ungetwc', 'vfwprintf',
                     'vfwscanf', 'vswprintf', 'vswscanf', 'vwprintf', 'vwscanf',
                     'wprintf', 'wscanf', 'wcstod', 'wcstof', 'wcstol',
                     'wcstold', 'wcstoll', 'wcstoul', 'wcstoull', 'btowc',
                     'mbrlen', 'mbrtowc', 'mbsinit', 'mbsrtowcs', 'wcrtomb',
                     'wctob', 'wcsrtombs', 'wcscat', 'wcschr', 'wcscmp',
                     'wcscoll', 'wcscpy', 'wcscspn', 'wcslen', 'wcsncat',
                     'wcsncmp', 'wcsncpy', 'wcspbrk', 'wcsrchr', 'wcsspn',
                     'wcsstr', 'wcstok', 'wcsxfrm', 'wmemchr', 'wmemcmp',
                     'wmemcpy', 'wmemmove', 'wmemset', 'wcsftime' }


    @classmethod
    def check_type( cls, typ ):
        # remove template markers if present and create a set of all types used
        cleanType  = typ.replace( '<', ' ' ).replace( '>', ' ' ).replace( ',', ' ' )
        setOfTypes = set( cleanType.split() )

        # create a set of type params
        # handle both simple cases ('int') and more complex cases like c++
        # template types ('ns1::ns2::int')
        p = set()

        for typeParam in setOfTypes:
            if '::' in typeParam:
                actualType = typeParam.split( '::' )[ -1 ]
            else:
                actualType = typeParam

            p.add( actualType )

        intersection = p & cls.badTypes

        return intersection


    def run( self, details, files ):
        """
            Checks if any of the files provided makes use of multi-byte characters.
        """
        logging.debug( 'looking for multibyte-characters usage' )

        platform  = getHostPlatform()
        passed    = 0
        failed    = 0

        headerAndLanguageMap = CMake.getHeaderAndLanguageMap( platform )
        logging.debug( 'language map: %s', headerAndLanguageMap )

        try:

            for filePath in files:
                _, ext = os.path.splitext( filePath )
                if ext in C_CPP_FILE_EXTENSIONS:

                    parser = createCParser( filePath, details, headerAndLanguageMap )

                    if not parser:
                        continue

                    logging.debug( 'checking %s', filePath )

                    funCalls = parser.getFunctionCalls( filePath )
                    decls    = parser.getVariableDeclarations( filePath )

                    for fun, line in funCalls:
                        if fun in self.badFunctions:
                            logging.info( 'SAFE05: %s:%d - Unsafe function call %s',
                                          filePath, line, fun )

                    for decl, typ, line in decls:
                        if self.check_type( typ ):
                            logging.info( 'SAFE05: %s:%d - Unsafe declaration %s %s',
                                          filePath, line, typ, decl )

                    passedInFile, failedInFile = findNonAsciiCharacters( filePath,
                                                                         'SAFE05')


                    if passedInFile > 0:
                        passed += 1

                    if failedInFile > 0:
                        failed += 1

            if failed == 0:
                result = ( OK, passed, failed,
                           'all files OK' )
            else:
                result = ( FAILED, passed, failed,
                           'files with non ASCII characters or wide string functionality usage found' )

        except EnvironmentError as e:
            logging.error( e )
            result = ( FAILED, passed, failed, e )


        return result


class QualityRule_SAFE06( AbstractQualityRule ):

    brief       = '''Recursion (directly or indirectly) must not be used.'''

    description = '''Recursion carries with it the danger of exceeding
available stack space, which can lead to a serious failure. Unless recursion
is very tightly controlled, it is not possible to determine before execution
what the worst-case stack usage could be.

MISRA-2012 rule 17.2 requires the absence of recursion.'''

    sqLevel     = frozenset( [ 'safety' ] )


class QualityRule_SAFE07( AbstractQualityRule ):

    brief       = '''Use safe string-processing functions only.'''

    description = '''When processing strings the maximum length of the string
must be specified. Traditional functions like `strlen()` which search for the
terminating `\\0` must not be used.'''

    goodExample = '''
    Any_strnlen()
    Any_snprintf()
    Any_strncmp()
    Any_strncat()
    [...]
'''

    badExample = '''
    strlen()
    sprintf()
    strcmp()
    strcat()
    [...]
'''

    seeAlso     = { 'AnyString.h API documentation':
                    'AnyString_About' }

    sqLevel     = frozenset( [ 'safety' ] )


class QualityRule_SAFE08( AbstractQualityRule ):

    brief       = '''Functions should be preferred over function-like
macros.'''

    description = '''In most circumstances, functions should be used instead
of macros. Functions perform argument type-checking and evaluate their
arguments once, thus avoiding problems with potential multiple side effects.

In many debugging systems, it is easier to step through execution of a
function than a macro. Nonetheless, macros may be useful in some
circumstances.'''

    seeAlso     = { 'MISRA-2012 rule 4.9':
                    None,
                    'CERT PRE00-C':
                    'https://www.securecoding.cert.org/confluence/display/c/PRE00-C.+Prefer+inline+or+static+functions+to+function-like+macros' }

    sqLevel     = frozenset( [ 'safety' ] )

    def run( self, details, files ):
        logging.debug( 'checking C/C++ function-like macro presence' )
        passed   = 0
        failed   = 0
        platform = getHostPlatform()

        headerAndLanguageMap = CMake.getHeaderAndLanguageMap( platform )
        logging.debug( 'language map: %s', headerAndLanguageMap )

        try:

            for filePath in files:
                _, ext = os.path.splitext( filePath )
                if ext in C_CPP_FILE_EXTENSIONS:

                    parser = createCParser( filePath, details, headerAndLanguageMap )

                    if not parser:
                        continue

                    for define in parser.localMacros.values():

                        if not define.name.isupper():
                            logging.info( 'SAFE08: %s:%d - define "%s" is not uppercase',
                                            filePath, define.location[ 1 ], define.name )
                            failed += 1

                    for define in parser.localFnMacros.values():

                        logging.info( 'SAFE08: %s:%d - function-like define "%s"',
                                        filePath, define.location[ 1 ], define.name )

                    failed += len( parser.localFnMacros )

            if failed == 0:
                result = ( OK, passed, failed,
                           'No function-like defines found' )
            else:
                result = ( FAILED, passed, failed,
                           'Function-like defines found' )

        except EnvironmentError as e:
            logging.error( e )
            result = ( FAILED, passed, failed, e )


        return result


class QualityRule_SPEC01( AbstractQualityRule ):

    brief       = '''Safety-critical car applications are requested to use
"state-of-the-art" tools (e.g. Klocwork) for checking code quality.'''

    description = '''Safety-critical car applications are requested to use
"state-of-the-art" tools (e.g. Klocwork) for checking code quality.'''

    seeAlso     = { 'MISRA coding standards in Klocwork':
                    'http://www.klocwork.com/products-services/klocwork/detection/misra-coding-standards',

                    'Mapping of MISRA rules to Klocwork checkers':
                    'http://docs.klocwork.com/Insight-10.0/MISRA-C_rules_mapped_to_Klocwork_checkers',

                    'MISRA + Automotive HIS':
                    'ToolBOS_Concept_CodingConventions_MISRA' }

    sqLevel     = frozenset( [ 'safety' ] )


class QualityRule_SPEC02( AbstractQualityRule ):

    brief       = '''MSVC requires variables to be declared at the top of a
function.'''

    description = '''MSVC is not fully C99 compliant, f.i. does not support
C99's way of declaring variables anywhere within a function.

Putting variable declarations at the top of a function is required for
compiling with MSVC, resp. eases a possible future porting to Windows,
without any sideeffects.'''

    goodExample = '''
    int foo( void )
    {
        int result = 0;
        int i      = 0;

        for( i = 0; i <= 42; i++ )
        {
            result += bar( i );
        }

        return result;
    }
'''

    badExample  = '''
    int foo( void )
    {
        int result = 0;

        for( int i = 0; i <= 42; i++ )
        {
            result += bar( i );
        }

        return result;
    }
'''

    sqLevel     = frozenset()


class QualityRule_SPEC03( AbstractQualityRule ):

    brief       = '''Portable POSIX-like functions should be used, rather
than platform-specific functions.'''

    description = '''Using **POSIX**-compliant functions for memory
allocation, string processing, multithreading and the like simplifies writing
multi-platform applications that need to run on both Unix-like and Windows
systems.

At least it pro-actively eases a possible future porting to either of such
platforms, without any sideeffects.

The ToolBOSCore library defines `Any_strcmp()`, `Any_memset()` and friends for
such purpose. They map to the underlying O.S.-specific functions with no cost
(resolved at compile-time).'''

    seeAlso     = { 'AnyString.h API documentation':
                    'AnyString_About' }

    sqLevel     = frozenset()


class QualityRule_SPEC04( AbstractQualityRule ):

    brief       = '''It is typically not foreseeable if code in the future
might be re-used in a multi-threaded environment. Therefore all code should be
explicitly crafted not to exhibit related synchronization issues (e.g. race
conditions, deadlocks,...).'''

    description = '''Special care should be taken to make classes and
functions thread-safe. That means the code should be invariant against the
number of threads at runtime.

Appropriate means are f.i. **mutexes**, **locks**, **conditional variables**,
**barriers**, and **atomic operations**.

**Important:** An _atomic operation_ is an explicit concept of the used
programming language (usually naming the keyword atomic).
This guarantees that the operation is atomic under all circumstances.
On the other hand, an operation can be atomic just as a side effect of a
certain combination of interpreter/compiler implementation and target
platform, f.i. there is documentation that some Python operations are atomic
under the current CPython implementation. However this might not be true in
future or for other Python implementations like PyPy, Jython or IronPython.
In this case you have to use other means to ensure thread-safety instead.
Do not rely on such implementation-specific side effects!'''

    seeAlso     = { 'Thread handling and synchronization primitives in Python 2.7':
                    'https://docs.python.org/2/library/threading.html',

                    'Wikipedia: Thread safety':
                    'https://en.wikipedia.org/wiki/Thread_safety' }

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )


class QualityRule_SPEC05( AbstractQualityRule ):

    brief       = '''Functions should be re-entrant.'''

    description = '''**Re-entrancy** means writing code in such a way that it
can be partially executed by a thread, reexecuted by the same thread or
simultaneously executed by another thread and still correctly complete the
original execution.

This requires the saving of state information in variables local to each
execution, usually on a stack, instead of in static or global variables or
other non-local state. All non-local state must be accessed through
atomic operations and the data-structures must also be reentrant.

Note: The ToolBOSCore library offers all means to create thread-safe, portable
applications.'''

    seeAlso     = { 'Thread handling and synchronization primitives':
                    'MThreads_About',

                    'Wikipedia: Thread safety':
                    'https://en.wikipedia.org/wiki/Thread_safety' }

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )


def findNonAsciiCharacters( filePath, rule ):
    content = FastScript.getFileContent( filePath, splitLines=True )
    passed  = 0
    failed  = 0

    for i, line in enumerate( content ):

        if six.PY2:

            try:
                line.decode( 'ascii' )
                passed += 1
            except UnicodeDecodeError as e:
                # PyCharm linter fails to recognize the start property
                # so we silence the warning.
                # noinspection PyUnresolvedReferences
                logging.info( '%s: %s:%d - Non-ASCII character found at position %d',
                              rule, filePath, i, e.start )
                failed += 1

        else:

            try:
                line.encode( 'ascii' )
                passed += 1
            except UnicodeEncodeError as e:
                # PyCharm linter fails to recognize the start property
                # so we silence the warning.
                # noinspection PyUnresolvedReferences
                logging.info( '%s: %s:%d - Non-ASCII character found at position %d',
                              rule, filePath, i, e.start )
                failed += 1


    return passed, failed


def createCParser( filePath, details, headerAndLanguageMap ):

    # this check can be removed in future when only bionic64 or its successor
    # are in use

    hostPlatform = getHostPlatform()
    msg          = 'check function not supported on platform=%s (only on bionic64)' % hostPlatform

    if hostPlatform != 'bionic64':
        raise EnvironmentError( msg )


    if six.PY2:

        try:
            from ToolBOSCore.Util.CAnalyzer import CParser
        except ImportError as e:
            raise EnvironmentError( e )

    else:

        try:
            from ToolBOSCore.Util.CAnalyzer import CParser
        except ModuleNotFoundError as e:
            raise EnvironmentError( e )


    _, ext       = os.path.splitext( filePath )
    platform     = getHostPlatform()
    targetName   = details.packageName + '-global'

    try:
        includePaths = CMake.getIncludePathsAsList( platform, targetName )
        includes     = [ '-I' + includeDir for includeDir in includePaths ]
        cflagsList   = CMake.getCDefinesAsList( platform, targetName )
        cflags       = [ '-D' + cflag for cflag in cflagsList ]
        args         = includes + cflags
    except ( AssertionError, IOError ):
        # most likely the depend.make does not exist for this target,
        # this might happen if there are no dependencies by the target
        # or if this is a pseudo-target such as "doc" coming from
        # FindDoxygen.cmake
        logging.debug( 'ignoring target: %s', targetName )
        return None

    # checking if the header file has been included in C files, C++ files or both
    if ext.lower() == '.h':
        # we default to C++ as the c++ compiler should correctly parse C headers,
        # and there is also a common use case for seemingly unused header files in
        # C++, namely templates.
        langs          = headerAndLanguageMap.get( filePath, ['c++'] )
        usedInCFiles   = 'c' in langs
        usedInCXXFiles = 'c++' in langs

        if usedInCFiles and (not usedInCXXFiles):
            # header only included in C files
            isCPlusPlus = False
        elif usedInCXXFiles and (not usedInCFiles):
            # header only included in C++ files
            isCPlusPlus = True
        elif usedInCXXFiles and usedInCFiles:
            # header included in both C and C++ files
            logging.warning( '%s included in both C and CPP files, parsing it as C++', filePath )
            isCPlusPlus = True
        else:
            # should never enter here
            logging.error(
                '%s does not appear to be included in any project C or C++ files, parsing it as C++',
                filePath )
            isCPlusPlus = True
    else:
        # hpp files, treating as c++
        isCPlusPlus = True

    # set default switches, this is needed at least for c++ (for macro analysis)
    switches = CMake.getStdSwitches( platform, targetName )

    if isCPlusPlus:
        stdSwitch = switches.cpp
    else:
        stdSwitch = switches.c

    # parse the file
    logging.debug( '%s: isCPlusPlus = %s', filePath, isCPlusPlus )
    langStd = stdSwitch[5:]

    return CParser( filePath,
                    isCPlusPlus,
                    langStd,
                    args=args + [ stdSwitch ],
                    includepaths=includePaths,
                    defines=cflagsList )


def getRules():
    """
        Returns a list of available rules/checkers. Each item in the list
        is a tuple of (ruleID,instance). The ruleID is a string, and the
        instance is a ready-to-use QualityRule representing one particular
        SW Quality Guideline rule.
    """
    # retrieve all classes defined within this Python module,
    # and create instances

    result = []
    ctors  = {}
    tmp    = inspect.getmembers( sys.modules[__name__], inspect.isclass )

    for className, constructor in tmp:
        if className.startswith( 'QualityRule_' ):
            ctors[ className ] = constructor


    # keep sorting as appears in SQ Guideline

    for category in ( 'GEN', 'C', 'PY', 'MAT', 'JAVA', 'DOC', 'SAFE',
                      'MT', 'SPEC' ):
        for i in range(50):

            ruleID = '%s%02d' % ( category, i )

            try:
                func = ctors[ 'QualityRule_%s' % ruleID ]
                Any.requireIsCallable( func )
                instance = func()
                result.append( ( ruleID, instance ) )
            except KeyError:
                pass               # no such rule, or rule not implemented

    return result


def getRuleIDs():
    """
        Returns a list of all SQ rule IDs in the order of appearance in the
        Software Quality Guideline.
    """
    ruleTuples = getRules()
    Any.requireIsListNonEmpty( ruleTuples )

    result = [ rule[0] for rule in ruleTuples ]
    Any.requireIsListNonEmpty( result )

    return result


# EOF
