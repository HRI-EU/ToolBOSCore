# -*- coding: utf-8 -*-
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

from __future__ import print_function, unicode_literals

import logging

import clang_macroinfo

import clang.cindex as cidx
from clang.cindex import CursorKind, TypeKind


from ToolBOSCore.Platforms                         import Platforms
from ToolBOSCore.Settings                          import ToolBOSConf
from ToolBOSCore.SoftwareQuality.CAnalyzerElements import MacroDefinition,\
                                                          MacroFnDefinition, \
                                                          Namespace
from ToolBOSCore.Util                                     import Any


class CParser( Namespace ):
    """Class for parsing C code to extract variable, struct, enum, and function declarations as well as preprocessor
    macros. This is a LLVM/CLANG based C/C++ parser; it is meant to simplify the process of extracting definitions from
    header files in the absence of a complete build system.

    Usage:
        ## create parser object, load two files
        p = CParser('header1.h')

        ## just to see what was successfully parsed from the files
        p.printAll()

        ## access parsed declarations
        macros   = p.defs['macros']
        fnmacros = p.defs['fnmacros']
        ...
    """

    def __init__( self, filepath, isCPlusPlus, langStd, verbose=False, includepaths=None, defines=None, args=None ):
        """
        Creates a new CParser instance.
        The file is indexed at constructor time.
        :param filepath: the file to parse
        :param verbose: whether or not to print diagnostic information during parsing.
        :param includepaths: a list of include paths. All the basic include
                             paths must be specified, including at least:
                             - the most basic include path, on unix usually /usr/include
                             - the clang standard library include path. Distribution and clang version dependent.
                               On Ubuntu Precise 64 with clang 3.4 this is /usr/lib/clang/3.4/include
                             For C++, the C++ include paths are also required.
                             On Precise 64 these are:
                             - /usr/include/c++/4.6/
                             - /usr/include/c++/4.6/x86_64-linux-gnu/
        :param args: extra compiler flags
        """

        Any.requireIsFileNonEmpty(filepath)
        includepaths       = includepaths or []
        systemIncludePaths = self._getSystemIncludePaths()
        defines            = defines or []

        self.langStd       = langStd
        self.isCPlusPlus   = isCPlusPlus
        self.verbose       = verbose

        try:
            self._index = cidx.Index.create( )
        except cidx.LibclangError:

            hostPlatform = Platforms.getHostPlatform()
            Any.requireIsTextNonEmpty( hostPlatform )

            libs = ToolBOSConf.getConfigOption( 'clang_lib' )
            Any.requireIsDictNonEmpty( libs )

            try:
                libPath = libs[ hostPlatform ]
            except KeyError:
                logging.error( 'unsupported platform: %s', hostPlatform )
                return

            Any.requireIsFileNonEmpty( libPath )
            cidx.Config.set_library_file( libPath )

            self._index = cidx.Index.create()

        self.filepath   = filepath

        # build a list of include directory compile flags to pass to the parse method of the index.
        argsIncludeDirs = [ "-I{}".format( d ) for d in systemIncludePaths ]
        completeArgs    = argsIncludeDirs + (args or [ ])
        self.args       = completeArgs

        translationUnit = self._index.parse( filepath,
                                             options=cidx.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD,
                                             args=completeArgs )

        self.translationUnit = translationUnit

        # call super with the translation unit cursor
        super( CParser, self ).__init__( translationUnit.cursor )

        # macros are extracted separately as the clang C bindings - and thus
        # the python ones - do not provide helpers to extract the info we need.
        self._populateMacros( filepath,
                              list(systemIncludePaths) + list(includepaths),
                              defines,
                              langStd )

    def _populateMacros( self, filepath, includepaths, defines, langStd ):
        """Populates the macro definitions in defs['macros'] and defs['fnmacros']"""
        macroTuples = clang_macroinfo.get_macros( filepath.encode( 'utf8' ),
                                                  [p.encode( 'utf8' ) for p in includepaths],
                                                  True,
                                                  [d.encode( 'utf8' ) for d in defines],
                                                  langStd.encode( 'utf8' ) )

        macros   = { }
        fnmacros = { }

        for mt in macroTuples.values( ):
            # mt.args is None for simple macros, a list for function style macros.
            if mt.args is None:
                macros[ mt.name ]   = MacroDefinition( mt.name, mt.body, mt.location )
            else:
                fnmacros[ mt.name ] = MacroFnDefinition( mt.name, mt.body, mt.args, mt.location )

        self.defs[ 'macros' ]   = macros
        self.defs[ 'fnmacros' ] = fnmacros

    def __repr__( self ):
        return 'TranslationUnit({})'.format( self.defs )

    def printAll( self ):
        print( self._membersStr( ) )

        def prn( title, collection ):
            ndashes = (72 - len( title ) - 2) / 2
            dashes = ndashes * '-'
            print( '// {} {} {}'.format( dashes, title, dashes ) )
            for x in collection:
                print( x )
                print( )

        prn( 'MACROS', self.macros.values( ) )
        prn( 'MACROS FNs', self.fnmacros.values( ) )

    # noinspection PyUnresolvedReferences
    def getFunctionCalls( self, fname, node=None ):

        node   = node or self._cursor
        retval = set()

        if node.location.file and node.location.file.name != fname:
            return

        if node.kind == CursorKind.CALL_EXPR:
            retval.add( (node.displayname, node.location.line) )

        for child in node.get_children():
            childFuncs =  self.getFunctionCalls( fname, child )
            if childFuncs:
                retval.update( childFuncs )

        return retval


    # noinspection PyUnresolvedReferences
    def getVariableDeclarations( self, fname, node=None ):

        node   = node or self._cursor
        retval = set()

        if node.location.file and node.location.file.name != fname:
            return

        if node.kind in (CursorKind.VAR_DECL, CursorKind.FIELD_DECL):
            if node.type.kind in (TypeKind.POINTER,
                                  TypeKind.ELABORATED):
                retval.add( (node.displayname, node.type.spelling, node.location.line) )
            elif node.type.kind == TypeKind.CONSTANTARRAY:
                retval.add( (node.displayname, node.type.get_array_element_type().spelling, node.location.line) )
            else:
                retval.add( (node.displayname, node.type.spelling, node.location.line) )


        for child in node.get_children():
            childDecls =  self.getVariableDeclarations( fname, child )
            if childDecls:
                retval.update( childDecls )

        return retval

    def getFunctionPrototypesWithoutParameters( self, fname, node=None ):

        node   = node or self._cursor
        retval = set()

        if node.location.file and node.location.file.name != fname:
            return

        if node.type.kind == TypeKind.FUNCTIONNOPROTO:
            retval.add( (node.displayname, node.location.line) )
        elif node.type.kind == TypeKind.FUNCTIONPROTO:
            # In C++ functions without parameters are accepted by the language,
            # and do not incur in the problems that are possible in C.
            # This is why clang does not mark those nodes as FUNCTIONNOPROTO,
            # but simply as FUNCTIONPROTO. In order to find functions without
            # parameter we then have to look in the tokens, searching for an
            # open parens and making sure that it is not followed by a close parens.
            toks      = list( n.spelling for n in node.get_tokens() )

            if '(' in toks and node.kind == CursorKind.FUNCTION_DECL:
                parensIdx = toks.index( '(' )

                if toks[parensIdx + 1] == ')':
                    retval.add( (node.displayname, node.location.line) )

        for child in node.get_children():
            childFuns = self.getFunctionPrototypesWithoutParameters( fname, child )
            if childFuns:
                retval.update( childFuns )

        return retval

    @property
    def macros( self ):
        return self.defs[ 'macros' ]

    @property
    def fnmacros( self ):
        return self.defs[ 'fnmacros' ]

    @property
    def namespaceHierarchy( self ):
        return [ ]

    @property
    def hierarchy( self ):
        return [ ]

    @property
    def localFunctions( self ):
        return self._locals( self.functions, self.filepath )

    @property
    def localVariables( self ):
        return self._locals( self.variables, self.filepath )

    @property
    def localTypedefs( self ):
        return self._locals( self.typedefs, self.filepath )

    @property
    def localStructs( self ):
        return self._locals( self.structs, self.filepath )

    @property
    def localClasses( self ):
        return self._locals( self.classes, self.filepath )

    @property
    def localUnions( self ):
        return self._locals( self.unions, self.filepath )

    @property
    def localTemplateFunctions( self ):
        return self._locals( self.templateFunctions, self.filepath )

    @property
    def localTemplateClasses( self ):
        return self._locals( self.templateClasses, self.filepath )

    @property
    def localMacros( self ):
        return self._locals( self.macros, self.filepath )

    @property
    def localFnMacros( self ):
        return self._locals( self.fnmacros, self.filepath )

    @property
    def localNamespaces(self):
        return self._localNamespaces(self.filepath)

    def _getSystemIncludePaths( self ):
        """
            Calculates the include paths using the preprocessor.
        """
        from ToolBOSCore.BuildSystem.Compilers import getIncludePaths

        return getIncludePaths( 'clang-%s' % clang_macroinfo.VERSION, 'c++' ) or getIncludePaths( 'clang', 'c++' )

# EOF
