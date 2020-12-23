# -*- coding: utf-8 -*-
#
#  pkgInfo.py writer
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


import glob
import io
import logging
import os
import pprint
import re

from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.Settings                 import ToolBOSConf
from ToolBOSCore.Storage.AbstractWriter   import AbstractWriter
from ToolBOSCore.Util                     import Any
from ToolBOSCore.Util                     import FastScript


class PkgInfoWriter( AbstractWriter ):

    _indentation     = len( 'linkAllLibraries' )   # reference width
    _indentationIter = _indentation + len( ' = [' )
    _valueWidthMax   = 78 - _indentation


    def __init__( self, details, sourceTree=False ):
        """
            This constructor uses an existing PackageDetector instance
            to avoid multiple detection of package meta-information
            (for each derived subclass BashSrcWriter etc.)

            The optional parameter 'sourceTree' flags if the resulting
            pkgInfo.py is intended to be installed into SIT (=False) or
            if it should go into the source tree of the package.
            The stored fields vary depending on the target destination.
        """
        Any.require( isinstance( details, PackageDetector ) )

        super( PkgInfoWriter, self ).__init__( details )

        self._sourceTree = sourceTree
        self._pprintOut  = io.StringIO()
        self._pprinter   = pprint.PrettyPrinter( width=self._valueWidthMax,
                                                 stream=self._pprintOut )


    def formatValue( self, value ):

        if Any.isTuple( value ) or Any.isList( value ) or \
             Any.isDict( value ):
            return self.formatIterable( value )

        else:
            return repr( value )


    def formatIterable( self, value ):
        Any.requireMsg( Any.isList( value ) or Any.isTuple( value ) or
                        Any.isDict( value ),
                        'unexpected datatype, value: %s' % str(value) )

        # use pprint module for formatting, however we do some further rework
        # on its output to achieve desired result

        self._pprintOut.seek(0)
        self._pprintOut.truncate()
        self._pprinter.pprint( value )

        tmp        = self._pprintOut.getvalue().strip()
        firstChar  = tmp[0]
        lastChar   = tmp[-1]
        centerPart = tmp[1:-1].strip()

        if not value:
            result = '%s%s' % ( firstChar, lastChar )
        else:
            result = '%s %s %s' % ( firstChar, centerPart, lastChar )
            result = result.replace( '\n', '\n' + self._indentationIter * ' ' )

        return result


    def writeTable( self, table, allowNoneValue=False ):
        content  = ''

        for ( key, value ) in table.items():
            if value is not None or allowNoneValue:
                content += "%s = %s\n\n" % ( key.ljust( self._indentation ),
                                                        self.formatValue( value ) )

        return content


    def addLeadIn( self ):
        return '''# -*- coding: utf-8 -*-
#
#  Custom package settings
#
#  Copyright (C)
#  Honda Research Institute Europe GmbH
#  Carl-Legien-Str. 30
#  63073 Offenbach/Main
#  Germany
#
#  UNPUBLISHED PROPRIETARY MATERIAL.
#  ALL RIGHTS RESERVED.
#
#


'''


    def addBasicInfo( self ):
        if self._sourceTree:
            return ''
        else:
            table = { 'name'    : self.details.packageName,
                      'package' : self.details.packageName,     # legacy, for backward compat
                      'version' : self.details.packageVersion,
                      'section' : self.details.packageCategory, # legacy, for backward compat
                      'category': self.details.packageCategory }

            if self.details.patchlevel != '':                   # patchlevel might be zero!
                table[ 'patchlevel' ] = self.details.patchlevel

            return self.writeTable( table )


    def addOriginalName( self ):
        linkPath = os.path.join( self.details.topLevelDir, 'src', 'sources.tar.bz2' )

        if not os.path.islink( linkPath ):
            return ''

        origPkgName = os.readlink( linkPath ).replace( '.tar.bz2', '' )

        return self.writeTable( { 'originalName': origPkgName } )


    def addMaintainer( self ):
        data = ( self.details.userAccount, self.details.userName )

        return self.writeTable( { 'maintainer': data } )


    def addComponentInterface( self ):
        """
            In case of BBCM/BBDM packages generates the section about
            inputs, outputs, and references.
        """
        if not self.details.isComponent() or self.details.isRTMapsPackage():
            # no need to create ToolBOS-style component interface info
            return ''

        try:
            from Middleware.InfoParser import BBCMInfoParser, BBDMInfoParser, Utils
        except ImportError as e:
            pkg = ToolBOSConf.getConfigOption( 'package_toolbosmiddleware' )
            msg = 'To work with Middleware-related packages, please run ' \
                  '"source ${SIT}/%s/BashSrc" first.' % pkg

            logging.debug( e )

            raise EnvironmentError( msg )


        srcDir               = os.path.join( self.details.topLevelDir, 'src' )
        infoFileExtensionSet = [ '.c', '.cpp', '.cxx', '.cc', '.c++' ]

        if self.details.isOldBBCM():
            bbcmInfo = Utils.collectOldStyleBBCMInfos( self.details.packageName, srcDir )
            cm       = Utils.createCodeModule( bbcmInfo )

            initRefs     = cm.referenceSettings.values( )
            inputEvents  = cm.inputEvents.values( )
            inputs       = cm.inputs.values( )
            outputEvents = cm.outputEvents.values( )
            outputs      = cm.outputs.values( )
            sysRefs      = cm.systemReferences.values( )

            return self.writeTable( { 'description'      : cm.description,
                                      'systemModule'     : cm.isSystemModule,
                                      'longDescription'  : cm.longDescription,
                                      'computingMode'    : cm.computingMode,
                                      'references'       : _generateReferences( initRefs ),
                                      'systemReferences' : _generateReferences( sysRefs ),
                                      'outputEvents'     : _generateEvents( outputEvents, outputs, 'output' ),
                                      'inputEvents'      : _generateEvents( inputEvents, inputs, 'input' ),
                                      'outputs'          : _generatePorts( outputs ),
                                      'inputs'           : _generatePorts( inputs ),
                                      'initFromXML'      : False,
                                      'moduleType'       : cm.moduleType,
                                      'isOldStyleBBCM'   : True } )

        elif self.details.isNewBBCM():
            infoFiles      = glob.glob( os.path.join( srcDir, '{}_info.*'.format( self.details.packageName ) ) )
            validInfoFiles = []

            hasInitFromXML = Utils.hasInitFromXML( 'BBCM', srcDir, self.details.packageName )

            Any.requireIsListNonEmpty( infoFiles )

            for f in infoFiles:
                name, ext = os.path.splitext( f )
                if ext.lower( ) in infoFileExtensionSet:
                    validInfoFiles.append( f )

            numValid = len( validInfoFiles )
            Any.requireMsg( numValid == 1,
                            'expected one *_info.c file, found %d' % numValid )

            infoFilePath = validInfoFiles[ 0 ]
            Any.requireIsFileNonEmpty( infoFilePath )

            parser = BBCMInfoParser.BBCMInfoParser( )
            infos  = parser.parse( FastScript.getFileContent( infoFilePath ) )

            cm = Utils.createCodeModule( infos )

            initRefs     = cm.referenceSettings.values( )
            inputEvents  = cm.inputEvents.values( )
            inputs       = cm.inputs.values( )
            outputEvents = cm.outputEvents.values( )
            outputs      = cm.outputs.values( )
            sysRefs      = cm.systemReferences.values( )

            return self.writeTable( { 'description'      : cm.description,
                                      'systemModule'     : cm.isSystemModule,
                                      'longDescription'  : cm.longDescription,
                                      'computingMode'    : cm.computingMode,
                                      'references'       : _generateReferences( initRefs ),
                                      'systemReferences' : _generateReferences( sysRefs ),
                                      'outputEvents'     : _generateEvents( outputEvents, outputs, 'output' ),
                                      'inputEvents'      : _generateEvents( inputEvents, inputs, 'input' ),
                                      'outputs'          : _generatePorts( outputs ),
                                      'inputs'           : _generatePorts( inputs ),
                                      'moduleType'       : cm.moduleType,
                                      'initFromXML'      : hasInitFromXML,
                                      'isOldStyleBBCM'   : False } )

        elif self.details.isBBDM():

            # BBDMAll is special, it does not have its own interface
            if self.details.packageName == 'BBDMAll':
                return ''

            srcFiles      = glob.glob( os.path.join( srcDir, '{}.*'.format( self.details.packageName ) ) )
            validSrcFiles = []

            hasInitFromXML = Utils.hasInitFromXML( 'BBDM', srcDir, self.details.packageName )

            for f in srcFiles:
                name, ext = os.path.splitext( f )
                if ext.lower( ) in infoFileExtensionSet:
                    validSrcFiles.append( f )

            numValid = len( validSrcFiles )
            Any.requireMsg( numValid == 1,
                            'expected one source file, found %d' % numValid )

            infoFilePath = validSrcFiles[ 0 ]
            Any.requireIsFileNonEmpty( infoFilePath )

            parser = BBDMInfoParser.BBDMInfoParser()
            infos  = parser.parse( FastScript.getFileContent( infoFilePath ) )

            cm = Utils.createDataModule( infos )

            initRefs     = cm.referenceSettings.values( )
            inputs       = cm.inputs.values( )
            outputs      = cm.outputs.values( )
            sysRefs      = cm.systemReferences.values( )

            return self.writeTable( { 'description'      : cm.description,
                                      'references'       : _generateReferences( initRefs ),
                                      'outputs'          : _generatePorts( outputs ),
                                      'inputs'           : _generatePorts( inputs ),
                                      'moduleType'       : cm.moduleType,
                                      'initFromXML'      : hasInitFromXML,
                                      'systemReferences' : _generateReferences( sysRefs ) } )

        elif self.details.isVirtualModule():
            from Middleware.BBMLv1.LoadBBML import loadVirtualModule

            projectName    = self.details.packageName
            projectVersion = self.details.packageVersion
            canonicalPath  = self.details.canonicalPath
            category       = self.details.packageCategory

            Any.requireIsTextNonEmpty( projectName )
            Any.requireIsTextNonEmpty( projectVersion )
            Any.requireIsTextNonEmpty( canonicalPath )
            Any.requireIsTextNonEmpty( category )

            sourcePath    = _getSourceFile( projectName, srcDir )
            interfacePath = _getInterfaceFile( projectName, srcDir )
            sourcePathExt = os.path.splitext( sourcePath )[1]

            Any.requireIsFileNonEmpty( sourcePath )
            Any.requireIsFileNonEmpty( interfacePath )

            # generate content
            virtualModule = loadVirtualModule( sourcePath, interfacePath, synthesizable=True )

            inputs       = virtualModule.inputs.values()
            outputs      = virtualModule.outputs.values()
            inputEvents  = virtualModule.inputEvents.values()
            outputEvents = virtualModule.outputEvents.values()

            return self.writeTable( {
                'inputEvents'     : _generateVirtualModulePorts( inputEvents ),
                'inputs'          : _generateVirtualModulePorts( inputs ),
                'library'         : 'VirtualModule',
                'moduleType'      : 'VirtualModule',
                'outputEvents'    : _generateVirtualModulePorts( outputEvents ),
                'outputs'         : _generateVirtualModulePorts( outputs ),
                'references'      : _generateVirtualModuleReferences( virtualModule ),
                'sourcePath'      : os.path.join( r'${SIT}', canonicalPath, 'include', projectName + sourcePathExt ),
                'virtualExecutor' : _generateVirtualExecutors( virtualModule )
            } )

        else:
            raise ValueError( 'unknown component type' )


    def addRepositoryInfo( self ):
        if self.details.gitFound:

            data = { 'gitBranch'     : self.details.gitBranch,
                     'gitCommitID'   : self.details.gitCommitIdLong,
                     'gitOrigin'     : self.details.gitOrigin,
                     'gitRelPath'    : self.details.gitRelPath }

            if self.details.gitBranchForCIA:
                data[ 'gitBranchForCIA' ] = self.details.gitBranchForCIA

            if self.details.gitOriginForCIA:
                data[ 'gitOriginForCIA' ] = self.details.gitOriginForCIA

        else:
            data = { 'revision'      : self.details.svnRevision,
                     'repositoryRoot': self.details.svnRepositoryRoot,
                     'repositoryUrl' : self.details.svnRepositoryURL,
                     'revisionForCIA': self.details.svnRevisionForCIA }

        return self.writeTable( data )


    def addDependencies( self ):
        result = ''

        if self.details.dependencies:
            result += self.writeTable( { 'depends': self.details.dependencies } )

        if self.details.dependsArch:
            result += self.writeTable( { 'dependsArch': self.details.dependsArch } )

        return result


    def addBuildDependencies( self ):
        result = ''

        if self.details.buildDependencies:
            result += self.writeTable( { 'buildDepends': self.details.buildDependencies } )

        if self.details.buildDependsArch:
            result += self.writeTable( { 'buildDependsArch': self.details.buildDependsArch } )

        return result


    def addRecommendations( self ):
        if self.details.recommendations:
            return self.writeTable( { 'recommends': self.details.recommendations } )
        else:
            return ''


    def addSuggestions( self ):
        if self.details.suggestions:
            return self.writeTable( { 'suggests': self.details.suggestions } )
        else:
            return ''


    def addMainLoop( self ):
        """
            The "MainLoop" historically was the part in the BashSrc files
            which contained the loop over all inherited BashSrc files to
            source the dependencies. It also contained add. environment
            settings the user might have specified in the pkgInfo.py.
                Hence we use the same function here to store the environment
            settings even if no "MainLoop" equivalent is present.
        """
        envVars = []


        # add package to LD_LIBRARY_PATH if it contains a library

        if os.path.isdir( os.path.join( self.details.topLevelDir, 'lib' ) ):
            varName  = 'LD_LIBRARY_PATH'
            varValue = '${LD_LIBRARY_PATH}:${SIT}/' \
                       '%s/lib/${MAKEFILE_PLATFORM}' % self.details.canonicalPath

            envVars.append( ( varName, varValue ) )


        # envVar-settings from pkgInfo.py:

        if self.details.userSrcEnv:
            envVars += self.details.userSrcEnv


        if envVars:
            return self.writeTable( { 'envVars': envVars } )
        else:
            return ''


    def addLeadOut( self ):
        return '\n# EOF\n'


    #------------------------------------------------------------------------
    # add. methods for modifying a pkgInfo.py, apart from the general
    # TemplateWriter interface
    #------------------------------------------------------------------------


    def setLeadIn( self ):
        self.content = self.addLeadIn()


    def setContent( self, filePath ):
        """
            Allows setting content from original file, in order to evolve an
            existing pkgInfo.py over time.
        """
        Any.requireIsFileNonEmpty( filePath )
        self.content = FastScript.getFileContent( filePath )


    def setLinkAllLibraries( self, boolean ):
        Any.requireIsBool( boolean )
        self.content += self.writeTable( { 'linkAllLibraries': boolean } )


    def setUsePatchlevelSystem( self, boolean ):
        Any.requireIsBool( boolean )
        self.content += self.writeTable( { 'usePatchlevels': boolean } )


    def setInstallUmask( self, umask ):
        Any.requireIsIntNotZero( umask )
        self.content += self.writeTable( { 'installUmask': umask } )


    def setInstall( self, patternList ):
        Any.requireIsListNonEmpty( patternList )
        self.content += self.writeTable( { 'install': patternList } )


    def setInstallMatching( self, patternList ):
        Any.requireIsListNonEmpty( patternList )
        self.content += self.writeTable( { 'installMatching': patternList } )


    def setLeadOut( self ):
        # ensure that EOF is not found in between the file
        self.content = self.content.replace( '# EOF\n', '' )
        self.content += '\n# EOF\n'


# ----------------------------------------------------------------------------
# Private functions
# ----------------------------------------------------------------------------

def _generateReferences( references ):
    retVal = [ ]

    for r in references:
        retVal.append( (r.name, r.type, r.format, r.default, r.description, r.range, r.complex) )

    return retVal


def _generateEvents( eventPorts, dataPorts, direction ):
    retVal = [ ]

    for e in eventPorts:
        retVal.append( (e.name, e.description) )

    for d in dataPorts:
        retVal.append( (d.name, 'Notify a change in the ' + direction) )

    return retVal


def _generatePorts( ports ):
    retVal = [ ]

    for p in ports:
        retVal.append( (p.name, p.portType, p.description, p.necessity) )

    return retVal

def _generateVirtualExecutors( virtualModule ):
    from Middleware.BBMLv1.Graph import VirtualModule

    Any.requireIsInstance( virtualModule, VirtualModule )

    retVal = []

    for executor in virtualModule.executors.values():
        retVal.append( ( executor.name,
                         executor.type,
                         '<NO DESCRIPTION>' ) )

    return retVal


def _generateVirtualModulePorts( ports ):
    retVal = []

    for p in ports:
        mandatory = 'MANDATORY' if p.mandatory == 'true' else 'OPTIONAL'
        retVal.append( (p.name, p.dataType, p.description, p.contents, mandatory) )

    return retVal


def _generateVirtualModuleReferences( virtualModule ):
    from Middleware.BBMLv1.Graph import VirtualModule

    Any.requireIsInstance( virtualModule, VirtualModule )

    retVal                   = []
    referenceImplementations = dict( (d.name, d.value) for d in virtualModule.referenceImplementations )

    for definition in virtualModule.referenceDefinitions:
        value = ''

        if definition.name in referenceImplementations:
            value = referenceImplementations[ definition.name ]

        retVal.append( ( definition.name,
                         definition.dataType or '<NO DATA TYPE>',
                         definition.format,
                         value,
                         definition.description or '<NO DESCRIPTION>',
                         '<NO RANGE DESCRIPTION>' ) )

    return retVal

def _getSourceFile( projectName, srcDir ):

    Any.requireIsTextNonEmpty( projectName )
    Any.requireIsDir( srcDir )

    r     = r'^({}\.[x,bb]ml)$'.format( projectName )
    files = []

    for f in os.listdir( srcDir ):
        match = re.search( r, f )
        if match:
            files.append( os.path.join( srcDir, match.group(1) ) )

    Any.requireIsListNonEmpty( files )
    Any.requireMsg( len(files) == 1, 'More than one valid source file was found for VirtualModule {}: {}'.format( projectName,
                                                                                                                  files ) )

    return files[0]

def _getInterfaceFile( projectName, srcDir ):
    Any.requireIsTextNonEmpty( projectName )
    Any.requireIsDir( srcDir )

    r     = r'^(I{}\.[x,bb]ml)$'.format( projectName )
    files = []

    for f in os.listdir( srcDir ):
        match = re.match( r, f )
        if match:
            files.append( os.path.join( srcDir, match.group(1) ) )

    Any.requireIsListNonEmpty( files )
    Any.requireMsg( len(files) == 1, 'More than one valid interface file was found for VirtualModule {}: {}'.format( projectName,
                                                                                                                     files ) )

    return files[0]

# EOF
