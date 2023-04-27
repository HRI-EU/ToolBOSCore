#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Qt-style mode for BST packages
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


import base64
import io
import logging
import os

import dill

from PyQt5.QtCore import pyqtSignal, QByteArray, QObject, QThread

from ToolBOSCore.CIA.PatchSystem import PatchSystem
from ToolBOSCore.GenericGUI      import ProcessExecutor, UnicodeSupport
from ToolBOSCore.Packages        import BSTPackage
from ToolBOSCore.SoftwareQuality import CheckRoutine
from ToolBOSCore.Util            import Any, FastScript


class BSTPackageModel( QObject, object ):
    """
        Qt-style data model to operate with BSTPackages.
    """
    opened           = pyqtSignal()
    closed           = pyqtSignal()
    newName          = pyqtSignal( str )
    newVersion       = pyqtSignal( str )
    newCategory      = pyqtSignal( str )
    newRevision      = pyqtSignal( str )
    depsDetected     = pyqtSignal( bool )
    sqCheckPrepared  = pyqtSignal()
    updatesAvailable = pyqtSignal()


    def __init__( self ):
        super( BSTPackageModel, self ).__init__()

        self._bstpkg_src          = BSTPackage.BSTSourcePackage()
        self._bstpkg_global       = BSTPackage.BSTGloballyInstalledPackage()
        self._depDetector         = None
        self._depDetectorData     = None
        self._globallyInstalled   = None
        self._sqPreparer          = None
        self._sqPreparationDone   = False
        self._topLevelDir         = None
        self._installStatus       = {}
        self._installStatusLocal  = {}
        self._installStatusProxy  = {}
        self._installStatusGlobal = {}


    def open( self, topLevelDir ):
        Any.requireIsDir( topLevelDir )

        self._sqPreparationDone = False

        self._open_main()
        self._open_details()


    def close( self ):
        # noinspection PyUnresolvedReferences
        self.close.emit()


    def getCanonicalPath( self ):
        return self._bstpkg_src.detector.canonicalPath


    def getDepInstallCmd_APT( self ):
        return self._bstpkg_src.getDepInstallCmd_APT()


    def getName( self ):
        return self._bstpkg_src.detector.packageName


    def getVersion( self ):
        return self._bstpkg_src.detector.packageVersion


    def getCategory( self ):
        return self._bstpkg_src.detector.packageCategory


    def getRevision( self ):
        svnRev = self._bstpkg_src.detector.svnRevision
        gitID  = self._bstpkg_src.detector.gitCommitIdShort

        if svnRev is not None and svnRev > 0:
            return str(svnRev)
        elif gitID:
            return gitID
        else:
            return None


    def getDependencySet( self ):
        if self._bstpkg_src.depSet is None:
            return None
        else:
            return self._bstpkg_src


    def getDependencyTree( self ):
        if self._bstpkg_src.depTree is None:
            return None
        else:
            return self._bstpkg_src


    def getReverseDependencySet( self ):
        if self._bstpkg_global.revDepSet is None:
            return None
        else:
            return self._bstpkg_global


    def getReverseDependencyTree( self ):
        if self._bstpkg_global.revDepTree is None:
            return None
        else:
            return self._bstpkg_global


    def getSQLevelIndex( self ):
        name  = self.getSQLevelName()
        Any.requireIsTextNonEmpty( name )

        index = CheckRoutine.sqLevelNames.index( name )
        Any.requireIsInt( index )

        return index


    def getSQLevelName( self ):
        name = self._bstpkg_src.detector.sqLevel

        if name:
            return name
        else:
            return CheckRoutine.sqLevelDefault


    def getSQOptInRules( self ):
        return self._bstpkg_src.detector.sqOptInRules


    def getSQOptOutRules( self ):
        return self._bstpkg_src.detector.sqOptOutRules


    def getSQComments( self ):
        return self._bstpkg_src.detector.sqComments


    def getCheckRoutine( self ):
        return self._bstpkg_src.sqChecker


    def isInstalled( self, packageURL ):
        try:
            result = self._installStatus[ packageURL ]
        except KeyError:
            logging.warning( 'No information about installation of %s', packageURL )
            result = False

        return result


    def isInstalled_locally( self, packageURL ):
        try:
            result = self._installStatusLocal[ packageURL ]
        except KeyError:
            logging.warning( 'No information about local installation of %s', packageURL )
            result = False

        return result


    def isInstalled_proxySIT( self, packageURL ):
        try:
            result = self._installStatusProxy[ packageURL ]
        except KeyError:
            logging.warning( 'No information about proxy-installation of %s', packageURL )
            result = False

        return result


    def isInstalled_globalSIT( self, packageURL ):
        try:
            result = self._installStatusProxy[ packageURL ]
        except KeyError:
            logging.warning( 'No information about global-installation of %s', packageURL )
            result = False

        return result


    def isQualityCheckPreparationFinished( self ):
        return self._sqPreparationDone


    def runSQCheck( self, rule ):
        self._bstpkg_src.sqChecker.setup()
        return rule.run( self._bstpkg_src.detector, self._bstpkg_src.sqChecker.filesByType )


    def setSQLevel( self, level ):
        Any.requireIsTextNonEmpty( level )

        if level == CheckRoutine.sqLevelDefault:
            self._bstpkg_src.pkgInfo_remove('sqLevel')
        else:
            self._bstpkg_src.pkgInfo_set('sqLevel', level)


    def setSQOptInRules( self, value ):
        Any.requireIsList( value )

        if value:
            self._bstpkg_src.pkgInfo_set('sqOptInRules', value)
        else:
            self._bstpkg_src.pkgInfo_remove('sqOptInRules')


    def setSQOptOutRules( self, value ):
        Any.requireIsList( value )

        if value:
            self._bstpkg_src.pkgInfo_set('sqOptOutRules', value)
        else:
            self._bstpkg_src.pkgInfo_remove('sqOptOutRules')


    def setSQComments( self, value ):
        Any.requireIsDict( value )

        if value:
            self._bstpkg_src.pkgInfo_set('sqComments', value)
        else:
            self._bstpkg_src.pkgInfo_remove('sqComments')


    def _open_main( self ):
        self._bstpkg_src.open( self._topLevelDir )
        self._bstpkg_src.detector.retrieveMakefileInfo()

        canonicalPath = self.getCanonicalPath()
        Any.requireIsTextNonEmpty( canonicalPath )

        bstpkg_proxy = BSTPackage.BSTProxyInstalledPackage()

        try:
            bstpkg_proxy.open( canonicalPath )
            self._installStatusProxy[ canonicalPath ] = True

        except ( AssertionError, OSError ):
            logging.debug( '%s: not installed in proxy SIT', canonicalPath )
            bstpkg_proxy.url = 'sit://' + canonicalPath
            self._installStatusProxy[ canonicalPath ] = False

        try:
            self._bstpkg_global.open( canonicalPath )
            self._installStatusGlobal[ canonicalPath ] = True

        except ( AssertionError, OSError ):
            logging.debug( '%s: not installed in global SIT', canonicalPath )
            self._bstpkg_global.url = 'sit://' + canonicalPath
            self._installStatusGlobal[ canonicalPath ] = False

        self.opened.emit()
        self.newName.emit( self.getName() )
        self.newVersion.emit( self.getVersion() )
        self.newCategory.emit( self.getCategory() )

        revision = self.getRevision()
        if revision:
            self.newRevision.emit( revision )


    def _open_details( self ):
        logging.debug( 'dependency detection started' )

        exe = os.path.join( FastScript.getEnv( 'TOOLBOSCORE_ROOT' ),
                            'include/ZenBuildMode/DependencyDetector.py' )
        Any.requireIsFileNonEmpty( exe )

        cmd = '%s --quiet %s %s' % ( exe,
                                     self._bstpkg_src.detector.topLevelDir,
                                     self._bstpkg_src.detector.canonicalPath )

        self._depDetectorData = io.BytesIO()

        self._depDetector = ProcessExecutor.ProcessExecutor()
        self._depDetector.setCommand( cmd )
        self._depDetector.newStdOut.connect( self._onDepDetectorOutput )
        self._depDetector.newStdErr.connect( self._onDepDetectorError )
        self._depDetector.finished.connect( self._onDepDetectorFinished )
        self._depDetector.start()

        logging.debug( 'dependency detection in progress (helper-process started)' )

        logging.debug( 'SQ-check setup started' )

        self._sqPreparer = self.QualityCheckPreparationThread( self._bstpkg_src )
        # noinspection PyUnresolvedReferences
        self._sqPreparer.finished.connect( self._onSQPreparerFinished )
        self._sqPreparer.start()

        self._updateCheckThread = self.UpdatesAvailableThread()
        self._updateCheckThread.updatesAvailable.connect( self._onUpdatesAvailable )
        self._updateCheckThread.start()


    def _onUpdatesAvailable(self):
        self.updatesAvailable.emit()


    def _onDepDetectorFinished( self ):
        logging.debug( 'dependency detection in progress (helper-process finished)' )

        self._depDetectorData.flush()

        base64payload     = self._depDetectorData.getvalue()
        base64payloadSize = len(base64payload)
        base64payloadType = type(base64payload)

        logging.debug( 'base64payload type: %s', base64payloadType )
        logging.debug( 'base64payload size: %d', base64payloadSize )

        if base64payloadSize == 0:
            logging.debug( 'no dependency data received' )
            return

        if not Any.isInstance( base64payload, bytes ):
            logging.debug( 'received dependency data of unexpected type' )
            logging.debug( '(this could come from a ~/.bashrc which prints text)' )
            return

        dillPayload     = base64.b64decode( base64payload )
        dillPayloadSize = len(dillPayload)
        dillPayloadType = type(dillPayload)

        logging.debug( 'dillPayload type: %s', dillPayloadType )
        logging.debug( 'dillPayload size: %d', dillPayloadSize )

        data = dill.loads( dillPayload )
        Any.requireIsDictNonEmpty( data )

        Any.requireIsInstance( data['bstpkg_src'],    BSTPackage.BSTSourcePackage )
        Any.requireIsInstance( data['bstpkg_global'], BSTPackage.BSTGloballyInstalledPackage )
        Any.requireIsDict( data['installStatus'] )
        Any.requireIsDict( data['installStatusLocal'] )
        Any.requireIsDict( data['installStatusProxy'] )
        Any.requireIsDict( data['installStatusGlobal'] )

        self._bstpkg_src.depSet   = data['bstpkg_src'].depSet
        self._bstpkg_src.depTree  = data['bstpkg_src'].depTree
        self._bstpkg_global       = data['bstpkg_global']

        try:
            self._bstpkg_global.open( self.getCanonicalPath() )
        except AssertionError as details:
            logging.debug( details )

        self._installStatus       = data['installStatus']
        self._installStatusLocal  = data['installStatusLocal']
        self._installStatusProxy  = data['installStatusProxy']
        self._installStatusGlobal = data['installStatusGlobal']

        logging.debug( 'depSet:     %s', self._bstpkg_src.depSet )
        logging.debug( 'depTree:    %s', self._bstpkg_src.depTree )
        logging.debug( 'revDepSet:  %s', self._bstpkg_global.revDepSet )
        logging.debug( 'revDepTree: %s', self._bstpkg_global.revDepTree )

        self.depsDetected.emit( True )

        # retrieving direct dependencies should work, consider an error if not

        try:
            Any.requireIsSet( self._bstpkg_src.depSet )
            Any.requireIsList( self._bstpkg_src.depTree )
        except AssertionError:
            self.depsDetected.emit( False )
            logging.error( 'unable to retrieve dependencies' )

        # while for reverse dependencies it is significant if the package is
        # installed, yet

        if self._bstpkg_global.isInstalled():
            try:
                Any.requireIsSet( self._bstpkg_global.revDepSet )
                Any.requireIsList( self._bstpkg_global.revDepTree )
            except AssertionError:
                logging.error( 'unable to retrieve reverse dependencies' )
        else:
            logging.debug( 'not globally installed --> no reverse dependencies' )

        logging.debug( 'dependency detection finished' )


    def _onDepDetectorError( self, data ):
        Any.requireIsInstance( data, QByteArray )

        text = UnicodeSupport.convertQByteArray( data )

        logging.error( text )


    def _onDepDetectorOutput( self, data ):
        Any.requireIsInstance( data, QByteArray )

        text = UnicodeSupport.convertQByteArray( data )

        self._depDetectorData.write( bytes( text, 'utf-8' ) )


    def _onSQPreparerFinished( self ):
        Any.requireIsNotNone( self._bstpkg_src.sqChecker )
        Any.requireIsInstance( self._bstpkg_src.sqChecker,
                               CheckRoutine.CheckRoutine )

        Any.requireIsDict( self._bstpkg_src.sqChecker.filesByType )

        self._sqPreparationDone = True
        self.sqCheckPrepared.emit()

        logging.debug( 'SQ-check setup finished' )


    class QualityCheckPreparationThread( QThread, object ):

        def __init__( self,  bstpkg ):
            QThread.__init__( self )

            self._bstpkg = bstpkg


        def run( self ):
            self._bstpkg.prepareQualityCheck()


    class UpdatesAvailableThread( QThread, object ):

        updatesAvailable = pyqtSignal()


        def __init__( self ):
            QThread.__init__( self )


        def run( self ):

            # suppress dry-run patching output
            oldDebugLevel = Any.getDebugLevel()
            Any.setDebugLevel( 1 )

            try:
                patchesAvailable = PatchSystem().run( dryRun=True )
            except AssertionError as e:
                # e.g. templates not installed, let's gnore this case
                logging.debug( e )
                patchesAvailable = False


            Any.setDebugLevel( oldDebugLevel )


            if patchesAvailable:
                logging.debug( 'patches available' )
                self.updatesAvailable.emit()


# EOF
