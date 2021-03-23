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
import io
import logging
import os
import re
import shlex
import subprocess
import sys
import tempfile

from ToolBOSCore.BuildSystem                      import BuildSystemTools
from ToolBOSCore.BuildSystem.DocumentationCreator import DocumentationCreator
from ToolBOSCore.Packages.BSTPackage              import BSTProxyInstalledPackage
from ToolBOSCore.Packages.PackageDetector         import PackageDetector
from ToolBOSCore.Platforms.Platforms              import getHostPlatform
from ToolBOSCore.Settings.ProcessEnv              import source
from ToolBOSCore.Settings.ToolBOSConf             import getConfigOption
from ToolBOSCore.SoftwareQuality.Common           import *
from ToolBOSCore.Tools                            import CMake, Klocwork,\
                                                         Matlab, PyCharm,\
                                                         Valgrind
from ToolBOSCore.Util                             import Any, FastScript


ALL_FILE_EXTENSIONS     = ( '.bat', '.c', '.cpp', '.h', '.hpp', '.inc',
                            '.java', '.m', '.py' )

C_FILE_EXTENSIONS       = ( '.c', '.h', '.inc' )

C_CPP_FILE_EXTENSIONS   = ( '.c', '.cpp', '.h', '.hpp', '.inc' )

C_HEADER_EXTENSIONS     = ( '.h', )

C_CPP_HEADER_EXTENSIONS = ('.h', '.hpp', 'hh', 'hxx')


class AbstractRule( object ):

    ruleID      = None
    brief       = None
    description = None
    goodExample = None
    badExample  = None
    seeAlso     = {}
    sqLevel     = None
    removed     = False


    def __init__( self ):
        self.details    = None
        self.files      = None
        self.passed     = 0
        self.failed     = 0


    def getRuleID( self ):

        className = type(self).__name__
        ruleID    = className.split('_')[-1]

        return ruleID


class RemovedRule( AbstractRule ):

    brief   = '*removed*'
    removed = True


class Rule_GEN01( AbstractRule ):

    brief       = '''All comments, documentation, identifier names (types,
variables, functions, classes) and filenames must be English.'''
    description = '''Even if intended for personal use only, you never know
who might be using your source code in the future.

English as corporate language should be reflected in the source code as well.
Other languages such as German or Japanese should be avoided.

Note that your application may well support various languages, e.g. print
Japanese output on screen.'''

    goodExample = '''\tint result = 123;'''

    badExample  = '''\tint ergebnis = 123;'''

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Look for specific characters such as German Umlauts, French
            accents, or Japanese characters.
        """
        logging.debug( 'checking filenames for Non-English characters...' )
        passed = 0
        failed = 0

        whitelist = ALL_FILE_EXTENSIONS

        for filePath in files:
            if os.path.splitext( filePath )[-1] in whitelist:

                logging.debug( 'checking %s', filePath )

                try:
                    filePath.encode( 'ascii' )
                    passed += 1
                except UnicodeEncodeError as e:
                    # PyCharm linter fails to recognize the start property
                    # so we silence the warning.
                    # noinspection PyUnresolvedReferences
                    logging.info( 'GEN01: %s - Non-ASCII character in filename',
                                  filePath )
                    failed += 1


        if failed == 0:
            result = ( OK, passed, failed,
                       'all filenames in ASCII characters' )
        else:
            result = ( FAILED, passed, failed,
                       'filenames with Non-ASCII characters found' )

        return result


class Rule_GEN02( AbstractRule ):

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
            try:
                content = FastScript.getFileContent( filePath, asBinary=True )
            except ( IOError, OSError ) as e:
                logging.error( e )
                failed += 1
                continue

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


class Rule_GEN03( AbstractRule ):

    brief       = '''Stick to 80 characters per line. Exceptions are fine
when increasing readability.'''

    description = '''Yes, monitors noawadays are huge and can display more
characters per line. Instead the reason of limiting to 80 characters are:

  * diff-ing two or three files next to each other, f.i. code comparison
  * IDEs + debuggers + source code analyzers show many widgets around the code
  * simpler editing / viewing
  * terminals default to 80x25, widely used for "less" / "git show" / ...
  * merging sources (side-by-side view)

Where readability would be increased, we allow a few exceptions up to 120
characters per line.'''

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

        for filePath in sorted( files ):
            longLines = 0
            maxLen    = 0
            try:
                lines = FastScript.getFileContent( filePath, splitLines=True )
            except ( IOError, OSError, UnicodeDecodeError ) as e:
                logging.error( 'unable to open file: %s: %s', filePath, type( e ) )
                failed += 1
                continue

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


class Rule_GEN04( AbstractRule ):

    brief       = '''All source code files and related artefacts, such as
configfiles or documentation, must start with a copyright header.'''

    description = '''The standardized HRI-EU copyright header contains both
copyright claim and address of the company.

Please add it to all source code files and related artefacts resulting from
work for HRI-EU.

This copyright header must also be applied by contractors and students working
for HRI-EU.

This rule does not need to be applied to auto-generated files (such as doxygen
HTML documentation or generated SWIG code).

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

This rule shall not be applied to open-source code released under a particular
license that most often requires a specific header. In such case please place
the copyright information into the pkgInfo.py, e.g.:

copyright       =
'''

    seeAlso     = { 'rule DOC-04': None }

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )


    def __init__( self ):
        super( Rule_GEN04 ).__init__()

        from ToolBOSCore.Packages.CopyrightHeader import getCopyright

        self._defaultCopyrightHeader = getCopyright()


    def run( self, details, files ):
        """
            Checks if the HRI-EU copyright header is present.
        """
        logging.debug( 'checking files for copyright header' )

        failed    = 0
        whitelist = ALL_FILE_EXTENSIONS


        if details.copyright:
            logging.info( 'found specific copyright information in pkgInfo.py' )
        else:
            logging.debug( 'searching for default copyright header' )


        for filePath in sorted( files ):
            fileExt = os.path.splitext( filePath )[-1]

            if fileExt in whitelist:
                content        = FastScript.getFileContent( filePath )
                copyrightLines = self._getCopyrightLines( filePath, details.copyright )


                for line in copyrightLines:
                    if content.find( line ) == -1:
                        logging.debug( "%s: '%s' not found", filePath, line )
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


    def _getCopyrightLines( self, filePath, copyrightData ):
        """
            Returns a list of strings (copyright header lines) that shall
            be present in 'filePath'.

            The info are taken from the pkgInfo.py file. The author may
            specify the appropriate copyright headers there.
            If no information have been provided we assume the common
            copyright header as returned from Packages.getCopyrightHeader().
        """
        Any.requireIsTextNonEmpty( filePath )

        if copyrightData is None:
            # logging.debug( 'no copyright info by author, assuming defaults' )

            lines = self._defaultCopyrightHeader

        elif Any.isText( copyrightData ):
            # logging.info( 'single copyright line by author, use this for all project files' )
            # logging.info( 'copyright info: %s', copyrightData )

            msg = 'copyright data in pkgInfo.py too short (min. 10 chars required)'
            Any.requireIsTextNonEmpty( copyrightData )
            Any.requireMsg( len(copyrightData) > 10, msg )
            lines = [ copyrightData ]

        elif Any.isList( copyrightData ):
            #logging.debug( 'multiple copyright lines by author, using them for all project files' )
            #logging.debug( '<copyrightInfo>' )
            #logging.debug( copyrightData )
            #logging.debug( '</copyrightInfo>' )

            Any.requireIsListNonEmpty( copyrightData )
            lines = copyrightData

        elif Any.isDict( copyrightData ):
            #logging.debug( 'dict with copyright info provided by author' )

            Any.requireIsDictNonEmpty( copyrightData )
            lines = self._getCopyrightFromDict( filePath, copyrightData )

        else:
            msg = 'pkgInfo.py: invalid type "%s" for value of "copyright"' % type(copyrightData)
            raise AssertionError( msg )

        return lines


    def _getCopyrightFromDict( self, filePath, copyrightData ):
        """
            Given a dict 'copyrightData' mapping 'path' --> 'copyright'

            We assume that 'path' is any part of a relative path to a file
            e.g.:
                 * "external"
                 * "external/foo.org"
                 * "external/foo.org/foo.c"

            and 'copyright' is any of:
                 * single string
                 * multiple strings (array)

            This function attempts to find the longest matching key in
            the dict matching 'filePath', and returns the associated value.
        """
        Any.requireIsTextNonEmpty( filePath )
        Any.requireIsDictNonEmpty( copyrightData )

        bestLen     = 0
        bestPattern = None
        bestLines   = self._defaultCopyrightHeader  # attempt to overwrite in for-loop

        for pattern, lines in copyrightData.items():

            if filePath.startswith( pattern ):
                patternLen = len(pattern)

                if patternLen > bestLen:
                    bestLen     = patternLen
                    bestPattern = pattern

                    if Any.isText( lines ):
                        msg = 'copyright data in pkgInfo.py too short (min. 10 chars required)'
                        Any.requireIsTextNonEmpty( lines )
                        Any.requireMsg( len(lines) > 10, msg )
                        bestLines = [ lines ]

                    elif Any.isList( lines ):
                        Any.requireIsListNonEmpty( lines )
                        bestLines = lines

                    else:
                        msg = 'Invalid type "%s" for copyright in path "%s"' % ( type(lines), pattern )
                        raise AssertionError( msg )

        logging.debug( 'best pattern for %s: %s', filePath, bestPattern )

        return bestLines


class Rule_GEN05( AbstractRule ):

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


class Rule_GEN06( AbstractRule ):

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
            try:
                content = FastScript.getFileContent( fileName )
            except ( IOError, OSError, UnicodeDecodeError ) as e:
                logging.error( 'unable to open file: %s: %s', fileName, type( e ) )
                failed += 1
                continue

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
                       'no tabs found' )
        else:
            result = ( FAILED, passed, failed,
                       'tabs found' )

        return result


class Rule_GEN07( AbstractRule ):

    brief       = 'Libraries and applications should contain a unittest.'

    description = '''Even if covering just a small part, some unittests make
you sleep better: When executed automatically (during nightly builds) they
show:

  * the code is compilable (f.i. on multiple platforms)
  * no broken dependencies, such as API changes
  * executables are runnable (no undefined symbols, missing files,...)
  * tested code somehow behaves as expected

Please provide a generic `unittest.sh` (Linux) and/or `unittest.bat`
(Windows) in the top-level directory of the package. This shall invoke any
package-specific testsuite.'''

    seeAlso     = { 'Unittest HowTo': 'ToolBOS_Util_BuildSystemTools_Unittesting' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks if the package provides a unittest.
        """
        Any.requireIsNotNone( details.packageCategory, 'Package category not specified. '
                                                       'Please check pkginfo.py '
                                                       'or CMakeLists.txt for category information.' )

        if details.isComponent():
            return NOT_APPLICABLE, 0, 0, 'unittests not required for components'

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


class Rule_GEN08( AbstractRule ):

    brief       = '''Any 3rd-party-code must be clearly separated to avoid
any intellectual property conflicts. Mind to put relevant license information
if needed.'''

    description = '''Closely integrating 3rd-party-software such as compiling
foreign source code into the own application very likely will violate the
license of the 3rd-party-software. This can result in severe legal problems.
(There are some licenses which permit such usage, f.i. BSD License).

Even putting 3rd-party-libraries into the own source code repository is within
a questionable grey zone. At least create a sub-directory named
*external* or *3rdParty* and put all 3rd-party-modules inside.
This makes it obvious that you do not claim ownership on this material.

Best approach is to install 3rd-party-software independently into SIT, and
interface with it.'''

    goodExample = '''\tMyPackage
\t\t1.0 (version directory is optional)
\t\t\texternal (or "3rdParty")
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


class Rule_GEN09( AbstractRule ):

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


class Rule_GEN10( AbstractRule ):

    brief       = '''Put package under version control system (Git/SVN).'''

    description = '''A version control system serves several purposes:

  * preserve individual source code states over time
  * track or rollback modifications
  * agreed "master" location
  * avoids chaos of various copies + patchfiles
  * central backup

Note: HRI-EU recommends to use Git.'''

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


class Rule_GEN11( AbstractRule ):

    brief       = '''Consider managing bugs and feature requests via JIRA
issue tracker.'''

    sqLevel     = frozenset()

    def __init__( self ):
        super( AbstractRule, self ).__init__()

        url = getConfigOption( 'bugtrackURL' )

        self.description = '''Instead of sending bug reports and feature requests via
e-mails please consider using JIRA.

It helps tracking issues, allows leaving comments and posting files, so that
all involved people have the same knowledge about the issue.

Within HRI-EU JIRA is reachable at:
[%(url)s](%(url)s)

Remote access is also possible upon request, please contact system
administration in this case.''' % { 'url': url }


class Rule_GEN12( AbstractRule ):

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


class Rule_GEN13( AbstractRule ):

    brief       = '''Always check return-values of function'''

    description = '''Return values, especially those indicating errors,
should not be silently ignored. If some return value is not very useful
(as could be those of `printf()` or `close()`), you should provide a cast
and/or comment that it has been ignored on purpose.'''

    sqLevel     = frozenset()


class Rule_GEN14( AbstractRule ):

    brief       = '''Strive for simple control-flows and keep functions
short'''

    description = '''Complex control-flows and long functions make reasoning
about and code-checking difficult, f.i. the cyclomatic complexity should be
sufficiently low.

Overly long functions are difficult to understand (especially if you have to
scroll).

Attempt to break-down functions longer than approximately 60 lines of code
into smaller chunks, and review their responsabilities. A function shall
perform one job only.'''


class Rule_C01( AbstractRule ):

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
        if not details.isCPackage() and not details.isCppPackage():
            return NOT_APPLICABLE, 0, 0, 'no C/C++ code found in src/'

        logging.debug( 'looking for direct exit() in code' )
        failed = 0
        passed = 0

        regexpExit1 = re.compile( r'\sexit\s*\(' )
        regexpExit2 = re.compile( r'\s_exit\s*\(' )
        regexpAbort = re.compile( r'\sabort\s*\(' )

        for filePath in files:
            if filePath.find( '/bin/' ) != -1 or \
               filePath.find( '/examples/' ) != -1 or \
                filePath.find( '/test/' ) != -1:

                logging.debug( '%s: found exit() within main program: OK', filePath  )
                continue

            _, ext = os.path.splitext( filePath )
            if ext in C_CPP_FILE_EXTENSIONS:

                try:
                    content = FastScript.getFileContent( filePath )
                except ( IOError, OSError, UnicodeDecodeError ) as e:
                    logging.error( 'unable to open file: %s: %s', filePath, type( e ) )
                    failed += 1
                    continue

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
                       'no invalid use of exit() or abort() found' )
        else:
            result = ( FAILED, passed, failed,
                       'exit() and/or abort() found' )

        return result


class Rule_C02( AbstractRule ):

    brief       = 'C header files should ensure C++ linkage compatibility.'

    description = '''For compatibility with C++, all function prototypes in C
header files should be surrounded by macros to ensure C linkage in case of C++.

This pro-actively enables using this header file in a possible future C++
context, without any sideeffects.

Without these macros the code will not link in C++ context.'''

    goodExample = '''
    #ifdef __cplusplus
    extern "C" {
    #endif
    ...
    #ifdef __cplusplus
    }
    #endif
'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    # TBCORE-2067  It turned out that the current implementation is not
    #              satisfactory as we have no easy way to determine if a
    #              header file (*.h) contains C or C++ code, despite
    #              attempting to interpret it. Given that the rule is
    #              anyway of limited use, we disabled this code.
    #
    # def run( self, details, files ):
    #     if not details.isCPackage():
    #         return NOT_APPLICABLE, 0, 0, 'no C code found in src/'
    #
    #     logging.debug( 'checking C header files for linkage guards' )
    #
    #     binDir            = os.path.join( details.topLevelDir, 'bin' )
    #     ifdefExpr         = r'#\s*if\s+defined\(\s*__cplusplus\s*\)\s+extern\s+"C"\s+\{\s+#\s*endif'
    #     ifdefinedExpr     = r'#\s*ifdef\s+__cplusplus\s+extern\s+"C"\s+\{\s+#\s*endif'
    #     toolbosMacroExpr  = r'ANY_BEGIN_C_DECLS.*ANY_END_C_DECLS'
    #     ifdefRegex        = re.compile( ifdefExpr )
    #     ifDefinedRegex    = re.compile( ifdefinedExpr )
    #     toolbosMacroRegex = re.compile( toolbosMacroExpr )
    #     passed            = 0
    #     failed            = 0
    #
    #     patterns          = { ifdefExpr       : ifdefRegex,
    #                           ifdefinedExpr   : ifDefinedRegex,
    #                           toolbosMacroExpr: toolbosMacroRegex }
    #
    #     try:
    #
    #         for filePath in files:
    #             fname, ext = os.path.splitext( filePath )
    #
    #             if ext in C_HEADER_EXTENSIONS and not filePath.startswith( binDir ):
    #
    #                 contents = FastScript.getFileContent( filePath )
    #                 found    = False
    #
    #                 logging.debug( 'checking: %s', filePath )
    #
    #                 for expr, regex in patterns.items():
    #                     if regex.search( contents ):
    #                         logging.debug( 'pattern found: %s', expr )
    #                         found = True
    #                     else:
    #                         logging.debug( 'pattern not found: %s', expr )
    #
    #
    #                 if found:
    #                     logging.debug( 'passed: %s', filePath )
    #                     passed += 1
    #                 else:
    #                     logging.info( 'C02: linkage guard missing: %s', filePath )
    #                     failed += 1
    #
    #     except EnvironmentError as e:
    #         logging.error( e )
    #         return FAILED, passed, failed, e
    #
    #
    #     if failed == 0:
    #         result = ( OK, passed, failed,
    #                    'all headers contain proper linkage guards' )
    #     else:
    #         result = ( FAILED, passed, failed,
    #                    'invalid C header files found' )
    #
    #     return result


class Rule_C03( AbstractRule ):

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
        if not details.isCPackage() and not details.isCppPackage():
            return NOT_APPLICABLE, 0, 0, 'no C/C++ code found in src/'

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
                if ext in C_CPP_HEADER_EXTENSIONS:
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


class Rule_C04( AbstractRule ):

    brief       = '''A function without parameters must be declared with a
`void` argument list.'''

    description = '''This rule only applies to C code.

A `void` argument list indicates that the function does
not take arguments. Hence the compiler can check for invalid calls where
unexpected parameters are supplied.

If `void` isn't specified, the compiler does not make any assumptions.
Hence the function could accidently be called with arguments.

This might lead to an error if a function that originally had taken parameters
has been changed (to not take parameters anymore) and the caller was not
updated and still passes parameters.'''

    goodExample = '''   int Foo_run( void );'''

    badExample  = '''   int Foo_run();'''

    seeAlso     = { 'CERT DCL20-C':
                    'https://wiki.sei.cmu.edu/confluence/display/c/DCL20-C.+Explicitly+specify+void+when+a+function+accepts+no+arguments' }

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        if not details.isCPackage():
            return NOT_APPLICABLE, 0, 0, 'no C code found in src/'

        logging.debug( 'looking for function prototypes with no information about the arguments' )
        platform             = getHostPlatform( )
        headerAndLanguageMap = CMake.getHeaderAndLanguageMap( platform )
        failed               = 0
        passed               = 0

        try:

            for filePath in files:
                _, ext = os.path.splitext( filePath )

                if ext in C_FILE_EXTENSIONS:
                    parser = createCParser( filePath, details, headerAndLanguageMap )

                    if not parser:
                        continue

                    protos = parser.getFunctionPrototypesWithoutParameters( filePath )

                    if protos:
                        failed += 1

                        for proto, line in protos:
                            msg = 'C04: %s:%d - void-function with ambiguous argument list'
                            logging.info( msg, filePath, line, proto )
                    else:
                        passed += 1

            if failed == 0:
                result = ( OK, passed, failed,
                           'no void-functions with ambiguous arguments found' )
            else:
                result = ( FAILED, passed, failed,
                           'void-functions with ambiguous arguments found' )

        except EnvironmentError as e:
            logging.error( e )
            result = ( FAILED, passed, failed, e )


        return result


class Rule_C05( AbstractRule ):

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
                    'https://wiki.sei.cmu.edu/confluence/display/c/PRE06-C.+Enclose+header+files+in+an+include+guard' }

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks that C/C++ header files contain inclusion guards, f.i.

                #ifndef BERKELEYSOCKET_H
                #define BERKELEYSOCKET_H
                ...
                #endif
        """
        if not details.isCPackage() and not details.isCppPackage():
            return NOT_APPLICABLE, 0, 0, 'no C/C++ code found in src/'

        logging.debug( 'checking header file inclusion guards' )

        blacklist = frozenset( [ 'documentation.h' ] )

        for filePath in files:
            _, ext = os.path.splitext( filePath )

            if ext in C_CPP_HEADER_EXTENSIONS:
                fileName    = os.path.basename( filePath )
                module      = os.path.splitext( fileName )[0]
                moduleUpper = module.upper()
                content     = FastScript.getFileContent( filePath )

                if fileName in blacklist:
                    # ignore / do not check whitelisted files
                    continue

                # Note that we are searching with regexp for a more relaxed
                # string with possible pre-/postfix namespace name, but we
                # print a stricter safeguard name in case it was not found,
                # see JIRA tickets TBCORE-918 and TBCORE-2060
                #
                # allowed:      PACKAGENAME_H
                #           FOO_PACKAGENAME_H
                #           FOO_PACKAGENAME_H_BAR
                #               PACKAGENAME_H_BAR
                #           FOO_PACKAGENAME_BAZ_H_BAR
                #               PACKAGENAME_BAZ_H

                safeguard   = '#ifndef %s_H' % moduleUpper
                regexp      = re.compile( r'#ifndef\s(\S*?%s\S*_H\S*)' % moduleUpper )

                tmp = regexp.search( content )

                if tmp:
                    logging.debug( "C05: %s: safeguard %s found",
                                   filePath, tmp.group(1) )
                    self.passed += 1
                else:
                    logging.info( "C05: %s: safeguard %s not found",
                                  filePath, safeguard )
                    self.failed += 1


        if self.failed == 0:
            result = ( OK, self.passed, self.failed,
                       'multi-inclusion safeguards present' )
        else:
            result = ( FAILED, self.passed, self.failed,
                       'multi-inclusion safeguards missing' )

        return result


class Rule_C06( RemovedRule ):
    pass


class Rule_C07( AbstractRule ):

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
                    'https://wiki.sei.cmu.edu/confluence/display/c/ERR00-C.+Adopt+and+implement+a+consistent+and+comprehensive+error-handling+policy' }

    sqLevel     = frozenset()


class Rule_C08( AbstractRule ):

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
                    'https://wiki.sei.cmu.edu/confluence/display/java/NUM03-J.+Use+integer+types+that+can+fully+represent+the+possible+range+of++unsigned+data',

                    'CERT INT31-C':
                    'https://wiki.sei.cmu.edu/confluence/display/c/INT31-C.+Ensure+that+integer+conversions+do+not+result+in+lost+or+misinterpreted+data',

                    'CERT INT08-C':
                    'https://wiki.sei.cmu.edu/confluence/display/c/INT08-C.+Verify+that+all+integer+values+are+in+range' }

    sqLevel     = frozenset()


class Rule_C09( AbstractRule ):

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
        output = io.StringIO() if Any.getDebugLevel() <= 3 else None

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


class Rule_C10( AbstractRule ):

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
        if not details.isCPackage() and not details.isCppPackage():
            return NOT_APPLICABLE, 0, 0, 'no C/C++ code found in src/'

        logging.debug( 'performing source code analysis using Klocwork' )
        passed = 0
        failed = 0
        output = io.StringIO()
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

        except ( AssertionError, subprocess.CalledProcessError,
                 EnvironmentError, RuntimeError ) as details:
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


class Rule_C11( AbstractRule ):
    brief       = '''`setjmp()` and `longjmp()` are forbidden'''

    description = '''The two functions `setjmp()` and `longjmp()` make the
execution paths through the code overly complicated. Do not use them.'''

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )


class Rule_C12( AbstractRule ):

    brief       = '''Heap-memory explicitly allocated with `malloc()` or
`new` (or wrappers thereof), must be explicitly released using `free()` or
`delete` (or corresponding wrappers).
'''

    description = '''If resources are not explicitly released then it is
possible for a failure to occur due to exhaustion of those resources.
Releasing resources as soon as possible reduces the possibility that
exhaustion will occur.

The check function for this rule invokes Valgrind on all executables listed
in the sqCheckExe variable in pkgInfo.py, e.g.:

    sqCheckExe = [ 'bin/${MAKEFILE_PLATFORM}/main',
                   'bin/${MAKEFILE_PLATFORM}/main foo --bar',
                   'test/${MAKEFILE_PLATFORM}/main foo --bar']

Please specify a list of commands, including arguments (if any), that
shall be analyzed by the check routine. 
No issues shall be found during execution of unittests also.

The paths to the executables are interpreted as relative to the package root.
Only specify the executbale that needs no user interaction.

Specify an empty list if really nothing has to be executed.'''

    seeAlso     = { 'MISRA-2012 rule 22.1': None }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Check for memory leaks.
        """
        ruleId = self.getRuleID()

        if not details.hasMainProgram( files ):
            return NOT_APPLICABLE, 0, 0, 'no C/C++ main programs found'

        # get SQ-settings from pkgInfo.py
        sqSettings = self._getSQSettings( details )
        logging.debug( "'sqCheckExe' settings from pkgInfo.py: %s", sqSettings )
        Any.requireIsIterable( sqSettings )

        if not sqSettings:
            logging.warning( "C/C++ source code found, but no executables listed in pkgInfo.py" )
            logging.warning( "please see documentation of %s (field 'sqCheckExe')", ruleId )
            msg    = "no executables to run under Valgrind"
            result = ( NOT_APPLICABLE, 0, 1, msg )

            return result

        # verify that the executables specified by user in pkgInfo.py exists

        validityCheck = self._validityCheck( sqSettings )

        if validityCheck[0] == FAILED:
            shortText = validityCheck[3]
            logging.debug( shortText )

            return validityCheck

        # source the package before running Valgrind, package should be installed in proxy or global SIT
        try:
            source( details.canonicalPath )
            logging.debug( "sourcing %s", details.canonicalPath )
        except AssertionError as e:
            logging.error( e )

            return FAILED, 0, 0, 'unable to run valgrind'

        bstProxyPackage = BSTProxyInstalledPackage()

        bstProxyPackage.open( details.canonicalPath )
        bstProxyPackage.retrieveDependencies( True )

        deps = bstProxyPackage.depSet
        logging.debug( "Package dependencies: %s", deps )

        if deps:
            logging.info( "sourcing dependencies of %s", details.canonicalPath )
            for dep in deps:
                source( dep )
                logging.info( "sourcing %s", dep )

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
            ruleId = self.getRuleID()
            Any.requireIsTextNonEmpty( ruleId )

            return None


    def _validityCheck( self, commandLines ):
        Any.requireIsList( commandLines )

        commands = []

        for cmdLine in commandLines:

            tmp = shlex.split( cmdLine )
            command = tmp[0]
            commands.append( command )

        for command in commands:
            if not os.path.exists( command ):
                logging.error( "The path specified in pkgInfo.py 'sqCheckExe' key does not exist: %s'. "
                               "Is the package compiled?", command )

                result = ( FAILED, 0, 1,
                           'no executables found to run under Valgrind' )

                return result

        return OK, 0, 0, 'validity check paas'


    def _runValgrind( self, commandLines, details ):
        passedExecutables = 0
        failedExecutables = 0
        errorMessages     = []

        ruleID            = self.getRuleID()

        for command in commandLines:

            logging.info( "%s: checking '%s'", ruleID,command )

            if Any.getDebugLevel() <= 3:
                stdout = io.StringIO()
                stderr = io.StringIO()
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
                    errorMessages.append( '%s: %s:%s - %s'
                                          % ( ruleID, error.fname, error.lineno, error.description ) )

                logging.info( "%s: '%s' failed (see verbose-mode for details: BST.py -q C12 -v)", ruleID, command )

            else:
                passedExecutables += 1
                logging.info( "%s: '%s successfully finished", ruleID, command )

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



class Rule_C13( AbstractRule ):

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


class Rule_C14( AbstractRule ):

    brief       = '''Minimize the use of global variables.'''

    description = '''Variables and functions should be declared in the
minimum scope from which all references to the identifier are still possible.

When a larger scope than necessary is used, code becomes less readable,
harder to maintain, and more likely to reference unintended variables.

Avoiding cluttering the global name space prevents the variable from being
accidentally (or intentionally) invoked from another compilation unit.'''

    seeAlso     = { 'CERT DCL19-C':
                    'https://wiki.sei.cmu.edu/confluence/display/c/DCL19-C.+Minimize+the+scope+of+variables+and+functions' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class Rule_C15( RemovedRule ):
    pass


class Rule_C16( AbstractRule ):

    brief       = '''Use the preprocessor only for inclusion of header-files
and simple macros.'''

    description = '''Complex and multiple levels of macros obfuscate the
code and make reasoning about it or debugging difficult.

In most circumstances, functions should be used instead of macros.
Functions perform argument type-checking and evaluate their arguments once,
thus avoiding problems with potential multiple side effects.

In many debugging systems, it is easier to step through execution of a
function than a macro. Nonetheless, macros may be useful in some
circumstances.'''

    seeAlso     = { 'MISRA-2012 rule 4.9':
                    None,
                    'CERT PRE00-C':
                    'https://wiki.sei.cmu.edu/confluence/display/c/PRE00-C.+Prefer+inline+or+static+functions+to+function-like+macros' }

    sqLevel     = frozenset( [ 'safety' ] )

    def run( self, details, files ):
        if not details.isCPackage() and not details.isCppPackage():
            return NOT_APPLICABLE, 0, 0, 'no C/C++ code found in src/'

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
                            logging.info( 'C16: %s:%d - define "%s" is not uppercase',
                                            filePath, define.location[ 1 ], define.name )
                            failed += 1

                    for define in parser.localFnMacros.values():

                        logging.info( 'C16: %s:%d - function-like define "%s"',
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


class Rule_PY01( RemovedRule ):
    pass


class Rule_PY02( AbstractRule ):

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
        if not details.isPythonPackage():
            return NOT_APPLICABLE, 0, 0, 'no Python code found'

        logging.debug( "checking for access to private members from outside" )
        found  = 0
        regexp = re.compile( r'(\w+)\._(\w+)' )

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


class Rule_PY03( AbstractRule ):

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

    logging.info( "Hello, World!" )
    logging.info( 'x=%d', x )


    # possibility B (Any.h-equivalent)

    import ToolBOSCore.Util.Any

    Any.setDebugLevel( 3 )
    Any.log( 3, "Hello, World!" )
    Any.requireMsg( x == 123, "Oops..." )
    Any.requireIsDir( '/tmp' )
'''

    seeAlso     = { 'Any.py API documentation':
                    'namespaceToolBOSCore_1_1Util_1_1Any' }

    sqLevel     = frozenset()


class Rule_PY04( AbstractRule ):

    brief       = '''Prefer throwing exceptions over `exit()` within the
code.'''

    description = '''As a rule of thumb, Python functions should hardly
directly terminate the application. Prefer throwing an exception
(`SystemExit` if necessary), so that the caller at least has a chance to
appropriately handle it.

Mind that the caller might be another program containing a Python
interpreter. In such case the `sys.exit(0)` will terminate the whole
application with no chance for the program to react to such situation,
potentially causing data loss or inconsistent states.'''

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
        if not details.isPythonPackage():
            return NOT_APPLICABLE, 0, 0, 'no Python code found'

        logging.debug( "checking for calls to sys.exit(), os.exit() and os._exit()" )
        passed    = 0
        failed    = 0
        syntaxErr = 0

        binDir = os.path.realpath( os.path.join( details.topLevelDir, 'bin' ) )

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


class Rule_PY05( AbstractRule ):

    brief       = '''Use a static source code analyzer.'''

    description = '''The **PyCharm IDE** contains a static source code
analyzer for Python. The analyzer can also be used separately from commandline.

It reports problems in your Python scripts, such as wrong API usage,
incompatibility with certain Python versions, or questionable coding practics.

Please regularly inspect your scripts using PyCharm.'''

    seeAlso     = { 'PyCharm Home':
                    'https://www.jetbrains.com/pycharm' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Execute the PyCharm source code analyzer in batch-mode for each
            *.py file.
        """
        if not details.isPythonPackage():
            return NOT_APPLICABLE, 0, 0, 'no Python code found'

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


class Rule_PY06( AbstractRule ):

    brief       = '''Mind compatibility with Python versions 2.7 to 3.x'''

    description = '''Python comes in various language versions, featuring
different included packages or language constructs. However the install base
is quite heterogeneous.

Hence developers should pro-actively care that scripts are compatible with a
range of Python versions. At least compatibility with 2.7 and latest 3.x is
desired.

The **PyCharm IDE** can be configured to annotate code incompatible with
certain versions of Python.'''

    seeAlso     = { 'PyCharm Home':
                    'https://www.jetbrains.com/pycharm' }

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )


class Rule_MAT01( RemovedRule ):
    pass


class Rule_MAT02( AbstractRule ):

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
        if not details.isMatlabPackage():
            return NOT_APPLICABLE, 0, 0, 'no Matlab code found'

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


class Rule_MAT03( AbstractRule ):

    brief       = '''Avoid unintentional shadowing, i.e. function names should
be unique.'''

    description = '''Shadowing increases the possibility of unexpected
behavior. Check with `which -all` or `exist`.'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class Rule_MAT04( AbstractRule ):

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


class Rule_MAT05( AbstractRule ):

    brief       = '''Function header comments should support the use of
`help` and `lookfor`.
'''

    description = '''The `help` command prints the first contiguous block of
comments; `lookfor` searches the first comment line of all `*.m`-files on the
path.'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class Rule_DOC01( AbstractRule ):

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
     * \\mainpage
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
            return self._searchMatlab( details )

        elif details.isRTMapsPackage():
            return self._searchRTMaps( details )

        else:
            return self._searchDoxygen( details )


    def _searchDoxygen( self, details ):
        found      = False
        docDir     = os.path.relpath( os.path.join( details.topLevelDir, 'doc' ) )
        srcDir     = os.path.relpath( os.path.join( details.topLevelDir, 'src' ) )

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

                logging.info( 'DOC01: found: %s', filePath )

                if filePath in fileList:
                    content = FastScript.getFileContent( filePath )

                    if content.find( search ) != -1:
                        logging.debug( 'DOC01: %s: mainpage section found', filePath )
                        found = True
                        break
                    else:
                        found = False
                        logging.debug( 'DOC01: %s: mainpage section not found', filePath )
            else:
                logging.debug( 'DOC01: not found: %s', filePath )

        if found:
            return OK, 1, 0, 'documentation found'
        else:
            logging.info( 'DOC01: neither README.md nor doxygen mainpage found' )

            return FAILED, 0, 1, 'documentation not found'


    def _searchMatlab( self, details ):
        logging.debug( 'Matlab package detected, looking for HTML documentation' )

        # Matlab-packages do not contain a doxygen mainpage, hence only
        # check for existence of index.html after doc-build

        DocumentationCreator( details.topLevelDir ).generate()

        indexPath = os.path.join( details.topLevelDir, 'doc/html/index.html' )
        logging.debug( 'looking for documentation in: %s', indexPath )
        found     = os.path.exists( indexPath )

        if found:
            return OK, 1, 0, 'documentation (index.html) found'
        else:
            return FAILED, 0, 1, 'documentation (index.html) found'


    def _searchRTMaps( self, *kwargs ):
        return NOT_APPLICABLE, 0, 0, 'API docs not required for RTMaps components'


class Rule_DOC02( AbstractRule ):

    brief       = '''All public entities must be documented.'''

    description = '''Each function, class, method, macro, or datatype which
is publicly accessible must contain a basic description / explaination what
it is about.

Preferrably both arguments and return value (if any) should be documented.

For redundant cases, doxygen's `\\copydoc` command should be considered. This
command duplicates documentation at other locations, to avoid physical
duplication (for consistency reasons).'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class Rule_DOC03( AbstractRule ):

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
        Any.requireIsNotNone( details.packageCategory, 'Package category not specified. '
                                                       'Please check pkginfo.py '
                                                       'or CMakeLists.txt for category information.' )

        if details.isComponent():
            return NOT_APPLICABLE, 0, 0, 'examples not required for components'

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


class Rule_DOC04( RemovedRule ):
    pass


class Rule_SAFE01( AbstractRule ):

    brief       = '''Only C90 and C99 are allowed.'''

    description = '''MISRA-2012 only talks about C90 and C99, with no
language extensions.'''

    sqLevel     = frozenset( [ 'safety' ] )


class Rule_SAFE02( AbstractRule ):

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


class Rule_SAFE03( AbstractRule ):

    brief       = '''Memory must not be allocated after init phase (startup)
of the application.'''

    description = '''The memory consumption of a program shall be
deterministic, or at least constant at runtime.

It is a common prerequisite for safety-critical applications to allocate
required resources during intialization and do not change this until
termination.'''

    sqLevel     = frozenset( [ 'safety' ] )


class Rule_SAFE04( AbstractRule ):

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
        if not details.isCPackage() and not details.isCppPackage():
            return NOT_APPLICABLE, 0, 0, 'no C/C++ code found in src/'

        logging.debug( 'looking for "goto"-statement' )
        found  = 0

        for filePath in files:
            _, ext = os.path.splitext( filePath )
            if ext in C_CPP_FILE_EXTENSIONS:

                try:
                    content = FastScript.getFileContent( filePath )
                except ( IOError, OSError, UnicodeDecodeError ) as e:
                    logging.error( 'unable to open file: %s: %s', filePath, type( e ) )
                    found += 1
                    continue

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


class Rule_SAFE05( AbstractRule ):

    brief       = '''Multi-byte characters (f.i. Unicode) shall not be
used.'''

    description = '''Wide character types (requiring more than 1 Byte per
character, f.i. Unicode) can not be used with traditional string processing
functions and need special treatment when performing pointer arithmetics.

To avoid any risks arising from usage of wide characters multi-byte string
literals their use in safety-critical application is highly discouraged.'''

    seeAlso      = { 'CERT STR38-C':
                     'https://wiki.sei.cmu.edu/confluence/display/c/STR38-C.+Do+not+confuse+narrow+and+wide+character+strings+and+functions' }

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
        if not details.isCPackage() and not details.isCppPackage():
            return NOT_APPLICABLE, 0, 0, 'no C/C++ code found in src/'

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
                           'No wchar-functions found' )
            else:
                result = ( FAILED, passed, failed,
                           'wchar-functions found' )

        except EnvironmentError as e:
            logging.error( e )
            result = ( FAILED, passed, failed, e )


        return result


class Rule_SAFE06( AbstractRule ):

    brief       = '''Recursion (directly or indirectly) must not be used.'''

    description = '''Recursion carries with it the danger of exceeding
available stack space, which can lead to a serious failure. Unless recursion
is very tightly controlled, it is not possible to determine before execution
what the worst-case stack usage could be.

MISRA-2012 rule 17.2 requires the absence of recursion.'''

    sqLevel     = frozenset( [ 'safety' ] )


class Rule_SAFE07( AbstractRule ):

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


class Rule_SAFE08( AbstractRule ):

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

    sqLevel     = frozenset( [ 'safety' ] )

    def run( self, details, files ):
        """
            Checks that public C/C++ functions are not exposed as 'inline'.
        """
        if not details.isCPackage() and not details.isCppPackage():
            return NOT_APPLICABLE, 0, 0, 'no C/C++ code found in src/'

        logging.debug( "looking for public functions declared 'inline'" )
        passed = 0
        failed = 0

        for filePath in files:
            _, ext = os.path.splitext( filePath )

            if ext in C_CPP_HEADER_EXTENSIONS:
                content = FastScript.getFileContent( filePath )

                if content.find( 'inline' ) != -1:
                    logging.info( "SAFE08: %s: public API should not be declared 'inline'",
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


class Rule_SPEC01( AbstractRule ):

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


class Rule_SPEC02( AbstractRule ):

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


class Rule_SPEC03( AbstractRule ):

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


class Rule_SPEC04( AbstractRule ):

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


class Rule_SPEC05( AbstractRule ):

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

    Any.requireMsg( Any.isDir( details.buildDirArch ),
                    "%s: No such directory (forgot to compile?)" % details.buildDirArch )

    # this check can be removed in future when only bionic64 or its successor
    # are in use

    hostPlatform = getHostPlatform()
    msg          = 'check function not supported on platform=%s (only on bionic64)' % hostPlatform

    if hostPlatform != 'bionic64':
        raise EnvironmentError( msg )


    try:
        from ToolBOSCore.SoftwareQuality.CAnalyzer import CParser
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
    except ( AssertionError, IOError ) as e:
        # most likely the depend.make does not exist for this target,
        # this might happen if there are no dependencies by the target
        # or if this is a pseudo-target such as "doc" coming from
        # FindDoxygen.cmake
        logging.debug( e )
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
        instance is a class representing one particular SW Quality
        Guideline rule.
    """
    # retrieve all classes defined within this Python module,
    # and create instances

    result = []
    ctors  = {}
    tmp    = inspect.getmembers( sys.modules[__name__], inspect.isclass )

    for className, constructor in tmp:
        if className.startswith( 'Rule_' ):
            ctors[ className ] = constructor


    # keep sorting as appears in SQ Guideline

    for category in ( 'GEN', 'C', 'PY', 'MAT', 'JAVA', 'DOC', 'SAFE',
                      'MT', 'SPEC' ):
        for i in range(50):

            ruleID = '%s%02d' % ( category, i )

            try:
                func = ctors[ 'Rule_%s' % ruleID ]
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
