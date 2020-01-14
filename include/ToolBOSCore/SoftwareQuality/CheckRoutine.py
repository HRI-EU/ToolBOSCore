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


import logging
import os

from ToolBOSCore.BuildSystem              import BuildSystemTools
from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.SoftwareQuality          import Rules
from ToolBOSCore.SoftwareQuality.Common   import *
from ToolBOSCore.Util                     import Any, FastScript


class CheckRoutine( object ):

    def __init__( self, projectRoot=None, details=None ):
        """
            By default scans the package within the current working directory.
            Alternatively 'projectRoot' may be specified to point to any
            other top-level directory of a source package.

            If a PackageDetector instance is already at hand it can be
            provided here to speed-up the things. In such case its
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

        self.excludeDirs      = { 'build', 'external', 'klocwork',
                                  'precompiled', 'sources', '.git', '.svn' }
        self.excludeFiles     = set()

        self.includeExts      = { '.c', '.h', '.cpp', '.hpp', '.inc', '.py',
                                  '.java', '.m' }

        self.useOptFlags      = True

        self.files            = set()  # final list of files to check

        self.rules            = {}     # { ID: obj } of all rules (None if n/a)
        self.ruleIDs          = set()  # IDs of all SQ rules, not ordered
        self.rulesOrdered     = []     # IDs of all SQ rules, sorted
        self.rulesImplemented = set()  # IDs of all implemented rules
        self.rulesInLevel     = set()
        self.rulesToRun       = []     # IDs of rules to run this time, sorted

        self.results          = {}     # result data, filled by runParticular()

        self._populatePackage( projectRoot, details )
        self._populateFiles()
        self._populateRules()

        self._applySqSettings()


    def excludeDir( self, dirPath ):
        raise NotImplemented()


    def excludeFile( self, filePath ):
        absPath = os.path.join( self.details.topLevelDir, filePath )

        try:
            self.files.remove( absPath )
        except KeyError:
            pass


    def excludeRule( self, ruleID ):
        try:
            self.rulesToRun.remove( ruleID )
        except KeyError:
            pass


    def includeDir( self, dirPath ):
        Any.requireIsTextNonEmpty( dirPath )

        for filePath in FastScript.getFilesInDirRecursive( dirPath ):

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
        for result in self.results:

            if result[0] is FAILED:
                return False

        return True


    def run( self ):
        """
            Executes the previously configured checks, no matter if they
            are actually needed in the given quality level or opted-out by
            the maintainer.

            See also
              * setRulesToRun()
              * setUseOptFlags()
        """
        for ruleID in self.rulesToRun:

            if ruleID in self.rulesImplemented:
                logging.info( '' )
                self._runCheck( ruleID )
            else:
                logging.info( '' )
                logging.info( '%s: Not implemented', ruleID )

        logging.info( '' )


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


    def setRulesToRun( self, ruleIDs ):
        """
            Run only the given list of rules, instead of all.
        """
        Any.requireIsListNonEmpty( ruleIDs )

        for ruleID in ruleIDs:
            Any.requireIsIn( ruleID, self.ruleIDs )

        self.rulesToRun = ruleIDs


    def setUseOptFlags( self, state ):
        """
            Consider opt-in/out flags (optionally) provided by the
            maintainer in the pkgInfo.py?

            True:   inform about opt-in rules, skip opt-out rules
            False:  run checks anyway
        """
        Any.requireIsBool( state )

        self.useOptFlags = state


    def showReport( self ):
        """
            Shows a summary of the execution results.
        """
        self._showReportHeadline()
        self._showReportTable()
        self._showReportComments()


    def _applySqSettings( self ):
        """
            Considers the opt-in/out files/rules in the pkgInfo.py (if any).
        """
        self._applySqSettingsLevel()
        self._applySqSettingsOptIn()
        self._applySqSettingsOptOut()


    def _applySqSettingsLevel( self ):
        msg = '"%s": No such quality level (allowed: %s)' % \
              ( self.details.sqLevel, ', '.join( sqLevelNames ) )
        Any.requireMsg( self.details.sqLevel in sqLevelNames, msg )


        for ruleID, rule in self.rules.items():
            if ruleID not in self.rulesImplemented:
                continue

            rule = self.rules[ ruleID ]

            Any.requireIsInstance( rule, Rules.AbstractQualityRule )
            Any.requireIsInstance( rule.sqLevel, frozenset )

            if self.details.sqLevel in rule.sqLevel:
                self.rulesInLevel.add( ruleID )

            else:
                # filter-out rules not needed in the level at hand
                # (don't filter-out if we force-run particular rules)
                if self.useOptFlags:

                    logging.debug( '%6s: no need to run at level=%s',
                                   ruleID, self.details.sqLevel )
                    self.rulesToRun.remove( ruleID )


    def _applySqSettingsOptIn( self ):
        Any.requireIsIterable( self.details.sqOptInRules )

        for ruleID in self.details.sqOptInRules:
            logging.debug( '%6s: enabled (opt-in via pkgInfo.py)', ruleID )
            self.includeRule( ruleID )


    def _applySqSettingsOptOut( self ):
        Any.requireIsIterable( self.details.sqOptOutRules )

        for ruleID in self.details.sqOptOutRules:
            logging.debug( '%6s: disabled (opt-out via pkgInfo.py)', ruleID )

            # Don't do that! it will hide a rule that is supposed to get
            # executed from the normal progress log + report
            #
            # self.excludeRule( ruleID )


    def _computeSuccessRate( self, ruleID ):
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
                percent = float(passed) / float(total) * 100
            except ZeroDivisionError:
                # Devision by zero can only happen in case the total number
                # is zero, f.i. the check did not apply to any file.
                # Set percentage to 100% in this case == success.
                percent = 100

            return '%3d%%' % percent

        else:

            return ''


    def _populateFiles( self ):
        """
            Performs an initial scan for files in the given project.

            Later on the user may customize this list using the
            corresponding functions.
        """
        self.includeDir( self.details.topLevelDir )


    def _populatePackage( self, projectRoot, details ):
        if details:
            Any.requireIsInstance( details, PackageDetector )
            self.details = details

        else:
            BuildSystemTools.requireTopLevelDir( projectRoot )

            logging.info( 'analyzing package... (this may take some time)' )
            self.details = PackageDetector( projectRoot )
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
            Any.requireIsInstance( rule, Rules.AbstractQualityRule )

            self.ruleIDs.add( ruleID )

            self.rules[ ruleID ] = rule

            self.rulesOrdered.append( ruleID )

            if hasattr( rule, 'run' ):
                self.rulesImplemented.add( ruleID )

                # will get overwritten below if 'forceRules' provided
                self.rulesToRun.append( ruleID )


        if forceRules is not None:
            Any.requireIsListNonEmpty( forceRules )

            for ruleID in forceRules:
                Any.requireIsTextNonEmpty( ruleID )
                Any.requireIsIn( ruleID, self.ruleIDs )

            self.rulesToRun = forceRules


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

        logging.info( 'checking rule: %s', ruleID )

        if self.useOptFlags and ruleID in self.details.sqOptOutRules:
            result = ( DISABLED, None, None, 'explicitly opt-out in pkgInfo.py' )

        else:

            if self.useOptFlags and ruleID in self.details.sqOptInRules:
                logging.info( 'explicitly enabled in pkgInfo.py' )

            result = self._runCheck_worker( ruleID )

        status = result[0]
        msg    = '(' + result[3] + ')' if result[3] else ''

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
            result = rule.run( self.details, self.files )
        else:
            result = ( NOT_IMPLEMENTED, None, None, None )

        Any.requireIsTuple( result )

        return result


    def _showReportHeadline( self ):
        Any.requireIsTextNonEmpty( self.details.canonicalPath )
        Any.requireIsTextNonEmpty( self.details.sqLevel )

        logging.info( '' )
        logging.info( 'results for %s (level=%s):',
                      self.details.canonicalPath, self.details.sqLevel )
        logging.info( '' )


    def _showReportTable( self ):
        Any.requireIsDictNonEmpty( self.results )
        Any.requireIsListNonEmpty( self.rulesOrdered )

        for ruleID in self.rulesOrdered:
            if ruleID not in self.rulesImplemented:
                continue

            if ruleID not in self.rulesInLevel:
                continue

            ( status, passed, failed, shortText ) = self.results[ ruleID ]

            displayStatus = status if status in ( OK, FAILED, DISABLED ) else ''
            successRate   = self._computeSuccessRate( ruleID )

            logging.info( '%8s | %6s | %4s | %s', ruleID,
                          displayStatus.ljust(8), successRate, shortText )

        logging.info( '' )


    def _showReportComments( self ):
        if self.details.sqComments:
            logging.info( 'comments by maintainer:' )
            logging.info( '' )

            for ruleID in self.rulesOrdered:
                if ruleID in self.details.sqComments:
                    comment = self.details.sqComments[ ruleID ]

                    logging.info( '%8s: "%s"', ruleID, comment )
                    logging.info( '' )


# EOF
