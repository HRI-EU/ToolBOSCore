#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  GUI for Quality Checker
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


import functools
import io
import logging
import re

import sip

sip.setapi( 'QString', 2 )
sip.setapi( 'QVariant', 2 )

import markdown

from PyQt5.QtCore    import Qt, QEvent, QThread
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from ToolBOSCore.GenericGUI      import IconProvider
from ToolBOSCore.SoftwareQuality import CheckRoutine, Common, Rules
from ToolBOSCore.Util            import Any
from ToolBOSCore.ZenBuildMode    import QtPackageModel


def run( model ):
    Any.requireIsInstance( model, QtPackageModel.BSTPackageModel )

    app = QApplication( [] )

    window = CheckRoutineDialog( model )
    window.show()

    return app.exec_()


class CheckRoutineDialog( QDialog, object ):

    def __init__( self, model, parent=None ):
        super( CheckRoutineDialog, self ).__init__( parent )

        self.installEventFilter( self )

        self._model             = model
        self._logOutput         = io.StringIO()
        self._allRules          = Rules.getRules()
        self._allRulesDict      = {}
        self._checkSelected     = False
        self._checkBoxes        = {}
        self._checkButtons      = {}
        self._commentFields     = {}
        self._dirty             = None
        self._safeplace         = set()      # avoid garbage-collection
        self._threads           = {}
        self._textWidgets       = {}
        self._textStates        = {}
        self._resultWidgets     = {}
        self._rowNumbers        = {}
        self._desiredLevelName  = None
        self._desiredLevelIndex = None
        self._desiredLevelLabel = QLabel( 'desired level:' )
        self._desiredLevelCombo = QComboBox()
        self._windowTitle       = 'Software Quality settings'

        Any.addStreamLogger( self._logOutput, logging.DEBUG, preamble=False )

        for level in CheckRoutine.sqLevelNames:
            text  = CheckRoutine.sqLevels[ level ]
            self._desiredLevelCombo.addItem( text, level )

        self._defaultLevel = CheckRoutine.sqLevelDefault
        self._defaultIndex = CheckRoutine.sqLevelNames.index( self._defaultLevel )
        self._desiredLevelCombo.setCurrentIndex( self._model.getSQLevelIndex() )

        # do this only once after all entries have been added, otherwise each
        # add would already (unnecessarily) trigger the slot
        self._desiredLevelCombo.currentIndexChanged.connect( self._toggleCombo )

        self._desiredLevelLayout = QHBoxLayout()
        self._desiredLevelLayout.addWidget( self._desiredLevelLabel )
        self._desiredLevelLayout.addWidget( self._desiredLevelCombo )
        self._desiredLevelLayout.addStretch( 1 )

        self._desiredLevelWidget = QWidget()
        self._desiredLevelWidget.setLayout( self._desiredLevelLayout )


        columns = ( 'rule', 'description', 'required', 'verify', 'result', 'comments' )
        self._table = QTableWidget()
        self._table.setRowCount( len( self._allRules ) +
                                 len( CheckRoutine.sectionKeys ) )
        self._table.setColumnCount( len(columns) )
        self._table.setHorizontalHeaderLabels( columns )
        self._table.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        self._table.setAutoScroll( False )

        self._cellHeightNormal   =  60
        self._cellHeightExpanded = 200

        self._hHeader = self._table.horizontalHeader()
        self._hHeader.setSectionResizeMode( 1, QHeaderView.Stretch )
        self._hHeader.setSectionResizeMode( 4, QHeaderView.Stretch )
        self._hHeader.setSectionResizeMode( 5, QHeaderView.Stretch )
        self._hHeader.setSectionsClickable( False )

        self._vHeader = self._table.verticalHeader()
        self._vHeader.setDefaultSectionSize( self._cellHeightNormal )
        self._vHeader.hide()

        i       = 0
        expr    = re.compile( r"^([A-Z]+)\d+$" )
        prevKey = None

        for ( ruleID, rule ) in self._allRules:

            # whenever the rule key (e.g. "C", "GEN", "SPEC",...) changes then
            # insert a table row with title and objective

            key = expr.match( ruleID ).group( 1 )
            Any.requireIsTextNonEmpty( key )

            if key != prevKey:
                prevKey = key

                sectionName = CheckRoutine.sectionNames[ key ]
                Any.requireIsTextNonEmpty( sectionName )

                sectionObjective = CheckRoutine.sectionObjectives[ key ]
                Any.requireIsTextNonEmpty( sectionObjective )

                text = '<h2>%s</h2><i>Objective: %s</i>' % ( sectionName,
                                                             sectionObjective )
                cellWidget = QTextEdit( text )
                cellWidget.setReadOnly( True )
                cellWidget.setFrameStyle( QFrame.NoFrame )
                self._table.setCellWidget( i, 0, cellWidget )
                self._table.setSpan( i, 0, 1, len(columns) )

                i += 1


            # keep references to rules and numbers
            self._allRulesDict[ ruleID ] = rule
            self._rowNumbers[ ruleID ] = i

            # column 0: rule IDs
            cellWidget = QTextEdit( ruleID )
            cellWidget.setReadOnly( True )
            cellWidget.setFrameStyle( QFrame.NoFrame )
            self._table.setCellWidget( i, 0, cellWidget )


            # column 1: rule description
            text = rule.brief

            if rule.description:
                text += ' [More...](expand-%s.html)' % ruleID

            cellWidget = QTextBrowser()
            cellWidget.setHtml( markdown.markdown( text ) )
            cellWidget.setReadOnly( True )
            cellWidget.setOpenLinks( False )
            cellWidget.setOpenExternalLinks( False )
            cellWidget.setFrameStyle( QFrame.NoFrame )
            cellWidget.anchorClicked.connect( self._toggleDescription )

            self._table.setCellWidget( i, 1, cellWidget )
            self._textWidgets[ ruleID ] = cellWidget
            self._textStates[ ruleID ] = False       # False/True = short/long


            # column 2: pre-selection for desired SQ level
            cellWidget = QWidget()
            checkbox   = QCheckBox()
            checkbox.setChecked( False )
            checkbox.stateChanged.connect( self._toggleCheckbox )
            checkbox.stateChanged.connect( self._setDirtyFlag )

            cellLayout = QHBoxLayout()
            cellLayout.setAlignment( Qt.AlignCenter )
            cellLayout.addWidget( checkbox )
            cellWidget.setLayout( cellLayout )

            self._table.setCellWidget( i, 2, cellWidget )

            if rule.removed:
                checkbox.setEnabled( False )
                self._safeplace.add( checkbox )
            else:
                self._checkBoxes[ ruleID ] = checkbox


            # column 3: check buttons
            button = QPushButton( 'Check' )
            button.clicked.connect( functools.partial( self._run, rule ) )

            cellLayout = QHBoxLayout()
            cellLayout.addWidget( button )

            cellWidget = QWidget()
            cellWidget.setLayout( cellLayout )
            self._table.setCellWidget( i, 3, cellWidget )

            if rule.removed:
                button.setEnabled( False )
                self._safeplace.add( button )
            else:
                self._checkButtons[ ruleID ] = button


            # column 4: checker output / result
            cellWidget = QTextEdit()
            cellWidget.setReadOnly( True )
            cellWidget.setFrameStyle( QFrame.NoFrame )
            self._table.setCellWidget( i, 4, cellWidget )
            self._resultWidgets[ ruleID ] = cellWidget


            # column 5: comments field
            cellWidget = QTextEdit()
            cellWidget.setFrameStyle( QFrame.NoFrame )
            cellWidget.textChanged.connect( self._setDirtyFlag )
            self._table.setCellWidget( i, 5, cellWidget )
            self._commentFields[ ruleID ] = cellWidget

            i += 1


        self._runSelectedButton = QPushButton( 'Check &selected' )
        self._runSelectedButton.setEnabled( False )   # toggle via checkboxes
        self._runSelectedButton.setToolTip( 'verify all rules where checkbox is selected' )
        self._runSelectedButton.pressed.connect( self._runSelected )

        self._restoreButton = QPushButton( '&Restore defaults' )
        self._restoreButton.setToolTip( 'Set to default values' )
        self._restoreButton.pressed.connect( self._restoreSettings )

        self._saveButton = QPushButton( '&Save selection and comments' )
        self._saveButton.setToolTip( 'Save settings to pkgInfo.py file' )
        self._saveButton.pressed.connect( self._saveSettings )

        self._okButton = QPushButton( '&OK' )
        self._okButton.pressed.connect( self.close )

        self._mainButtonsLayout = QHBoxLayout()
        self._mainButtonsLayout.setAlignment( Qt.AlignRight )
        self._mainButtonsLayout.addWidget( self._runSelectedButton )
        self._mainButtonsLayout.addWidget( self._restoreButton )
        self._mainButtonsLayout.addWidget( self._saveButton )
        self._mainButtonsLayout.addWidget( self._okButton )

        self._mainButtonsWidget = QWidget()
        self._mainButtonsWidget.setLayout( self._mainButtonsLayout )

        self._groupBoxLayout = QVBoxLayout()
        self._groupBoxLayout.addWidget( self._desiredLevelWidget )
        self._groupBoxLayout.addWidget( self._table )

        self._groupBoxWidget = QGroupBox( self._windowTitle )
        self._groupBoxWidget.setLayout( self._groupBoxLayout )

        self._layout = QVBoxLayout()
        self._layout.addWidget( self._groupBoxWidget )
        self._layout.addWidget( self._mainButtonsWidget )

        # noinspection PyArgumentList
        screen       = QApplication.desktop().screenGeometry()

        dialogWidth  = screen.width() / 4 * 3
        dialogHeight = screen.height() / 4 * 3

        self.setLayout( self._layout )
        self.setWindowIcon( IconProvider.getIcon( 'QualityGuideline' ) )
        self.setWindowTitle( self._windowTitle )
        self.resize( dialogWidth, dialogHeight )
        self.move( screen.center() - self.rect().center() )  # center


        # pre-initialize check-state of all checkboxes depending on combobox,
        # this must be done after all checkboxes, combobox, and also the
        # "check selected" button are created
        self._toggleCombo()

        for ruleID in self._model.getSQOptInRules():
            self._checkBoxes[ ruleID ].setChecked( True )

        for ruleID in self._model.getSQOptOutRules():
            self._checkBoxes[ ruleID ].setChecked( False )

        for ruleID, comment in self._model.getSQComments().items():
            self._commentFields[ ruleID ].setText( comment )


        self._okButton.setDefault( True )

        self._dirty = False

        self.show()


    def close( self ):
        doClose = True

        if self._dirty:
            mbox = QMessageBox()
            mbox.setText( 'The Software Quality settings have been modified.' )
            mbox.setInformativeText( 'Do you want to save your changes?' )
            mbox.setStandardButtons( QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel )
            mbox.setDefaultButton( QMessageBox.Save )

            choice = mbox.exec_()

            if choice == QMessageBox.Save:
                self._saveSettings()
            elif choice == QMessageBox.Discard:
                pass
            elif choice == QMessageBox.Cancel:
                doClose = False
            else:
                raise RuntimeError( 'script error' )

        if doClose:
            super( QDialog, self ).close()


    def eventFilter( self, obj, event ):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.close()

        return False


    def _composeSummaryText( self, success, message, ruleID ):
        """
            Assembles the summary text from the checker result string and,
            in case success=False, the individual outputs.
        """
        if success:
            result     = message
        else:
            fullLog    = self._logOutput.getvalue()
            filterFunc = lambda s: s.startswith( ruleID )
            lines      = filter( filterFunc, fullLog.splitlines() )
            stripFunc  = lambda s: s.replace( '%s: ' % ruleID, '' )
            lines      = map( stripFunc, lines )
            ruleLog    = '\n'.join( lines )
            result     = "%s\n\n%s" % ( message, ruleLog )

        return result


    def _onCheckerThreadFinished( self, rule ):
        ruleID = rule.getRuleID()

        # reporting
        thread = self._threads[ ruleID ]
        result = thread.result

        if result is None:                       # checker not implemented
            status  = CheckRoutine.NOT_IMPLEMENTED
            message = 'not implemented'
        else:
            status       = result[0]
            message      = result[3]

        widget = self._resultWidgets[ ruleID ]
        widget.setText( self._composeSummaryText( status == CheckRoutine.OK,
                                                  message, ruleID ) )

        if status == CheckRoutine.OK:
            color = QColor( 220, 255, 220 )                         # green
        elif status == CheckRoutine.FAILED:
            color = QColor( 255, 120, 120 )                         # red
        else:
            color = QColor( 240, 240, 240 )                         # grey

        palette = QPalette()
        palette.setColor( QPalette.Base, color )
        widget.setPalette( palette )

        # ensure thread has stopped
        thread.wait()
        del thread
        self._threads[ ruleID ] = None

        logging.debug( 'finished check for rule %s', ruleID )

        # restore button text
        self._checkButtons[ ruleID ].setText( 'Check' )


        # once the last thread terminated

        if not any ( self._threads.values() ):
            # no more threads in list
            self._checkSelected = False
            logging.debug( 'no more worker threads' )

            # enable all checkboxes + individual "Check"-buttons
            for checkbox in self._checkBoxes.values():
                checkbox.setEnabled( True )

            for button in self._checkButtons.values():
                button.setEnabled( True )

            # have a look if we need to enable the "Check selected" button
            self._toggleCheckbox()


    def _preselectCheckboxes( self, sqLevel ):
        """
            Determines for each checkbox if the associated rule belongs to
            the desired SQ level, and set the checkbox state accordingly.
        """
        for ruleID, rule in self._allRulesDict.items():
            try:
                checkbox = self._checkBoxes[ ruleID ]
            except KeyError:
                # checkbox is read-only (kept in safeplace to not get
                # garbage-collected) and is not intended to be set
                continue

            if rule.sqLevel is None:
                checkbox.setChecked( False )                    # optional rule

            elif rule.removed:
                checkbox.setChecked( False )                    # removed rule

            else:
                checkbox.setChecked( sqLevel in rule.sqLevel )  # regular rule


    def _restoreSettings( self ):
        logging.info( 'restoring defaults' )

        self._desiredLevelCombo.setCurrentIndex( self._defaultIndex )
        self._preselectCheckboxes( self._defaultLevel )


    def _run( self, rule ):
        ruleID = rule.getRuleID()
        logging.debug( 'starting check for rule %s', ruleID )

        # disable "Check" button and change its text to "Running"
        button = self._checkButtons[ ruleID ]
        button.setEnabled( False )
        button.setText( 'Running' )

        # disable "Check selected" button to not collide
        self._runSelectedButton.setEnabled( False )

        # set yellow background color during execution
        palette = QPalette()
        palette.setColor( QPalette.Base, QColor( 255, 248, 220 ) )  # yellow

        # reset result-widget content
        widget = self._resultWidgets[ ruleID ]
        widget.setPalette( palette )
        widget.setText( 'please wait...' )

        # execute in separate thread
        t = self._CheckRunner( self._model, rule )
        self._threads[ ruleID ] = t
        t.finished.connect( functools.partial( self._onCheckerThreadFinished, rule ) )
        t.start()


    def _runSelected( self ):

        self._checkSelected = True

        # disable all checkboxes + individual "Check"-buttons
        for checkbox in self._checkBoxes.values():
            checkbox.setEnabled( False )

        for button in self._checkButtons.values():
            button.setEnabled( False )

        # run all selected checks
        for ruleID, checkbox in self._checkBoxes.items():
            if checkbox.isChecked():
                self._run( self._allRulesDict[ ruleID ] )


    def _saveSettings( self ):
        logging.info( 'saving settings' )

        index = self._desiredLevelCombo.currentIndex()
        Any.requireIsInt( index )
        self._desiredLevelIndex = index

        name = CheckRoutine.sqLevelNames[ index ]
        Any.requireIsTextNonEmpty( name )
        self._desiredLevelName = name

        self._saveSettings_level()
        self._saveSettings_optInOut()
        self._saveSettings_comments()

        self._dirty = False
        self.setWindowTitle( self._windowTitle )


    def _saveSettings_level( self ):
        self._model.setSQLevel( self._desiredLevelName )


    def _saveSettings_optInOut( self ):
        optIn  = []
        optOut = []

        for ruleID, rule in self._allRules:
            if rule.sqLevel is None:
                continue

            checkbox = self._checkBoxes[ ruleID ]

            if self._desiredLevelName in rule.sqLevel:
                # rule belongs to desired level, but was opt-out
                if not checkbox.isChecked():
                    optOut.append( ruleID )

            else:
                # rule does not belong to desired level, but was opt-in
                if checkbox.isChecked():
                    optIn.append( ruleID )


        self._model.setSQOptInRules( optIn )
        self._model.setSQOptOutRules( optOut )


    def _saveSettings_comments( self ):
        comments = {}

        for ruleID, commentField in self._commentFields.items():
            comment = str( commentField.toPlainText() ).strip()

            if comment:
                comments[ ruleID ] = comment

        self._model.setSQComments( comments )


    def _setDirtyFlag( self ):
        if self._dirty is False:
            logging.debug( 'SQ settings modified' )

            self._dirty = True
            self.setWindowTitle( '%s [modified]' % self._windowTitle )


    def _toggleCheckbox( self ):
        enabled = False

        for checkbox in self._checkBoxes.values():
            if checkbox.isChecked():
                enabled = True

        self._runSelectedButton.setEnabled( enabled )


    def _toggleCombo( self ):
        index = self._desiredLevelCombo.currentIndex()
        Any.requireIsInt( index )

        text = self._desiredLevelCombo.currentText()
        Any.requireIsTextNonEmpty( text )

        sqLevel = CheckRoutine.sqLevelNames[ index ]
        Any.requireIsTextNonEmpty( sqLevel )

        logging.debug( 'changed desired level to level=%s ("%s")',
                       sqLevel, text )

        self._preselectCheckboxes( sqLevel )


    def _toggleDescription( self, url ):
        fileName = str(url)

        # extract ruleID from URL/filename
        try:
            ruleID = re.search( '^.+-(.+)\.html', fileName ).group(1)
        except AttributeError:                 # no match, e.g. external link
            return

        Any.requireIsTextNonEmpty( ruleID )

        logging.debug( 'toggling description for rule=%s', ruleID )

        rule = self._allRulesDict[ ruleID ]

        # compute new text
        if self._textStates[ ruleID ] == 0:     # was "short" until now
            text = rule.brief

            if rule.description:
                text += '\n\n' + rule.description

            if rule.goodExample:
                text += '\n\n**good example:**\n\n' + rule.goodExample

            if rule.badExample:
                text += '\n\n**bad example:**\n\n' + rule.badExample

            text += '\n\n[Less](collapse-%s.html)' % ruleID

            html = markdown.markdown( text )

            self._textStates[ ruleID ] = True

            newHeight = self._cellHeightExpanded

        else:                                   # was "long" until now
            text = rule.brief + ' [More...](expand-%s.html)\n' % ruleID
            html = markdown.markdown( text )

            self._textStates[ ruleID ] = False

            newHeight = self._cellHeightNormal


        # update textfield
        self._textWidgets[ ruleID ].setText( html )

        # update cell height (actually the entire row)
        i = self._rowNumbers[ ruleID ]
        self._vHeader.resizeSection( i, newHeight )


    class _CheckRunner( QThread, object ):

        __block = None


        def __init__( self, model, rule ):
            QThread.__init__( self )

            self.result = None

            self._model = model
            self._rule  = rule


        def run( self ):
            logging.debug( 'executing rule checker' )
            if hasattr( self._rule, 'run' ):
                try:
                    self.result = self._model.runSQCheck( self._rule )
                    logging.debug( 'rule checker finished' )
                except ( AssertionError, EnvironmentError, OSError ) as e:
                    self.result = ( Common.FAILED, 0, 0, e )
                    logging.error( 'rule checker failed: %s', e )


# EOF
