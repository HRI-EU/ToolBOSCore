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


import argparse
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
from ToolBOSCore.Packages.BSTPackage              import BSTSourcePackage
from ToolBOSCore.Packages.PackageDetector         import PackageDetector
from ToolBOSCore.Settings                         import ProcessEnv
from ToolBOSCore.Settings.ToolBOSConf             import getConfigOption
from ToolBOSCore.SoftwareQuality.Common           import *
from ToolBOSCore.Storage                          import SIT
from ToolBOSCore.Tools                            import Klocwork,\
                                                         Valgrind, Shellcheck
from ToolBOSCore.Util                             import Any, FastScript


FILE_EXTENSIONS_TO_EXCLUDE  = { 'GEN03': [ 'ipynb' ] }

class AbstractRule( object ):

    ruleID      = None
    name        = None
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

    name        = 'readability: English only'

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

        fileList = files[ 'all' ]

        for filePath in fileList:

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

    name        = 'portability: file encoding'

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

    utility = 'file'

    def run( self, details, files ):
        """
            Attempts to find special characters in source files. According
            to GEN-02 only ASCII- or UTF-8 files shall be used, and German
            Umlauts or Japanese characters must be avoided.
        """
        logging.debug( 'checking files for ASCII or UTF-8 charset' )

        passed  = 0
        failed  = 0
        ProcessEnv.requireCommand( self.utility )

        fileList = files[ 'all' ]

        for filePath in fileList:

            if self._checkFile( filePath ) is True:
                passed += 1
            else:
                failed += 1

        if failed == 0:
            result = ( OK, passed, failed,
                       'all files with ASCII or UTF-8 encoding' )
        else:
            result = ( FAILED, passed, failed,
                       'files with invalid encoding found' )

        return result

    def _checkFile( self, filePath ):
        # empty files will pass
        if Any.isEmptyFile( filePath ):
            logging.debug( '%s: file is empty', filePath )
            return True
        else:
            stdout = io.StringIO()
            stdout.truncate( 0 )

            cmd = f'{self.utility} -b {filePath}'
            FastScript.execProgram( cmd, stdout=stdout )

            encoding = stdout.getvalue().strip()

            # besides UTF-8 we also accept UTF-16
            if 'ASCII' in encoding or 'UTF-' in encoding:
                logging.debug( '%s: %s', filePath, encoding )
                result = True
            else:
                logging.info( 'GEN02: %s: invalid file (%s)',
                             filePath, encoding )
                result = False

            return result

class Rule_GEN03( AbstractRule ):

    name        = 'readability: max. linelength'

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

        fileList = files[ 'all' ]

        for filePath in fileList:

            fileExtension = filePath.split( "." )[ -1 ]
            if fileExtension in FILE_EXTENSIONS_TO_EXCLUDE[ 'GEN03' ]:
                continue

            longLines = 0
            maxLen    = 0
            try:
                lines = FastScript.getFileContent( filePath, splitLines=True )
            except ( IOError, OSError, UnicodeDecodeError ) as e:
                # If file has different encoding than UTF-8 then the default
                # encoding (UTF-8) won't work.
                logging.error( f'GEN03: unable toopen file: {filePath}: {e}' )
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

        passed = len(fileList) - failed

        if failed == 0:
            result = ( OK, passed, failed,
                       'all source files within length limit' )
        else:
            result = ( FAILED, passed, failed,
                       'source files exceeding width limit of %d (grace=%d)' % \
                       ( limit, maxWidth ) )

        return result


class Rule_GEN04( AbstractRule ):

    name        = 'compliance: copyright header'

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

        self._defaultCopyrightHeader = getCopyright().splitlines()


    def run( self, details, files ):
        """
            Checks if the HRI-EU copyright header is present.
        """
        logging.debug( 'checking files for copyright header' )

        failed    = 0

        if details.copyright:
            logging.info( 'found specific copyright information in pkgInfo.py' )
        else:
            logging.debug( 'searching for default copyright header' )

        fileList = files[ 'all' ]

        for filePath in fileList:
            try:
                content = FastScript.getFileContent( filePath )
            except ( IOError, OSError, UnicodeDecodeError ) as e:
                # If file has different encoding than UTF-8 then the default
                # encoding (UTF-8) won't work.
                logging.error( f'GEN04: unable toopen file: {filePath}: {e}' )
                failed += 1
                continue

            copyrightLines = self._getCopyrightLines( filePath, details.copyright )

            for line in copyrightLines:
                if content.find( line ) == -1:
                    logging.debug( "%s: '%s' not found", filePath, line )
                    logging.info( 'GEN04: copyright header missing in %s',
                                  filePath )
                    failed += 1
                    break

        passed = len( files[ 'all' ] ) - failed

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

    name        = 'portability: no Hungarian notation'

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

    name        = 'portability: no tabs in code'

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

        fileList = files[ 'all' ]

        for filePath in fileList:
            try:
                content = FastScript.getFileContent( filePath )
            except ( IOError, OSError, UnicodeDecodeError ) as e:
                # If file has different encoding than UTF-8 then the default
                # encoding (UTF-8) won't work.
                logging.error( f'GEN06: unable toopen file: {filePath}: {e}' )
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
                        logging.info( 'GEN06: tab found in %s:%d', filePath, lineNo )
                        reported += 1

                    if reported > 10:
                        logging.info( 'GEN06: tab found in %s:[...]', filePath )
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

    name        = 'reliability: tests present'

    brief       = 'Libraries and applications should contain a unittest.'

    description = '''Even if covering just a small part, some unittests make
you sleep better: When executed automatically (e.g. within CI/CD pipelines) they
show:

  * the code is compilable (f.i. on multiple platforms)
  * no broken dependencies, such as API changes
  * executables are runnable (no undefined symbols, missing files,...)
  * tested code somehow behaves as expected

Please provide a generic `unittest.sh` (Linux) and/or `unittest.bat`
(Windows) in the top-level directory of the package. This shall invoke any
package-specific testsuite.

You may also override the filename of such scripts using settings in the
pkgInfo.py, e.g.:

scripts          = { 'unittest': 'myScript.sh' }
'''

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks if the package provides unittests.
        """
        Any.requireIsNotNone( details.packageCategory, 'Package category not specified. '
                                                       'Please check pkginfo.py '
                                                       'for category information.' )

        if details.isComponent():
            return NOT_APPLICABLE, 0, 0, 'unittests not required for components'


        if 'unittest' in details.scripts:
            candidates = [ details.scripts[ 'unittest' ] ]
        else:
            candidates = [ 'unittest.sh', 'unittest.bat' ]

        logging.info( 'GEN07: looking for %s', candidates )
        found = False

        for fileName in candidates:
            if os.path.exists( fileName ):
                logging.debug( '%s found', fileName )
                found = True

        if found:
            result = ( OK, 1, 0, 'unittests found' )
        else:
            result = ( FAILED, 0, 1, 'unittests not found' )

        return result


class Rule_GEN08( AbstractRule ):

    name        = 'compliance: 3rd-party material'

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
                    'https://github.com/HRI-EU/ToolBOSCore/blob/main/doc/ToolBOSCore/Concepts/SourceTreeConventions.md',

                    'Installation conventions':
                    'https://github.com/HRI-EU/ToolBOSCore/blob/main/doc/ToolBOSCore/Concepts/SourceTreeConventions.md' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )


class Rule_GEN09( AbstractRule ):

    name        = 'compliance: 3rd-party licenses'

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

    name        = 'maintainability: VCS usage'

    brief       = '''Put package under version control system (Git).'''

    description = '''A version control system serves several purposes:

  * preserve individual source code states over time
  * track or rollback modifications
  * agreed "main" location
  * avoids chaos of various copies + patchfiles
  * central backup'''

    seeAlso     = { 'Git HowTo':
                    'https://hri-wiki.honda-ri.de/Git' }

    sqLevel     = frozenset( [ 'cleanLab', 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Checks if the package is managed via VCS.
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

    name        = 'maintainability: issue tracking'

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

    name        = 'reliability: deterministic mode'

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

    name        = 'reliability, safety: usage of return-values'

    brief       = '''Always check return-values of function'''

    description = '''Return values, especially those indicating errors,
should not be silently ignored. If some return value is not very useful
(as could be those of `printf()` or `close()`), you should provide a cast
and/or comment that it has been ignored on purpose.'''

    sqLevel     = frozenset()


class Rule_GEN14( AbstractRule ):

    name        = 'safety, maintainability: cyclomatic complexity'

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

    name        = 'interoperability: exit() calls'

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

        regexpExit1 = re.compile( r'\sexit\s*\(' )
        regexpExit2 = re.compile( r'\s_exit\s*\(' )
        regexpAbort = re.compile( r'\sabort\s*\(' )

        fileList = files[ 'cpp' ] + files[ 'c' ] + files[ 'cppHeaders' ]

        for filePath in fileList:
            if '/bin/' in filePath or '/examples/' in filePath or '/test/' in filePath:
                logging.debug( '%s: skipping file with excluded directory '
                               '[ "bin", "examples", "test" ]', filePath )

                continue

            try:
                content = FastScript.getFileContent( filePath )
            except ( IOError, OSError, UnicodeDecodeError ) as e:
                # If file has different encoding than UTF-8 then the default
                # encoding (UTF-8) won't work.
                logging.error( f'C01: unable toopen file: {filePath}: {e}' )
                failed += 1
                continue

            if regexpExit1.search( content ):
                logging.info( f'C01: exit() found in {filePath}' )
                failed += 1
            elif regexpExit2.search( content ):
                logging.info( f'C01: _exit() found in {filePath}' )
                failed += 1
            elif regexpAbort.search( content ):
                logging.info( f'C01: abort() found in {filePath}' )
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

    name        = 'interoperability: C++ linkage'

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


class Rule_C03( AbstractRule ):

    name        = 'interoperability: macro names'

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


class Rule_C04( AbstractRule ):

    name        = 'security: void argument list'

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


class Rule_C05( AbstractRule ):

    name        = 'interoperability: inclusion guards'

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
        logging.debug( 'checking header file inclusion guards' )

        blacklist = frozenset( [ 'documentation.h' ] )

        fileList = files[ 'cppHeaders' ]

        for filePath in fileList:

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

            macroName   = moduleUpper.replace( '.', '_' )
            macroName   = macroName.replace( '-', '_' )
            safeguard   = '#ifndef %s_H' % macroName
            regexp      = re.compile( r'#ifndef\s(\S*?%s\S*_H\S*)' % macroName )

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

    name        = 'consistency: logging'

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

    seeAlso     = { 'CERT ERR00-CPP':
                    'https://wiki.sei.cmu.edu/confluence/display/c/ERR00-C.+Adopt+and+implement+a+consistent+and+comprehensive+error-handling+policy' }

    sqLevel     = frozenset()


class Rule_C08( AbstractRule ):

    name        = 'portability: datatypes'

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

    seeAlso     = { 'CERT NUM03-J':
                    'https://wiki.sei.cmu.edu/confluence/display/java/NUM03-J.+Use+integer+types+that+can+fully+represent+the+possible+range+of++unsigned+data',

                    'CERT INT31-C':
                    'https://wiki.sei.cmu.edu/confluence/display/c/INT31-C.+Ensure+that+integer+conversions+do+not+result+in+lost+or+misinterpreted+data',

                    'CERT INT08-C':
                    'https://wiki.sei.cmu.edu/confluence/display/c/INT08-C.+Verify+that+all+integer+values+are+in+range' }

    sqLevel     = frozenset()


class Rule_C09( AbstractRule ):

    name        = 'scalability: BST.py compatibility'

    brief       = '''Package can be built using `BST.py.`'''

    description = '''For ensuring that our software is compilable and
unittests pass, HRI-EU software is regularly being rebuilt and unittests get
executed.

As a prerequisite for this, the Nightly Build process must be able to compile
arbitrary packages and invoke their unittests. The `BST.py` serves as generic
interface for both humans and machines.

Hence, please ensure that your package is compatible with `BST.py`.'''

    seeAlso     = { 'BST.py documentation':
                    'https://github.com/HRI-EU/ToolBOSCore/blob/main/doc/ToolBOSCore/Tools/BuildSystemTools/BuildSystemTools.md' }

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

    name        = 'security, reliability: static analysis'

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
                    'https://hri-wiki.honda-ri.de/Klocwork' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Execute the Klocwork source code analyzer in CLI mode.
        """
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
            Klocwork.codeCheck( kwDir, output, output, logToConsole=True )

            output = output.getvalue()

            if Any.getDebugLevel() > 3:
                logging.info( 'output:\n%s', output )

            if output:
                defects = Klocwork.parseCodeCheckResult( output )

                if defects:
                    for item in defects:
                        logging.info( 'C10: %s:%s: %s [%s]', *item )
                        failed += 1

        except ( AssertionError, subprocess.CalledProcessError,
                 EnvironmentError, RuntimeError ) as e:

            logging.info( 'output:\n%s', output.getvalue() )

            logging.error( 'C10: %s', e )
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

    name        = 'security, maintainability: setjmp() and longjmp()'

    brief       = '''`setjmp()` and `longjmp()` are forbidden'''

    description = '''The two functions `setjmp()` and `longjmp()` make the
execution paths through the code overly complicated. Do not use them.'''

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )


class Rule_C12( AbstractRule ):

    name        = 'security: memory allocation'

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

        if not details.hasMainProgram( files[ 'all' ] ):
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

        # source the package before running Valgrind

        try:
            ProcessEnv.sourceFromHere()
            logging.debug( "sourcing %s", os.getcwd() )
        except AssertionError as e:
            logging.error( e )

            return FAILED, 0, 0, 'unable to run valgrind'

        # get the package dependencies, if found, source the dependencies
        # before running Valgrind

        bstSourcePackage = BSTSourcePackage()

        bstSourcePackage.open( os.getcwd() )
        bstSourcePackage.retrieveDependencies( True )

        deps = bstSourcePackage.depSet
        logging.debug( "Package dependencies: %s", deps )

        if deps:
            logging.info( "sourcing dependencies of %s", details.canonicalPath )
            for dep in deps:
                ProcessEnv.source( SIT.strip( dep ) )
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
                # TBCORE-2118: executables may return non-zero exit codes,
                # do not consider those as failure!

                logging.debug( e )
                failed = False
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
                       '%d executable%s failed' % ( failedExecutables,
                                                    's' if failedExecutables > 1 else '' ) )

        return result



class Rule_C13( AbstractRule ):

    name        = 'security, maintainability: clean compilation'

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

    name        = 'security, maintainability: global variables'

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

    name        = 'maintainability: function-like macros'

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


class Rule_PY01( RemovedRule ):
    pass


class Rule_PY02( AbstractRule ):

    name        = 'maintainability: private members'

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
        if files[ 'python' ] == [ './pkgInfo.py' ]:
            return NOT_APPLICABLE, 0, 0, 'no Python code found'

        logging.debug( "checking for access to private members from outside" )
        found   = 0
        errors  = 0
        regexp  = re.compile( r'(\w+)\._(\w+)' ) # capture private members
        dunder  = re.compile( r'_(\w+)__' )      # capture dunder methods

        for filePath in files[ 'python' ]:
            if os.path.exists( filePath ):
                try:
                    content = FastScript.getFileContent( filePath, splitLines=True )
                except ( IOError, OSError, UnicodeDecodeError ) as e:
                    # If file has different encoding than UTF-8 then the default
                    # encoding (UTF-8) won't work.
                    logging.error( f'PY02: unable to open file: {filePath}: {e}' )
                    errors += 1
                    continue

                for line in content:
                    tmp = regexp.search( line )

                    if tmp:
                        allowed = dunder.search( tmp.group(2) )
                        if tmp.group(1) not in ( 'self', 'cls' ) and not allowed:
                            logging.info( 'PY02: %s: access to private member (%s)',
                                          filePath, tmp.group() )
                            found += 1

        if errors > 0:
            result = ( FAILED, 0, 1,
                       '%d error(s) occurred during check' % errors )
        elif found == 0:
            result = ( OK, 1, 0,
                       'no access to private members from outside' )
        else:
            result = ( FAILED, 0, 1,
                       'found %d accesses to private members from outside' % found )

        return result


class Rule_PY03( AbstractRule ):

    name        = 'consistency: logging'

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

    sqLevel     = frozenset()


class Rule_PY04( AbstractRule ):

    name        = 'interoperability: exception handling'

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
        if files[ 'python' ] == [ './pkgInfo.py' ]:
            return NOT_APPLICABLE, 0, 0, 'no Python code found'

        logging.debug( "checking for calls to sys.exit(), os.exit() and os._exit()" )
        passed = 0
        failed = 0
        errors = 0
        binDir = os.path.realpath( os.path.join( details.topLevelDir, 'bin' ) )

        for filePath in files[ 'python' ]:
            if not filePath.startswith( binDir ):

                try:
                    code = FastScript.getFileContent(filePath)
                    exitCalls = self.getExitCalls( code )
                except SyntaxError as e:
                    logging.error( f'PY04: {e.__class__.__name__} error in file {filePath}' )
                    errors += 1
                    continue
                except UnicodeDecodeError as e:
                    # If file has different encoding than UTF-8 then the default
                    # encoding (UTF-8) won't work.
                    logging.error( f'PY04: unable to open file: {filePath}: {e}' )
                    errors += 1
                    continue

                if not exitCalls:
                    passed += 1
                else:
                    # logging.info(exitCalls)
                    for call in exitCalls:
                        logging.info( 'PY04: %s:%s: found %s() call',
                                      filePath, call[1], call[0] )
                    failed += len( exitCalls )


        if errors > 0:
            msg    = '%d error(s) occurred during check' % errors
            status = FAILED
        elif failed:
            msg    = 'found %d exit() calls' % failed
            status = FAILED
        else:
            msg    = 'no exit() calls found'
            status = OK

        return status, passed, failed, msg


class Rule_PY05( AbstractRule ):

    name        = 'security, reliability: static analysis'

    brief       = '''Use a static source code analyzer.'''

    description = '''PY05 checker uses pylint as a linter for static code
analysis of Python files. Pylint can also be used separately from commandline.

It reports problems in your Python scripts, such as wrong API usage,
incompatibility with certain Python versions, or questionable coding practices.

By default the checker reports only errors in your python code.
You can configure the checker in the following two steps:

  * Add a `pyproject.toml` file and configure it as per your project requirement.
  * Specify path to the `pyproject.toml` file in pkgInfo.py as: 
  'pylintConf' = '/path/to/pylint/conf'

Please regularly inspect your scripts using Pylint.'''

    seeAlso     = { 'Pylint Home':
                    'https://pylint.pycqa.org/en/latest/user_guide/run.html' }

    sqLevel     = frozenset( [ 'basic', 'advanced', 'safety' ] )

    def run( self, details, files ):
        """
            Execute the PyCharm source code analyzer in batch-mode for each
            *.py file.
        """
        if files[ 'python' ] == [ './pkgInfo.py' ]:
            return NOT_APPLICABLE, 0, 0, 'no Python code found'

        from ToolBOSCore.Tools import Pylint

        logging.info( 'performing source code analysis using pylint' )
        passed        = 0
        failed        = 0
        overallIssues = 0

        timestamp      = FastScript.now().strftime( '%Y-%m-%d_%H-%M-%S' )
        outputFileName = f'{timestamp}_pylint.log'
        logging.info( 'PY05: using pylint config file: %s', details.pylintConf )

        # pylint provides configuration '--output=<file>' to redirect output
        # to file, while using this option it writes additional characters to
        # file, making it difficult to read the results. for better readability
        # we are using sys.stdout to redirect the output to a file

        sys.stdout = open( outputFileName, 'w' )
        for filePath in files[ 'python' ]:
            if not ( filePath.endswith( '__init__.py' ) or
                     filePath.endswith( 'pkgInfo.py' ) ) :

                print( "Analyzing file: " + filePath )

                pylintResult   = Pylint.getPylintResult( filePath, details.pylintConf )
                codeIssues     = Pylint.getTotalPylintIssues( pylintResult )
                overallIssues += codeIssues

                if codeIssues > 1:
                    logging.info( 'PY05: %s: %d issues', filePath, codeIssues )
                    failed += 1
                elif codeIssues == 1:
                    logging.info( 'PY05: %s: %d issue', filePath, codeIssues )
                    failed += 1
                else:
                    passed += 1
        sys.stdout.close()
        sys.stdout = sys.__stdout__

        if failed == 0:
            result = ( OK, passed, failed,
                       'no issues found by pylint' )
        else:
            msg = 'pylint found %s issues' % overallIssues
            result = ( FAILED, passed, failed, msg )
            logging.info( 'for detailed code issues refer to: %s',
                          outputFileName )
        return result


class Rule_PY06( AbstractRule ):

    name        = 'interoperability: Python version compatibility'

    brief       = '''Mind compatibility with different Python versions'''

    description = '''Python comes in various language versions, featuring
different included packages or language constructs. However the install base
is quite heterogeneous.

Hence developers should pro-actively care that scripts are compatible with a
range of Python versions. At least compatibility with 3.7 and higher is
desired.

The **PyCharm IDE** can be configured to annotate code incompatible with
certain versions of Python.'''

    seeAlso     = { 'PyCharm Home':
                    'https://www.jetbrains.com/pycharm' }

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )


class Rule_DOC01( AbstractRule ):

    name        = 'understandability: documentation present'

    brief       = '''The main functionality (why this package exists) should
be briefly documented.'''

    description = '''Other people should be able to roughly understand what
the package contains, and if it might be of interest for them.

Basic documentation can also programmatically be searched for keywords, e.g.
in case you don't precisely remember the name of a package anymore.

Documentation should be maintained under one of the following locations:

* README.md (recommended)
* doc/documentation.h
* doc/Mainpage.dox
* doc/Mainpage.md
* doc/html/index.html
* src/__init__.py
* src/documentation.h
* src/<PackageName>.h
* src/<PackageName>/__init__.py

Alternatively, you may specify the list of documentation files in the
pkgInfo.py file.
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
        if details.docFiles:
            return self._searchDocFiles( details )

        elif details.isMatlabPackage():
            return self._searchMatlab( details )

        elif details.isRTMapsPackage():
            return self._searchRTMaps( details )

        else:
            return self._searchDoxygen( details )


    def _searchDocFiles( self, details ):
        docFiles   = details.docFiles
        found      = False
        expected   = len( docFiles )

        logging.debug( 'searching for: %s', docFiles )

        for docFile in docFiles:
            if os.path.exists( docFile ):
                logging.info( f'DOC01: {docFile} found' )
                found += 1
            else:
                logging.error( f'DOC01: {docFile} not found' )

        if found == expected:
            return OK, found, 0, 'documentation found'
        else:
            return FAILED, found, expected - found, 'not all documentation found'


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
                if Any.isFileNonEmpty( filePath ):
                    found = True
                    logging.info( 'DOC01: found: %s', filePath )
                else:
                    found = False
                    logging.info( 'DOC01: found empty file: %s', filePath )

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

    name        = 'understandability: public API documentation'

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

    name        = 'understandability: examples present'

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

    name        = 'security, portability: C90 and C99 only'

    brief       = '''Only C90 and C99 are allowed.'''

    description = '''MISRA-2012 only talks about C90 and C99, with no
language extensions.'''

    sqLevel     = frozenset( [ 'safety' ] )


class Rule_SAFE02( AbstractRule ):

    name        = 'security: plausabiity checks'

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

    name        = 'security: no dynamic memory allocation during runtime'

    brief       = '''Memory must not be allocated after init phase (startup)
of the application.'''

    description = '''The memory consumption of a program shall be
deterministic, or at least constant at runtime.

It is a common prerequisite for safety-critical applications to allocate
required resources during intialization and do not change this until
termination.'''

    sqLevel     = frozenset( [ 'safety' ] )


class Rule_SAFE04( AbstractRule ):

    name        = 'security, maintainability: no goto'

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
        errors = 0

        fileList = files[ 'c' ] + files[ 'cpp' ]

        for filePath in fileList:

            try:
                content = FastScript.getFileContent( filePath )
            except ( IOError, OSError, UnicodeDecodeError ) as e:
                logging.error( f'SAFE04: unable to open file: {filePath}: {e}' )
                errors += 1
                continue

            if content.find( ' goto ' ) > 0:
                logging.info( 'SAFE04: goto-statement found: %s', filePath )
                found += 1

        if errors > 0:
            result = ( FAILED, 0, 1,
                       '%d error(s) occurred during check' % errors )
        elif found == 0:
            result = ( OK, 1, 0,
                       "'goto' not used" )
        else:
            result = ( FAILED, 0, 1,
                       "found %d 'goto'-statements" % found )

        return result


class Rule_SAFE05( AbstractRule ):

    name        = 'security, portability: no multi-byte characters'

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


class Rule_SAFE06( AbstractRule ):

    name        = 'security: no recursion'

    brief       = '''Recursion (directly or indirectly) must not be used.'''

    description = '''Recursion carries with it the danger of exceeding
available stack space, which can lead to a serious failure. Unless recursion
is very tightly controlled, it is not possible to determine before execution
what the worst-case stack usage could be.

MISRA-2012 rule 17.2 requires the absence of recursion.'''

    sqLevel     = frozenset( [ 'safety' ] )


class Rule_SAFE07( AbstractRule ):

    name        = 'security: safe string-processing only'

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

    sqLevel     = frozenset( [ 'safety' ] )


class Rule_SAFE08( AbstractRule ):

    name        = 'security, reliability: no inline in public API'

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
        logging.debug( "looking for public functions declared 'inline'" )
        passed = 0
        failed = 0

        fileList = files[ 'cppHeaders' ]

        for filePath in fileList:

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

    name        = 'security, reliability: static analysis'

    brief       = '''Safety-critical car applications are requested to use
"state-of-the-art" tools (e.g. Klocwork) for checking code quality.'''

    description = '''Safety-critical car applications are requested to use
"state-of-the-art" tools (e.g. Klocwork) for checking code quality.'''

    seeAlso     = { 'MISRA coding standards in Klocwork':
                    'http://www.klocwork.com/products-services/klocwork/detection/misra-coding-standards',

                    'Mapping of MISRA rules to Klocwork checkers':
                    'http://docs.klocwork.com/Insight-10.0/MISRA-C_rules_mapped_to_Klocwork_checkers' }

    sqLevel     = frozenset( [ 'safety' ] )


class Rule_SPEC02( AbstractRule ):

    name        = 'portability: MSVC-compliant variable declaration'

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

    name        = 'portability: POSIX functions'

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

    sqLevel     = frozenset()


class Rule_SPEC04( AbstractRule ):

    name        = 'reliability: thread-safeness'

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

    name        = 'reliability: re-entrancy'

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

    seeAlso     = { 'Wikipedia: Thread safety':
                    'https://en.wikipedia.org/wiki/Thread_safety' }

    sqLevel     = frozenset( [ 'advanced', 'safety' ] )


class Rule_BASH01( AbstractRule ):

    name        = 'security: correct quoting'

    brief       = '''Strings, variables, and command-substitutions should
always be quoted, unless word-splitting is explicitly desired.'''

    description = '''Quoting prevents word-splitting, which is done
automatically by bash, and can result in more arguments being given to the
preceding command or in spaces not being honored.
'''

    goodExample = '''
    users=('Adam Wilson' 'Brian May' 'Maggy Reilly')
    for user in "${users[@]}"; do
        echo "${user}"
    done

Output:

    Adam Wilson
    Brian May
    Maggy Reilly
    '''

    badExample  = '''
    users=('Adam Wilson' 'Brian May' 'Maggy Reilly')
    for user in ${users[@]}; do
        echo ${user}
    done

Output:

    Adam
    Wilson
    Brian
    May
    Maggy
    Reilly
    '''

    seeAlso     = { 'Shellcheck SC2046, SC2048, SC2068, SC2248, SC2248':
                    'https://gist.github.com/eggplants/9fbe03453c3f3fd03295e88def6a1324#file-_shellcheck-md',

                    'Bash Pitfalls':
                    'https://mywiki.wooledge.org/BashPitfalls#echo_.24foo' }

    sqLevel     = frozenset( [ 'basic', 'advanced' ] )

    def run( self, details, files ):
        """
            Checks that strings, variables, and command-substitutions in Bash-scripts
            are quoted to avoid word-splitting and globbing.
        """
        logging.debug( "checking that strings, variables, substitutions are quoted" )
        passed = 0
        failed = 0

        fileList = files[ 'bash' ]

        for filePath in fileList:
            results = Shellcheck.checkScript( filePath,
                                              '2046,2048,2068,2086,2248',
                                              'quote-safe-variables')
            if results[0]:
                _printErrorReport( 'BASH01',
                                   'unquoted strings, variables, substitutions',
                                   filePath, results[1] )
                failed += 1
            else:
                passed += 1

        if failed == 0:
            result = ( OK, passed, failed,
                       'secure quoting applied everywhere' )
        else:
            result = ( FAILED, passed, failed,
                       'found occurrences of unsecure quoting' )

        return result


class Rule_BASH02( AbstractRule ):

    name        = "security: Bash-Builtin's"

    brief       = '''Always use the safe built-in [[ for tests in bash-scripts.'''

    description = '''This construct is safer than the single [, because expressions
work as expected. The single [ has quirky behavior for e.g. comparisons with < and >,
which are almost always interpreted as redirection and definitely not what you
intended. [[ parses the whole command before it is being expanded, which yields
correct evaluation of expressions with empty variables (if quoting is omitted).
This makes it safer.
This construct is also faster, because it is a bash-builtin, whereas the single
[ spawns a separate process.'''

    goodExample = '''
    var=a
    [[ $var > b ]] && echo "True"|| echo "False"
    '''

    badExample  = '''
    var=a
    [ $var > b ] && echo "True"|| echo "False"
    '''

    seeAlso     = { 'Bash best practices':
                    'https://mywiki.wooledge.org/BashGuide/Practices#Bash_Tests' }

    sqLevel     = frozenset( [ 'basic', 'advanced' ] )


class Rule_BASH03( AbstractRule ):

    name        = 'maintainability: subshell invocation'

    brief       = '''Use $() instead of back-ticks for command-substitution.'''

    description = '''The backticks for command-substitution are deprecated and
problematic:

1. Backslashes are not handled as you would expect, e.g. "\\\\a" produces "a" and
not "\\a".

2. Nesting backticks and quotes is difficult, as the backticks and nested
quotes inside backticks need to be escaped.

3. Not all valid scripts can be embedded in backticks.
The above issues do not exist for $(). This is accomplished by $() enforcing a
new context for quoting and by separately parsing the contents inside the
parenthesis.
'''

    goodExample = '''
    a=$(dirname $(which grep))
    '''

    badExample  = r'''
    a=`dirname \`which grep\``
    '''

    seeAlso     = { 'Shellcheck SC2006':
                    'https://gist.github.com/eggplants/9fbe03453c3f3fd03295e88def6a1324#file-_shellcheck-md',

                    'BashFAQ':
                    'https://mywiki.wooledge.org/BashFAQ/082',

                    'Bash-hackers':
                    'https://wiki.bash-hackers.org/syntax/expansion/cmdsubst' }

    sqLevel     = frozenset( [ 'basic', 'advanced' ] )

    def run( self, details, files ):
        """
            Checks that $() is used for command-substitution instead of backticks.
        """
        logging.debug( "checking that $() is used for command-substitution" )
        passed = 0
        failed = 0

        fileList = files[ 'bash' ]

        for filePath in fileList:
            results = Shellcheck.checkScript( filePath, '2006' )
            if results[0]:
                _printErrorReport( 'BASH03',
                                   'command-substitution with backticks',
                                   filePath, results[1] )
                failed += 1
            else:
                passed += 1

        if failed == 0:
            result = ( OK, passed, failed,
                       'correct subshell invocations found' )
        else:
            result = ( FAILED, passed, failed,
                       'found subshell invocations using backticks' )

        return result


class Rule_BASH04( AbstractRule ):

    name        = 'security, reliability: array usage'

    brief       = '''Use an array instead of one string when passing arguments.'''

    description = '''Arguments should always be passed as an array to a script
or function. Splitting a string into separate parts that contain spaces is
problematic: either it does not split at all or the separate parts
split at their spaces, too. Furthermore, single quotes used to mark a part
will remain on the extracted part and have to be stripped. All this will
make the code much more complicated. The handling of an array on the other
hand is straight-forward.
'''

    goodExample = '''
    #!/bin/bash
    args=(--only-matching --no-filename "args for grep")
    grep "${args[@]}" "${0}"

output:

    args for grep
    '''

    badExample  = '''
    #!/bin/bash
    args='--only-matching --no-filename "args for grep"'
    grep ${args} "${0}"

output:

    grep: for: No such file or directory
    grep: grep": No such file or directory
    "args
    '''

    seeAlso     = { 'Shellcheck SC2089, SC2090':
                    'https://gist.github.com/eggplants/9fbe03453c3f3fd03295e88def6a1324#file-_shellcheck-md' }

    sqLevel     = frozenset( [ 'basic', 'advanced' ] )

    def run( self, details, files ):
        """
            Checks that an array is used instead of a string when passing arguments.
        """
        logging.debug( "checking that an array is used instead of a string when passing arguments" )
        passed = 0
        failed = 0

        fileList = files[ 'bash' ]
        for filePath in fileList:
            results = Shellcheck.checkScript( filePath, '2089,2090' )
            if results[0]:
                _printErrorReport( 'BASH04',
                                   'string used for passing arguments',
                                   filePath, results[1] )
                failed += 1
            else:
                passed += 1

        if failed == 0:
            result = ( OK, passed, failed,
                       'correct usage of Bash arrays' )
        else:
            result = ( FAILED, passed, failed,
                       'found strings that should be arrays' )

        return result


class Rule_BASH05( AbstractRule ):

    name        = 'maintainability: use long form of parameter'

    brief       = '''Use the long form of parameters if available to keep scripts readable.'''

    description = '''External programs like e.g. grep, find, or rsync have a
lot of parameters. From the short form of those parameters it is not always
obvious what they are for. The long form on the other hand is mostly
descriptive and does not need any further explanation through e.g.
comments. Using the long form (if available) will make scripts more
readable and a little more self-explanatory.
'''

    goodExample = '''
    date | grep --extended-regexp --only-matching '([0-9]{2}[:]){2}[0-9]{2}'
    '''

    badExample  = '''
    date | grep -Eo '([0-9]{2}[:]){2}[0-9]{2}'
    '''

    seeAlso     = { 'CheatSheet':
                    'https://bertvv.github.io/cheat-sheets/Bash.html' }

    sqLevel     = frozenset( [ 'basic', 'advanced' ] )


class Rule_BASH06( AbstractRule ):

    name        = 'security: referencing of variables'

    brief       = '''Use braces when referring to variables.'''

    description = '''Braces are needed for

1. expanding variables into strings, e.g. ${var}appendage,

2. array-references, e.g. ${array[2]},

3. parameter-expansion, e.g. ${filename%.*}

4. expanding positional parameters > 9, e.g. ${10}, ${11}, ...

To deliver a consistent appearance throughout the whole script you should
use braces even if they are not strictly necessary. This will prevent
forgetting the braces if they are needed, which will lead to strange
errors or behaviour.
'''

    goodExample = '''
    echo ${foo}
    '''

    badExample  = '''
    echo $foo
    '''

    seeAlso     = { 'Shellcheck':
                    'https://github.com/koalaman/shellcheck/wiki/SC2250',

                    'CheatSheet':
                    'https://bertvv.github.io/cheat-sheets/Bash.html' }

    sqLevel     = frozenset( [ 'basic', 'advanced' ] )

    def run( self, details, files ):
        """
            Checks that variables in Bash-scripts are referred to using braces.
        """
        logging.debug( "checking that variables are referred to using braces" )
        passed = 0
        failed = 0

        fileList = files[ 'bash' ]

        for filePath in fileList:
            results = Shellcheck.checkScript( filePath, '2250', 'require-variable-braces')
            if results[0]:
                _printErrorReport( 'BASH06',
                                   'variables referred to without braces',
                                   filePath, results[1] )
                failed += 1
            else:
                passed += 1

        if failed == 0:
            result = ( OK, passed, failed,
                       'correct referencing of variables' )
        else:
            result = ( FAILED, passed, failed,
                       'found insecure referencing of variables' )

        return result


class Rule_BASH07( AbstractRule ):

    name        = 'reliability: strict shell settings'

    brief       = '''Use `set -euo pipefail` to abort script on errors and unbound variables.'''

    description = '''The command `set -euo pipefail` should be placed at the top
of the script right after the copyright-header. This has the following consequences for
the rest of the script:

1. If a pipeline, simple-command, list, or compound-command exits with a
non-zero status, the script is immediately exited.

2. Unset variables or parameters are treated as an error and the script
exits immediately.

3. If one command in a pipeline returns with a non-zero status the whole
pipeline fails.

These consequences make the script safer, because an immediate exit after
an error prevents an execution of subsequent commands in an erroneous
context, which is the default for bash.

To facilitate debugging you can use  `set -x` as follows:

    if [[ "${VERBOSE}" == "TRUE" ]]
    then
        set -x
    else

`set -x` will print every line in the script before it being executed. It can be
placed anywhere after `set -euo pipefail`.
'''

    goodExample = '''
    [...]

    set -euo pipefail

    SCRIPT_DIR=$(dirname $(readlink -f "$0"))

    source ${SCRIPT_DIR}/config/defaults.config

    [...]
    '''

    badExample  = '''
    [...]

    SCRIPT_DIR=$(dirname $(readlink -f "$0"))

    source ${SCRIPT_DIR}/config/defaults.config

    [...]
    '''

    seeAlso      = { 'CheatSheet':
                     'https://bertvv.github.io/cheat-sheets/Bash.html' }

    sqLevel      = frozenset( [ 'basic', 'advanced' ] )

    skippedFiles = [ 'BashSrc', 'useFromHere.sh' ]


    def run( self, details, files ):
        """
            Checks that Bash-scripts have a set -euo pipefail or
            a set -euxo pipefail line.
        """
        logging.debug( 'checking strict shell settings' )

        passed     = 0
        failed     = 0

        fileList = files[ 'bash' ]

        for filePath in fileList:
            if os.path.basename( filePath ) in self.skippedFiles:
                continue

            lines    = FastScript.getFileContent( filePath, splitLines=True )
            foundSet = False
            setArgs  = argparse.Namespace()

            # initialize setArgs namespace properly
            _parseSet( 'set', setArgs )

            for line in lines:
                setPos = line.find( 'set' )
                if setPos != -1:
                    _parseSet( line[setPos:], setArgs )

                    if setArgs.e and setArgs.u and setArgs.p:
                        foundSet = True
                        break

            if foundSet:
                passed += 1
            else:
                failed += 1
                results = [ 'Please add the following at the top of your script:' ]
                if not setArgs.e:
                    results.append( "'set -o errexit' or 'set -e'" )
                if not setArgs.u:
                    results.append( "'set -o nounset' or 'set -u'")
                if not setArgs.p:
                    results.append( "'set -o pipefail'")
                _printErrorReport( 'BASH07',
                                   'strict settings missing',
                                   filePath, results )
        if failed == 0:
            result = ( OK, passed, failed, 
                       'strict shell settings found' )
        else:
            result = ( FAILED, passed, failed,
                       'strict shell settings missing' )

        return result


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
                      'MT', 'SPEC', 'BASH' ):
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


def _parseSet( line, namespace ):
    """
        Parses bash's set arguments in line and puts them into namespace if found.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument( '-o', nargs='+', action='append' )
    parser.add_argument( '-e', action='store_true' )
    parser.add_argument( '-u', action='store_true' )
    parser.add_argument( '-x', action='store_true' )
    parser.add_argument( '-p', action='store_true' )
    parser.parse_known_args( line.split(), namespace=namespace )

    if hasattr( namespace, 'o' ) and namespace.o is not None and len(namespace.o) > 0:
        for arg in namespace.o:
            if arg[0] == 'errexit':
                namespace.e = True
            if arg[0] == 'nounset':
                namespace.u = True
            if arg[0] == 'pipefail':
                namespace.p = True
            if arg[0] == 'xtrace':
                namespace.x = True


def _printErrorReport( ruleName, description, filePath, explanation ):
    logging.info( "%s: %s", ruleName, '-' * 80 )
    logging.info( "%s: %s: %s", ruleName, filePath, description )

    if type( explanation ) is list:
        for line in explanation:
            logging.info( "%s: %s", ruleName, line )
    else:
        logging.info( "%s: %s", ruleName, explanation )

    logging.info( "%s: %s", ruleName, '-' * 80 )


# EOF
