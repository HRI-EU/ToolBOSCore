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


import io
import os
import pprint

from ToolBOSCore.Packages import PackageDetector
from ToolBOSCore.Storage  import AbstractWriter
from ToolBOSCore.Util     import FastScript


class PkgInfoWriter( AbstractWriter.AbstractWriter ):

    _indentation     = 16   # reference width
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
        FastScript.require( isinstance( details, PackageDetector.PackageDetector ) )

        super( PkgInfoWriter, self ).__init__( details )

        self._sourceTree = sourceTree
        self._pprintOut  = io.StringIO()
        self._pprinter   = pprint.PrettyPrinter( width=self._valueWidthMax,
                                                 stream=self._pprintOut )


    def formatValue( self, value ):

        if FastScript.isTuple( value ) or FastScript.isList( value ) or \
             FastScript.isDict( value ):
            return self.formatIterable( value )

        else:
            return repr( value )


    def formatIterable( self, value ):
        FastScript.requireMsg( FastScript.isList( value ) or FastScript.isTuple( value ) or
                        FastScript.isDict( value ),
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


    def addRepositoryInfo( self ):
        if self.details.gitFound:

            data = { 'gitBranch'     : self.details.gitBranch,
                     'gitCommitID'   : self.details.gitCommitIdLong,
                     'gitOrigin'     : self.details.gitOrigin,
                     'gitRelPath'    : self.details.gitRelPath }

        else:
            data = {}

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
                Hence, we use the same function here to store the environment
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
        FastScript.requireIsFileNonEmpty( filePath )
        self.content = FastScript.getFileContent( filePath )


    def setUsePatchlevelSystem( self, boolean ):
        FastScript.requireIsBool( boolean )
        self.content += self.writeTable( { 'usePatchlevels': boolean } )


    def setInstallUmask( self, umask ):
        FastScript.requireIsIntNotZero( umask )
        self.content += self.writeTable( { 'installUmask': umask } )


    def setInstall( self, patternList ):
        FastScript.requireIsListNonEmpty( patternList )
        self.content += self.writeTable( { 'install': patternList } )


    def setInstallMatching( self, patternList ):
        FastScript.requireIsListNonEmpty( patternList )
        self.content += self.writeTable( { 'installMatching': patternList } )


    def setLeadOut( self ):
        # ensure that EOF is not found in between the file
        self.content = self.content.replace( '# EOF\n', '' )
        self.content += '\n# EOF\n'


# EOF
