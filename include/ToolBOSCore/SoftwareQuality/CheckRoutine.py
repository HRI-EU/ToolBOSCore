# -*- coding: utf-8 -*-
#
#  CLI check routine for Software Quality Guideline rules
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


import copy
import logging
import os

from typing import List, Optional, Set

from ToolBOSCore.BuildSystem              import BuildSystemTools
from ToolBOSCore.Packages                 import AppDetector, PackageDetector
from ToolBOSCore.SoftwareQuality          import Rules
from ToolBOSCore.SoftwareQuality.Common   import *
from ToolBOSCore.Util                     import Any, ColoredOutput, FastScript


FastScript.tryImport( 'terminaltables' )

import terminaltables


class CheckRoutine( object ):

    def __init__( self, projectRoot=None, details=None ):
        """
            By default, scans the package within the current working directory.
            Alternatively 'projectRoot' may be specified to point to any
            other top-level directory of a source package.

            If a PackageDetector instance is already at hand it can be
            provided here to speed up the things. In such case its
            retrieveMakefileInfo() and retrieveVCSInfo() must have already
            been called.

            You need to call setup() and run() to use it.

            You may optionally specify list of rule IDs to run,
            and/or a set of files to consider.
            The default is to run all checkers on all files of the package.
        """
        self.details          = None

        self.includeDirs      = set()
        self.includeFiles     = set()
        self.excludeDirs      = { '3rdParty', 'build', 'cmake-build-debug',
                                  'external', 'install', 'klocwork',
                                  'precompiled', 'sources', '.git', '.svn' }
        self.excludeFiles     = set()
        self.includeExts      = { '.c', '.h', '.cpp', '.hpp', '.inc', '.py',
                                  '.java', '.m', '.bash', '.sh', '.ipynb' }
        self.bashExts         = { '.bash', '.sh' }

        self.sqLevelToRun     = None   # level to use for this SQ check run

        self.useOptFlags      = True   # disabled when invoking setRules()

        self.files            = set()  # final list of files to check
        self.filesByType      = {}     # dict with key: file type &
                                       # value: list of files of that type
        self.rules            = {}     # { ID: obj } of all rules (None if n/a)
        self.ruleIDs          = set()  # IDs of all SQ rules, not ordered
        self.rulesOrdered     = []     # IDs of all SQ rules, sorted
        self.rulesImplemented = set()  # IDs of all implemented rules
        self.rulesInLevel     = set()  # IDs of rules required by selected SQ level
        self.rulesRemoved     = set()  # IDs of outdated rules
        self.rulesToRun       = []     # IDs of rules to run this time, sorted

        self.results          = {}     # result data, filled by runParticular()

        self._summaryEnabled  = True   # True/False, show stats after run

        self._populatePackage( projectRoot, details )
        self._populateFiles()
        self._populateRules()


    def excludeDir( self, dirPath ):
        Any.requireIsTextNonEmpty( dirPath )

        # all files in self.files start with relative path "./", in order
        # to filter-out some we need to prepend this in the search pattern
        dirPath = os.path.join( '.', dirPath )

        if os.path.exists( dirPath ):
            logging.debug( 'ignoring content in %s', dirPath )

            origFiles = copy.copy( self.files )

            for filePath in origFiles:
                if filePath.startswith( dirPath ):
                    self.files.remove( filePath )


    def excludeFile( self, filePath ):
        Any.requireIsTextNonEmpty( filePath )

        filePath = os.path.join( '.', filePath )

        try:
            self.files.remove( filePath )
        except KeyError:
            pass


    def excludeRule( self, ruleID ):
        try:
            self.rulesToRun.remove( ruleID )
        except KeyError:
            pass


    def includeDir( self, dirPath ):
        Any.requireIsTextNonEmpty( dirPath )

        # FastScript.getFilesInDirRecursive() returns:
        #    * absolute file paths if absolute dir. path provided
        #    * relative file paths if relative dir. Path provided
        #
        # shorten absolute path names to relative ones for shorter outputs:
        searchPath = os.path.relpath( dirPath )


        for filePath in FastScript.getFilesInDirRecursive( searchPath ):

            # only consider whitelisted extensions, f.i. do not analyze
            # binaries, bytecode files, PDFs etc.
            fileExt = os.path.splitext( filePath )[-1]

            if fileExt in self.includeExts:
                if not os.path.islink( filePath ):
                    self.includeFile( filePath )


    def includeFile( self, filePath ):
        Any.requireIsTextNonEmpty( filePath )

        self.files.add( filePath )


    def includeRule( self, ruleID ):
        Any.requireIsTextNonEmpty( ruleID )
        Any.requireIsIn( ruleID, self.ruleIDs )

        if ruleID not in self.rulesToRun:
            self.rulesToRun.append( ruleID )


    def overallResult( self ):
        overallResult = True

        logging.debug( 'computing overall result:' )

        for ruleID, result in self.results.items():

            status = result[0]
            logging.debug( '%s: %s', ruleID, status )

            if status is FAILED:
                overallResult = False

        logging.debug( 'overall result: %s', overallResult )

        return overallResult


    def run( self ):
        """
            Executes the previously configured checks, no matter if they
            are actually needed in the given quality level or opted-out by
            the maintainer.

            See also
              * setRules()
              * setUseOptFlags()
        """
        for ruleID in self.rulesToRun:

            if ruleID in self.rulesRemoved:
                logging.info( '' )
                logging.info( '%s: Rule has been removed', ruleID )

            elif ruleID in self.rulesImplemented:
                logging.info( '' )
                self._runCheck( ruleID )
            else:
                logging.info( '' )
                logging.info( '%s: Not implemented', ruleID )

        logging.info( '' )

        if self._summaryEnabled:
            self._showSummary()


    def setDirs( self, dirs ):
        """
            Check the given set of directories, regardless other settings.

            Note that filename-extensions apply.
        """
        Any.requireIsSet( dirs )

        self.files = set()

        for path in dirs:
            self.includeDir( path )


    def setFiles( self, files ):
        """
            Check the given set of files, regardless other settings.
        """
        Any.requireIsSet( files )

        self.files = files


    def setLevel( self, levelName ):
        """
            Performs the check using a particular pre-defined quality set.

            This overrides the (optional) setting 'sqLevel' in the
            pkgInfo.py of the package to test.
        """
        Any.requireIsTextNonEmpty( levelName )
        Any.requireIsIn( levelName, sqLevelNames )

        self.sqLevelToRun = levelName


    def setRulesForGroups( self, groups: str ) -> None:
        """
            sets rules to run by checker to only the rules from the specified groups,
            instead of all.
        """
        Any.requireIsTextNonEmpty( groups )

        groupList = groups.split( "," )

        for group in groupList:
            msg = f'{group}: No such group in {sectionKeys}'
            Any.requireIsIn( group, sectionKeys, msg )

        filteredRules = []

        for ruleId in self.rulesToRun:
            if ruleId.startswith( tuple( groupList ) ):
                filteredRules.append( ruleId )

        self.rulesToRun = filteredRules

        logging.info( 'selected rules for %s group: %s', groups, self.rulesToRun )


    def setRules( self, ruleIDs ):
        """
            Run only the given list of rules, instead of all.

            This overrides the (optional) settings 'sqOptIn' and/or
            'sqOptOut' in the pkgInfo.py of the package to test.
        """
        Any.requireIsListNonEmpty( ruleIDs )

        for ruleID in ruleIDs:
            Any.requireIsIn( ruleID, self.ruleIDs )

        self.rulesToRun  = ruleIDs
        self.useOptFlags = False


    def setup( self, useOptOptions = True ):
        """
            if useOptOptions is set, consider the optOut rules in the pkgInfo.py (if any).
            else SQ checks will be performed against all the rules and optOut flags are ignored.

            Note: OptOut/In will always be applied to the files and directories (if any).
        """
        self.useOptFlags = False

        if useOptOptions:
            self.useOptFlags = True
            self._setupSqLevel()
            self._setupOptOut()
        self._setupOptIn()
        self._setupOptInDirs()
        self._setupOptOutDirs()
        self._setupOptOutFiles()
        self._setupOptInFiles()
        self._setupFilesByType()


    def showSummary( self, state ):
        """
            Force showing (or not) a summary at the end of run().
        """
        Any.requireIsBool( state )

        self._summaryEnabled = state


    def _computeSuccessRate( self, ruleID ) -> Optional[int]:
        """
            Computes the success rate (in percent) for a given rule,
            based on the values returned by the corresponding checker.
        """
        Any.requireIsTextNonEmpty( ruleID )

        ( status, passed, failed, shortText ) = self.results[ ruleID ]

        # in case of 'not required' do not display any arbitrary number
        # like 0% or 100% (does not make sense)

        if status in ( OK, FAILED ):
            total = passed + failed

            try:
                result = int( float(passed) / float(total) * 100 )
            except ZeroDivisionError:
                # Division by zero can only happen in case the total number
                # is zero, f.i. the check did not apply to any file.
                # Set percentage to 100% in this case == success.
                result = 100
        else:
            result = None

        # returns Integer or None
        return result


    def _populateFiles( self ):
        """
            Performs an initial scan for files in the given project.

            Later on the user may customize this list using the
            corresponding functions.
        """
        self.includeDir( self.details.topLevelDir )

        for path in self.excludeDirs:
            self.excludeDir( path )


    def _populatePackage( self, projectRoot, details ):
        if details:
            Any.requireIsInstance( details, PackageDetector.PackageDetector )
            self.details = details

        else:
            BuildSystemTools.requireTopLevelDir( projectRoot )

            logging.info( 'analyzing package... (this may take some time)' )
            self.details = PackageDetector.PackageDetector( projectRoot )
            self.details.retrieveMakefileInfo()
            self.details.retrieveVCSInfo()


    def _populateRules( self, forceRules=None ):
        """
            Discovers available / not implemented / opted-in / opted-out
            checkers.

            'forceRules' is supposed to be an ordered list of rule IDs
            to get executed this time. In case of 'None' all rules will
            get checked.
        """
        checkersAvailable = Rules.getRules()
        Any.requireIsListNonEmpty( checkersAvailable )

        for elem in checkersAvailable:
            Any.requireIsTuple( elem )

            ( ruleID, rule ) = elem
            Any.requireIsTextNonEmpty( ruleID )
            Any.requireIsInstance( rule, Rules.AbstractRule )

            self.ruleIDs.add( ruleID )

            self.rules[ ruleID ] = rule

            self.rulesOrdered.append( ruleID )

            if hasattr( rule, 'run' ):
                self.rulesImplemented.add( ruleID )

                # will get overwritten below if 'forceRules' provided
                self.rulesToRun.append( ruleID )

            elif rule.removed:
                self.rulesRemoved.add( ruleID )

            # else: rule not implemented, yet


        if forceRules is not None:
            Any.requireIsListNonEmpty( forceRules )

            for ruleID in forceRules:
                Any.requireIsTextNonEmpty( ruleID )
                Any.requireIsIn( ruleID, self.ruleIDs )

            self.rulesToRun = forceRules


    def _setupFilesByType( self ) -> None:
        """
            populates a dictionary `self.filesByType` with key as file type and
            value as list of files of that type.
            self.filesByType: Dict[ str, List[ str ] ]
        """

        self.filesByType = {}

        self.filesByType[ 'all' ]        = sorted( self.files )
        self.filesByType[ 'bash' ]       = self._populateBashFiles()
        self.filesByType[ 'python' ]     = self._getFileListByExt( self.files, { '.py' } )
        self.filesByType[ 'cpp' ]        = self._getFileListByExt( self.files, { '.cpp' } )
        self.filesByType[ 'cppHeaders' ] = self._getFileListByExt( self.files, { '.h', '.hh',
                                                                                 '.hpp', '.hxx', '.inc' } )
        self.filesByType[ 'c' ]          = self._getFileListByExt( self.files, { '.c' } )
        self.filesByType[ 'cHeaders' ]   = self._getFileListByExt( self.files, { '.h', '.inc' } )


    def _getFileListByExt( self, files: Set[ str ], extensions: Set[ str ] ) -> List[  str ]:
        """
            Returns a fileList by iterating over the 'files' set
            and filtering for the given set of extensions.
        """
        Any.requireIsSet( files )
        Any.requireIsSet( extensions )

        fileList = []

        for filePath in self.files:
            fileExt = os.path.splitext( filePath )[ -1 ]

            if fileExt in extensions:
                fileList.append( filePath )

        return sorted( fileList )


    def _populateBashFiles( self ):
        """
            returns list of bash files by iterating over the 'self.files' list
        """
        bashFiles = []

        for filePath in self.files:
            fileExt = os.path.splitext( filePath )[ -1 ]

            if fileExt in self.bashExts:
                bashFiles.append( filePath )
            else:
                if fileExt == '':
                    content = FastScript.getFileContent( filePath, True )
                    if len(content) > 0 and 'bash' in content[0].lower():
                        bashFiles.append( filePath )

        return bashFiles


    def _printEnabled( self ):
        """
            Print the final list of files and rules, for debugging purposes
            to see what we are going to execute / check.
        """
        logging.debug( '' )

        logging.debug( 'checking files:' )

        for filePath in sorted( self.files ):
            logging.debug( filePath )

        logging.debug( '' )
        logging.debug( 'checking rules:' )
        logging.debug( ' '.join( self.rulesToRun ) )
        logging.debug( '' )


    def _runCheck( self, ruleID ):
        """
            Executes the checker for the specified rule ID, and stores the
            result in self.results[ ruleID ].

            Raises a KeyError upon invalid ID, and AttributeError if not
            implemented.
        """
        Any.requireIsTextNonEmpty( ruleID )

        ruleName = self.rules[ ruleID ].name
        Any.requireIsTextNonEmpty( ruleName )

        logging.info( 'checking rule: %s (%s)', ruleID, ruleName )

        if self.useOptFlags and ruleID in self.details.sqOptOutRules:
            result = ( DISABLED, None, None, 'explicitly opt-out in pkgInfo.py' )

        else:

            if self.useOptFlags and ruleID in self.details.sqOptInRules:
                logging.info( 'explicitly enabled in pkgInfo.py' )

            result = self._runCheck_worker( ruleID )

        status = result[0]
        msg    = '(' + str(result[3]) + ')' if result[3] else ''

        logging.info( 'checking rule: %s → %s %s', ruleID, status, msg )

        try:
            comment = self.details.sqComments[ ruleID ]
            logging.info( 'comment by maintainer: "%s"', comment )
        except KeyError:
            pass

        self.results[ ruleID ] = result


    def _runCheck_worker( self, ruleID ):
        Any.requireIsTextNonEmpty( ruleID )

        rule = self.rules[ ruleID ]

        if ruleID in self.rulesImplemented:
            files = self.filesByType
            result = rule.run( self.details, files )
        else:
            result = ( NOT_IMPLEMENTED, None, None, None )

        Any.requireIsTuple( result )

        return result


    def _setupSqLevel( self ):
        # force run under certain SQ level if provided, otherwise fallback
        # to the pkgInfo.py setting

        if not self.sqLevelToRun:
            self.sqLevelToRun = self.details.sqLevel


        msg = '"%s": No such quality level (allowed: %s)' % \
              ( self.sqLevelToRun, ', '.join( sqLevelNames ) )
        Any.requireMsg( self.sqLevelToRun in sqLevelNames, msg )

        for ruleID, rule in self.rules.items():
            if ruleID not in self.rulesImplemented:
                continue

            rule = self.rules[ ruleID ]

            Any.requireIsInstance( rule, Rules.AbstractRule )
            Any.requireIsInstance( rule.sqLevel, frozenset )

            if self.sqLevelToRun in rule.sqLevel:
                self.rulesInLevel.add( ruleID )

            else:
                # filter-out rules not needed in the level at hand
                # (don't filter-out if we force-run particular rules)
                if self.useOptFlags and ruleID in self.rulesToRun:

                    logging.debug( '%6s: no need to run at level=%s',
                                   ruleID, self.sqLevelToRun )
                    self.rulesToRun.remove( ruleID )


    def _setupOptIn( self ):
        Any.requireIsIterable( self.details.sqOptInRules )

        for ruleID in self.details.sqOptInRules:
            logging.debug( '%6s: enabled (opt-in via pkgInfo.py)', ruleID )
            self.includeRule( ruleID )


    def _setupOptOut( self ):
        Any.requireIsIterable( self.details.sqOptOutRules )

        for ruleID in self.details.sqOptOutRules:
            logging.debug( '%6s: disabled (opt-out via pkgInfo.py)', ruleID )

            # Don't do that! it will hide a rule that is supposed to get
            # executed from the normal progress log + report
            #
            # self.excludeRule( ruleID )


    def _setupOptInDirs( self ):
        Any.requireIsIterable( self.details.sqOptInDirs )

        for dirname in self.details.sqOptInDirs:
            logging.debug( '%6s: explicitly included via pkgInfo.py', dirname )
            self.includeDir( dirname )


    def _setupOptOutDirs( self ):
        Any.requireIsIterable( self.details.sqOptOutDirs )

        for dirname in self.details.sqOptOutDirs:
            logging.debug( '%6s: explicitly excluded via pkgInfo.py', dirname )
            self.excludeDir( dirname )


    def _setupOptInFiles( self ):
        Any.requireIsIterable( self.details.sqOptInFiles )

        for filename in self.details.sqOptInFiles:
            logging.debug( '%6s: explicitly included via pkgInfo.py', filename )
            self.includeFile( filename )


    def _setupOptOutFiles( self ):
        Any.requireIsIterable( self.details.sqOptOutFiles )

        for filename in self.details.sqOptOutFiles:
            logging.debug( '%6s: explicitly excluded via pkgInfo.py', filename )
            self.excludeFile( filename )


    def _showSummary( self ):
        """
            Shows a summary of the execution results.
        """
        self._showSummaryHeadline()
        self._showSummaryTable()
        self._showSummaryComments()


    def _showSummaryHeadline( self ):
        Any.requireIsTextNonEmpty( self.details.canonicalPath )
        Any.requireIsTextNonEmpty( self.details.sqLevel )

        tcRoot    = FastScript.getEnv( 'TOOLBOSCORE_ROOT' )
        tcVersion = AppDetector.getAppVersion( tcRoot )

        print( f'\nPackage:       {self.details.canonicalPath}' )
        print(   f'Quality level: {self.sqLevelToRun}' )
        print(   f'Scan engine:   {tcVersion}\n' )


    def _showSummaryTable( self ):
        Any.requireIsDictNonEmpty( self.results )
        Any.requireIsListNonEmpty( self.rulesOrdered )

        tableData = [ [ 'ID', 'objective', 'val.', 'status', 'comment' ] ]

        for ruleID in self.rulesOrdered:
            if ruleID not in self.rulesImplemented:
                continue

            if ruleID not in self.rulesToRun:
                continue

            result        = self.results[ ruleID ]
            state         = result[0]
            comment       = result[3]
            ruleName      = self.rules[ ruleID ].name
            successRate   = self._computeSuccessRate( ruleID )
            displayedRate = f'{successRate:3d}%' if successRate is not None else ''

            if state is FAILED:
                displayedState = ColoredOutput.error( state )
            elif state is DISABLED:
                displayedState = ColoredOutput.emphasized( state )
            else:
                displayedState = state

            rowData        = [ ruleID, ruleName, displayedRate, displayedState, comment ]
            tableData.append( rowData )

        table = terminaltables.DoubleTable( tableData ).table
        print( table, '\n' )


    def _showSummaryComments( self ):
        if self.details.sqComments:
            logging.info( 'comments by maintainer:' )
            logging.info( '' )

            for ruleID in self.rulesOrdered:
                if ruleID in self.details.sqComments:
                    comment = self.details.sqComments[ ruleID ]

                    logging.info( '%8s: "%s"', ruleID, comment )
                    logging.info( '' )


    def hasRule( self, ruleType ):
        for rule in self.rulesToRun:
            if ruleType in rule:
                return True
        return False


# EOF
