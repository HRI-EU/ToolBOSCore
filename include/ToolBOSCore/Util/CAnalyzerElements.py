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

import itertools
import clang.cindex as cidx

from ToolBOSCore.Util import Any


def getNamespaceHierarchy( cur ):
    """
        Returns the full namespace name where the object identified by the
        clang cursor is contained, as a list.

        Example:
            if cur identifies the variable abc::xyz::bar, returns ['abc', 'xyz']
    """
    res = [ ]
    while cur.semantic_parent and cur.semantic_parent.kind == cidx.CursorKind.NAMESPACE:
        res.insert( 0, cur.semantic_parent.spelling )
        cur = cur.semantic_parent
    return res


def getParentNamespace( cursor ):
    """
        Returns the full namespace name where the object identified by the
        clang cursor is contained.
    """
    return "::".join( getNamespaceHierarchy( cursor ) )


def _addDefinitionOrPrototype( c, definitionSet, definitionCls, prototypeCls ):
    tmpDefinition = definitionCls( c.get_definition( ) or c.canonical or c )
    if tmpDefinition not in definitionSet:
        definitionSet.add( tmpDefinition )
    if not c.is_definition( ):
        # the node of the AST we are visiting now is not a definition node.
        # This means we just encountered a function prototype.
        # We extract the definition from definitionSet, and add
        definition = None
        for f in definitionSet:
            # equals is redefined so that two definitions are equals if the location
            # (file, line, column) is the same
            if f == tmpDefinition:
                definition = f
                break

        Any.requireIsNotNone( definition )

        definition.prototypes.append( prototypeCls( c ) )


class Definition( object ):
    """
        Base class for definitions
        Exposed fields:
        - name
        - location
    """

    def __init__( self, name, location ):
        """
            Create a new Definition instance with the given name and location,
            which must be None or a tuple
            (file, line, column)
        """
        self.name     = name
        self.location = location

    def __key( self ):
        # noinspection PyRedundantParentheses
        return (self.name,)

    def __hash__( self ):
        return hash( self.__key( ) + self.location )

    @property
    def namespaceHierarchy( self ):
        """
            Returns the parent namespace hierarchy as a list
        """
        return [ ]

    @property
    def parentNamespace( self ):
        """
            Returns the a string representation of the parent namespace
        """
        return "::".join( self.namespaceHierarchy )

    @property
    def _classname( self ):
        return self.__class__.__name__


class MacroDefinition( Definition ):
    """
        Represents a simple macro definition.
        a MacroDefinition exposes 3 fields:
        - name
        - body
        - location
    """

    def __init__( self, name, body, loc ):
        """
            Create a new MacroDefinition, with the given macro name, body and definition location
        """
        super( MacroDefinition, self ).__init__( name, loc )

        self.body = body

    def __repr__( self ):
        return '{}({}, {}, {})'.format( self._classname, repr( self.name ),
                                        repr( self.body ), repr( self.location ) )

    def __str__( self ):
        return '[{}] {} = {}'.format( self.location, self.name, self.body )


class MacroFnDefinition( MacroDefinition ):
    """
        Represents a function style macro definition.
        exposes 4 fields:
        - name
        - args (a list of argument names)
        - body
        - location
    """

    def __init__( self, name, body, params, loc=None ):
        """
            Create a macro function definition, with the given name, body,
            arguments and definition location
        """
        super( MacroFnDefinition, self ).__init__( name, body, loc )

        self.params = params or [ ]

    def __repr__( self ):
        return '{}({}, {}, {}, {})'.format( self._classname, repr( self.name ),
                                            repr( self.params ), repr( self.body ),
                                            repr( self.location ) )

    def __str__( self ):
        argsStr = ', '.join( self.params )
        return '[{}] {}({}) = {}'.format( self.location, self.name, argsStr, self.body )


class DefinitionWithCursor( Definition ):
    """
        A Definition extracted from a libclang cursor
    """

    def __init__( self, cursor ):
        """
            Initializes the definition with the name and location extracted from the cursor
        """
        loc = cursor.location
        try:
            self._dloc = (loc.file.name, loc.line, loc.column)
        except AttributeError:
            self._dloc = None

        super( DefinitionWithCursor, self ).__init__( cursor.spelling, self._dloc )

        self._cursor = cursor

        try:
            acc = self._cursor.access_specifier.name
            if acc == 'INVALID':
                self.access = None
            else:
                self.access = acc
        except AttributeError:
            # This happens with ancient versions of clang, such as 3.4
            # logging.debug( "access specifier (PUBLIC, PRIVATE, PROTECTED) not available." )
            self.access = None

    @property
    def _accessString( self ):
        if self.access is None:
            return ''
        else:
            return self.access + ' '

    # noinspection PyProtectedMember
    # o is an instqance of this class, so the warning
    # does not make sense.
    def __eq__( self, o ):
        return self._cursor.location == o._cursor.location

    def __hash__( self ):
        return hash( self._dloc )

    def _key( self ):
        return self.name, self._cursor

    @property
    def namespaceHierarchy( self ):
        """
            Returns the parent namespace hierarchy as a list.
        """
        return getNamespaceHierarchy( self._cursor )


class FunctionParameter( DefinitionWithCursor ):
    """
        Represents a function argument.
        exposes 3 fields:
        - name
        - type (a string representing the type)
        - location
    """

    def __init__( self, cursor ):
        """
            Create a new FunctionArgument instance from a function argument cursor
        """
        super( FunctionParameter, self ).__init__( cursor )

        self.type = cursor.type.spelling

    def __repr__( self ):
        return '{}({}, {})'.format( self._classname, repr( self.name ), repr( self.type ) )

    def __str__( self ):
        return '{} {}'.format( self.type, self.name )


class FunctionDefinition( DefinitionWithCursor ):
    """
        Represents a function definition.
        Exposes 4 fields:
        - name
        - params (a list of FunctionArgument objects)
        - returnType (a string representing the return type)
        - location
        - isVariadic: True if variadic, False if not variadic, None if libclang cannot determine it.
    """

    def __init__( self, cursor ):
        """
            Create a new FunctionDefinition instance from a function argument cursor
        """
        super( FunctionDefinition, self ).__init__( cursor )

        self.returnType = cursor.type.get_result( ).spelling
        self.params      = [ FunctionParameter( arg ) for arg in cursor.get_arguments( ) ]
        self.prototypes  = [ ]
        if cursor.type.kind != cidx.TypeKind.FUNCTIONPROTO:
            self.isVariadic = None
        else:
            self.isVariadic = cursor.type.is_function_variadic( )

    def __repr__( self ):
        return '{}({}, {}, {}, variadic={})'.format( self._classname, repr( self.name ),
                                                     repr( self.returnType ), repr( self.params ),
                                                     repr( self.isVariadic ) )

    def __str__( self ):
        paramsStr = [ str( a ) for a in self.params ]
        if self.isVariadic:
            paramsStr.append( str( '...' ) )
        return '{} {}({})'.format( self.returnType, self.name,
                                   ', '.join( paramsStr ) )


class FunctionPrototype( FunctionDefinition ):
    """
        Represents a function prototype.
    """
    pass


class Typedef( DefinitionWithCursor ):
    """
        Represents a typedef declaration.
        Exposes 3 fields:
        - name (the name of the new defined type)
        - type (the string representation of the type being aliased)
        - location
    """

    def __init__( self, cursor ):
        """
            Create a new instance of Typedef
        """
        super( Typedef, self ).__init__( cursor )

        self.type   = cursor.underlying_typedef_type.spelling

    def __repr__( self ):
        return '{}({}, {}, {})'.format( self._classname, self.name, self.type, self.access )

    def __str__( self ):
        return '{}typedef {} {}'.format( self._accessString, self.type, self.name )


class Enum( DefinitionWithCursor ):
    """
        Represents a enum definition
        Exposes 3 fields:
        - name
        - values (an array of enum constant names)
        - location
    """

    def __init__( self, cursor ):
        """
            Create a new instance of Enum
        """
        super( Enum, self ).__init__( cursor )

        self.values = [ c.spelling for c in cursor.get_children( )
                        if c.kind == cidx.CursorKind.ENUM_CONSTANT_DECL ]

    def __repr__( self ):
        return '{}({}, {}, {})'.format( self._classname, repr( self.name ),
                                        repr( self.values ), repr( self.access ) )

    def __str__( self ):
        return '{}enum {} {{ {} }}'.format( self._accessString, self.name,
                                            ', '.join( self.values ) )


class Variable( DefinitionWithCursor ):
    """
        Represents a variable or struct field declaration.
        Exposes 3 fields:
        - name
        - type (a string representation of the variable type)
        - location
    """

    def __init__( self, cursor ):
        """
            Create a new instance of Variable
        """
        super( Variable, self ).__init__( cursor )

        self.type = cursor.type.spelling

    def __repr__( self ):
        return '{}({} {})'.format( self._classname, repr( self.name ), repr( self.type ) )

    def __str__( self ):
        return '{} {}'.format( self.type, self.name )


class Field( Variable ):
    """
        Represent a struct, union or class field.
        Exposes the following fields:
        - name
        - location
        - type
        - access (PUBLIC, PRIVATE, PROTECTED, None)
    """

    def __init__( self, cursor ):
        """
            Create a new instance of Field
        """
        super( Field, self ).__init__( cursor )

    def __repr__( self ):
        return '{}({}, {}, {})'.format( self._classname, repr( self.name ),
                                        repr( self.type ), repr( self.access ) )

    def __str__( self ):
        return '{}{} {}'.format( self._accessString, self.type, self.name )


class Constructor( DefinitionWithCursor ):
    """
        Represents a struct, union or class constructor.
        Exposes the following fields:
        - name
        - location
        - params (a list of FunctionParameter objects)
        - access (PUBLIC, PRIVATE, PROTECTED, None(
    """

    def __init__( self, cursor ):
        """
            Create a new instance of Constructor
        """
        super( Constructor, self ).__init__( cursor )

        self.params = [ FunctionParameter( p ) for p in cursor.get_arguments( ) ]

    def __repr__( self ):
        return '{}({}, {}, {})'.format( self._classname, repr( self.name ),
                                        repr( self.params ), repr( self.access ) )

    def __str__( self ):
        return '{}({})'.format( self.name, ', '.join( [ str( a ) for a in self.params ] ) )


class Destructor( DefinitionWithCursor ):
    """
        Represents a struct, union or class constructor.
        Exposes the following fields:
        - name
        - location
        - access (PUBLIC, PRIVATE, PROTECTED, None(
    """
    def __init__( self, cursor ):
        """
            Create a new instance of Destructor
        """
        super( Destructor, self ).__init__( cursor )

    def __repr__( self ):
        return '{}({}, {})'.format( self._classname, repr( self.name[ 1: ] ), repr( self.access ) )

    def __str__( self ):
        return '{}{}()'.format( self._accessString, self.name )


class Method( FunctionDefinition ):
    """
        Represents a struct, union or class method.
        - name
        - location
        - access (PUBLIC, PRIVATE, PROTECTED, None)
        - params (a list of FunctionArgument objects)
        - returnType (a string representing the return type)
    """
    def __init__( self, cursor ):
        """
            Create a new instance of Method
        """
        super( Method, self ).__init__( cursor )

    def __repr__( self ):
        return '{}({}, {}, {}, {})'.format( self._classname, repr( self.name ),
                                            repr( self.returnType ), repr( self.params ),
                                            repr( self.access ) )

    def __str__( self ):
        paramsStr = [ str( a ) for a in self.params ]
        if self.isVariadic:
            paramsStr.append( str( '...' ) )
        return '{}{} {}({})'.format( self._accessString, self.returnType, self.name,
                                     ', '.join( paramsStr ) )


class MethodPrototype( Method ):
    """
        Represents a method prototype.
    """
    pass


class TemplateParameter( DefinitionWithCursor ):
    """
        Represents a template parameter.
        Exposes the following fields:
        - name
        - location
        - type (the string representation of a basic type, or 'typename' for a type parameter)
    """
    def __init__( self, cursor ):
        """
            Create a new instance of TemplateParameter
        """
        super( TemplateParameter, self ).__init__( cursor )

        if cursor.kind == cidx.CursorKind.TEMPLATE_TYPE_PARAMETER:
            self.type = 'typename'
        else:
            self.type = cursor.type.spelling

    def __repr__( self ):
        return '{}({}, {})'.format( self._classname, repr( self.name ), repr( self.type ) )

    def __str__( self ):
        return '{} {}'.format( self.type, self.name )


class TemplateFunctionDefinition( Method ):
    """
        Represents a template function definition.
        - name
        - location
        - access (PUBLIC, PRIVATE, PROTECTED, None)
        - params (a list of FunctionArgument objects)
        - returnType (a string representing the return type)
        - templateParameters (a list of TemplateParameter objects)
    """

    def __init__( self, cursor ):
        """
            Create a new instance of TemplateFunctionDefinition
        """
        super( TemplateFunctionDefinition, self ).__init__( cursor )

        # the call to super cannot extract the parameters, because
        # get_arguments() returns [] for template functions.
        self.params = self._extractParameters( cursor )
        self.templateParameters = self._extractTemplateParameters( cursor )

    def _extractTemplateParameters( self, cursor ):
        res = [ ]
        for c in cursor.get_children( ):
            if c.kind in (cidx.CursorKind.TEMPLATE_TYPE_PARAMETER,
                          cidx.CursorKind.TEMPLATE_NON_TYPE_PARAMETER):
                res.append( TemplateParameter( c ) )
        return res

    def _extractParameters( self, cursor ):
        res = [ ]
        for c in cursor.get_children( ):
            if c.kind == cidx.CursorKind.PARM_DECL:
                res.append( FunctionParameter( c ) )
        return res

    def __repr__( self ):
        return '{}({}, {}, {}, {}, {})'.format( self._classname,
                                                repr( self.name ),
                                                repr( self.returnType ),
                                                repr( self.params ),
                                                repr( self.templateParameters ),
                                                repr( self.access ) )

    def __str__( self ):
        res = super( TemplateFunctionDefinition, self ).__str__( )

        tparams      = ', '.join( [ str( p ) for p in self.templateParameters ] )
        templateDef = 'template<{}>'.format( tparams )

        return templateDef + '\n' + res


class TemplateFunctionPrototype( TemplateFunctionDefinition ):
    """
        Represents a function prototype.
    """
    pass

class Struct( DefinitionWithCursor ):
    """
        Represents a struct definition.
        Exposes the following fields:
        - name
        - location
        - access (PUBLIC, PRIVATE, PROTECTED, None)
        - fields (dictionary of Field objects)
        - constructors (list of Constructor objects)
        - methods (dictionary of sets of Method objects)
        - structs (nested structs, dictionary of Struct objects)
        - classes (nested classes, dictionary of ClassDef objects)
        - typedefs (dictionary of typedef objects)
        - destructor (a Destructor object if present, None otherwise)
        - enums (dictionary of Enum objects)
        - unions (dictionary of Union objects)
        - templateFunctions (dictionary of sets of FunctionTemplateDefinition objects)
        - templateClasses (nested template classes, union or structs; dictionary of ClassTemplateDef objects)
    """

    def __init__( self, cursor ):
        """
            Create a new instance of Struct
        """
        super( Struct, self ).__init__( cursor )

        self.fields             = { }
        self.constructors       = [ ]
        self.methods            = { }
        self.structs            = { }
        self.classes            = { }
        self.typedefs           = { }
        self.destructor         = None
        self.enums              = { }
        self.unions             = { }
        self.templateFunctions = { }
        self.templateClasses   = { }

        for c in cursor.get_children( ):
            if c.kind == cidx.CursorKind.FIELD_DECL:
                self.fields[ c.spelling ] = Field( c )

            elif c.kind == cidx.CursorKind.CONSTRUCTOR:
                self.constructors.append( Constructor( c.get_definition( ) or c.canonical or c ) )

            elif c.kind == cidx.CursorKind.DESTRUCTOR:
                self.destructor = Destructor( c )

            elif c.kind == cidx.CursorKind.CXX_METHOD:
                if c.spelling not in self.methods:
                    self.methods[ c.spelling ] = set( )
                fset = self.methods[ c.spelling ]
                _addDefinitionOrPrototype( c, fset, Method, MethodPrototype )

            elif c.kind == cidx.CursorKind.STRUCT_DECL:
                self.structs[ c.spelling ] = Struct( c.get_definition() or c.canonical or c )

            elif c.kind == cidx.CursorKind.CLASS_DECL:
                self.classes[ c.spelling ] = ClassDef( c.get_definition() or c.canonical or c )

            elif c.kind == cidx.CursorKind.TYPEDEF_DECL:
                self.typedefs[ c.spelling ] = Typedef( c )

            elif c.kind == cidx.CursorKind.ENUM_DECL:
                self.enums[ c.spelling ] = Enum( c.get_definition() or c.canonical or c )

            elif c.kind == cidx.CursorKind.UNION_DECL:
                self.unions[ c.spelling ] = Union( c.get_definition() or c.canonical or c )

            elif c.kind == cidx.CursorKind.FUNCTION_TEMPLATE:
                if c.spelling not in self.templateFunctions:
                    self.templateFunctions[ c.spelling ] = set( )
                fset = self.templateFunctions[ c.spelling ]
                _addDefinitionOrPrototype( c, fset, TemplateFunctionDefinition,
                                           TemplateFunctionPrototype )

            elif c.kind == cidx.CursorKind.CLASS_TEMPLATE:
                if c.spelling not in self.templateClasses:
                    self.templateClasses[ c.spelling ] = set( )
                classTemplateDef =  ClassTemplateDef( c.get_definition() or c.canonical or c )
                self.templateClasses[ c.spelling ].add( classTemplateDef )

    def __repr__( self ):
        return 'Struct({}, {}, {}, {}, {}, {}, {}, ' \
               '{}, {}, {}, {}, {}, {})'.format( repr( self.name ),
                                                 repr( self.fields ),
                                                 repr( self.constructors ),
                                                 repr( self.destructor ),
                                                 repr( self.methods ),
                                                 repr( self.templateFunctions ),
                                                 repr( self.structs ),
                                                 repr( self.classes ),
                                                 repr( self.templateClasses ),
                                                 repr( self.typedefs ),
                                                 repr( self.enums ),
                                                 repr( self.unions ),
                                                 repr( self.access ) )

    def __str__( self ):

        def indent( s ):
            lines = [ '\t' + l for l in s.split( '\n' ) ]
            return '\n'.join( lines )

        methods  = itertools.chain( *self.methods.values( ) )
        tfuncs   = itertools.chain( *self.templateFunctions.values( ) )
        tclasses = itertools.chain( *self.templateClasses.values( ) )

        if self.destructor:
            dtor = [ self.destructor ]
        else:
            dtor = [ ]

        stuff = itertools.chain( self.enums.values( ),
                                 self.typedefs.values( ),
                                 self.structs.values( ),
                                 self.classes.values( ),
                                 self.unions.values( ),
                                 tclasses,
                                 self.fields.values( ),
                                 self.constructors,
                                 dtor,
                                 methods,
                                 tfuncs )

        return '{}struct {} {{\n{}\n}}'.format( self._accessString,
                                                self.name,
                                                indent( '\n'.join( [ str( x ) + ';' for x in stuff ] ) ) )


class ClassDef( Struct ):
    """
        Represents a C++ class definition
        Exposes the following fields
        - name
        - location
        - access (PUBLIC, PRIVATE, PROTECTED, None)
        - fields (dictionary of Field objects)
        - constructors (list of Constructor objects)
        - methods (dictionary of sets of Method objects)
        - structs (nested structs, dictionary of Struct objects)
        - classes (nested classes, dictionary of ClassDef objects)
        - typedefs (dictionary of typedef objects)
        - destructor (a Destructor object if present, None otherwise)
        - enums (dictionary of Enum objects)
        - unions (dictionary of Union objects)
        - templateFunctions (dictionary of sets of FunctionTemplateDefinition objects)
        - templateClasses (nested template classes, union or structs; dictionary of ClassTemplateDef objects)
    """

    def __init__( self, cursor ):
        """
            Create a new instance of ClassDef
        """
        super( ClassDef, self ).__init__( cursor )

    def __repr__( self ):
        ret = super( ClassDef, self ).__str__( )

        return ret.replace( 'Struct', 'ClassDef', 1 )

    def __str__( self ):
        ret = super( ClassDef, self ).__str__( )

        return ret.replace( 'struct', 'class', 1 )


# Unluckily, libclang does not distinguish between struct, union or class templates.
# TODO: find a way to know if we are handling a struct, class or union template.
class ClassTemplateDef( ClassDef ):
    """
        Represents a class, struct or union template.
        - name
        - location
        - access (PUBLIC, PRIVATE, PROTECTED, None)
        - fields (dictionary of Field objects)
        - constructors (list of Constructor objects)
        - methods (dictionary of sets of Method objects)
        - structs (nested structs, dictionary of Struct objects)
        - classes (nested classes, dictionary of ClassDef objects)
        - typedefs (dictionary of typedef objects)
        - destructor (a Destructor object if present, None otherwise)
        - enums (dictionary of Enum objects)
        - unions (dictionary of Union objects)
        - templateFunctions (dictionary of sets of FunctionTemplateDefinition objects)
        - templateClasses (nested template classes, union or structs; ictionary of ClassTemplateDef objects)
        - templateParameters (a list of TemplateParameter objects)
    """

    def __init__( self, cursor ):
        """
            Create a new instance of ClassTemplateDef
        """
        super( ClassTemplateDef, self ).__init__( cursor )

        self.templateParameters = self._extractTemplateParameters( cursor )

    def _extractTemplateParameters( self, cursor ):
        res = [ ]
        for c in cursor.get_children( ):
            if c.kind in (cidx.CursorKind.TEMPLATE_TYPE_PARAMETER,
                          cidx.CursorKind.TEMPLATE_NON_TYPE_PARAMETER):
                res.append( TemplateParameter( c ) )
        return res

    def __repr__( self ):
        return '{}({}, {}, {}, {}, {}, {}, {}, ' \
               '{}, {}, {}, {}, {}, {}, {})'.format( self._classname,
                                                     repr( self.templateParameters ),
                                                     repr( self.name ),
                                                     repr( self.fields ),
                                                     repr( self.constructors ),
                                                     repr( self.destructor ),
                                                     repr( self.methods ),
                                                     repr( self.templateFunctions ),
                                                     repr( self.structs ),
                                                     repr( self.classes ),
                                                     repr( self.templateClasses ),
                                                     repr( self.typedefs ),
                                                     repr( self.enums ),
                                                     repr( self.unions ),
                                                     repr( self.access ) )

    def __str__( self ):
        res = super( ClassTemplateDef, self ).__str__( )

        tparams      = ', '.join( [ str( p ) for p in self.templateParameters ] )
        templateDef = 'template<{}>'.format( tparams )

        return templateDef + '\n' + res.replace( 'class', 'class/union/struct', 1 )


class Union( Struct ):
    """
        Represents a union definition.
        Exposes the following fields:
        - name
        - location
        - access (PUBLIC, PRIVATE, PROTECTED, None)
        - fields (dictionary of Field objects)
        - constructors (list of Constructor objects)
        - methods (dictionary of sets of Method objects)
        - structs (nested structs, dictionary of Struct objects)
        - classes (nested classes, dictionary of ClassDef objects)
        - typedefs (dictionary of typedef objects)
        - destructor (a Destructor object if present, None otherwise)
        - enums (dictionary of Enum objects)
        - unions (dictionary of Union objects)
        - templateFunctions (dictionary of sets of FunctionTemplateDefinition objects)
        - templateClasses (nested template classes, union or structs; dictionary of ClassTemplateDef objects)
    """

    def __repr__( self ):
        ret = super( Union, self ).__str__( )

        return ret.replace( 'Struct', 'Union', 1 )

    def __str__( self ):
        ret = super( Union, self ).__str__( )

        return ret.replace( 'struct', 'union', 1 )


class Namespace( DefinitionWithCursor ):
    """
        Represents a namespace
        Esposes the following properties and fields:
        - name
        - structs (nested structs, dictionary of Struct objects)
        - classes (nested classes, dictionary of ClassDef objects)
        - typedefs (dictionary of typedef objects)
        - destructor (a Destructor object if present, None otherwise)
        - enums (dictionary of Enum objects)
        - unions (dictionary of Union objects)
        - templateFunctions (dictionary of sets of FunctionTemplateDefinition objects)
        - templateClasses (dictionary of ClassTemplateDef objects)
        - namespaces (nested namespaces, dictionary of Namespace objects)
        - functions (dictionary of sets of FunctionDefinition objects)
        - variables (dictionary of Variable objects)
    """

    def __init__( self, cursor, addDefinitions=True ):
        """
            Create a Namespace instance from a clang namespace cursor.
        """
        super( Namespace, self ).__init__( cursor )

        self.defs = { }
        for key in [ 'functions', 'typedefs', 'enums', 'structs', 'classes', 'unions',
                     'variables', 'namespaces', 'templateClasses', 'templateFunctions' ]:
            self.defs[ key ] = { }

        if addDefinitions:
            self.addDefinitions( self._cursor )

    def addDefinitions( self, cursor ):
        """
            Extracts all the definitions from the libclang namespace cursor and adds them to the database
        """

        def getNamespace( cur ):
            if ( cur.semantic_parent and
                 cur.semantic_parent.kind in (cidx.CursorKind.NAMESPACE,
                                              cidx.CursorKind.TRANSLATION_UNIT ) ):
                curNamespaceHierarchy = getNamespaceHierarchy( cur )
                return self._getInnerNamespace( curNamespaceHierarchy )
            else:
                return None

        Any.requireIsNotNone( cursor )
        Any.require( cursor.kind in (cidx.CursorKind.NAMESPACE,
                                     cidx.CursorKind.TRANSLATION_UNIT,
                                     cidx.CursorKind.UNEXPOSED_DECL) )

        for c in cursor.get_children( ):
            ns = getNamespace( c )

            if c.kind == cidx.CursorKind.UNEXPOSED_DECL:
                self.addDefinitions( c )

            elif ns is not None:
                if c.kind == cidx.CursorKind.VAR_DECL:
                    self.variables[ c.spelling ] = Variable( c )

                elif c.kind in (cidx.CursorKind.FUNCTION_DECL, cidx.CursorKind.CXX_METHOD):
                    # function definition or prototype
                    if c.spelling not in ns.functions:
                        ns.functions[ c.spelling ] = set( )

                    # fset is the set of functions named as the one we are visiting now
                    fset = ns.functions[ c.spelling ]
                    _addDefinitionOrPrototype( c, fset, FunctionDefinition, FunctionPrototype )

                elif c.kind == cidx.CursorKind.STRUCT_DECL:
                    ns.structs[ c.spelling ] = Struct( c.get_definition( ) or c.canonical or c )

                elif c.kind == cidx.CursorKind.CLASS_DECL:
                    ns.classes[ c.spelling ] = ClassDef( c.get_definition( ) or c.canonical or c )

                elif c.kind == cidx.CursorKind.TYPEDEF_DECL:
                    ns.typedefs[ c.spelling ] = Typedef( c )

                elif c.kind == cidx.CursorKind.ENUM_DECL:
                    ns.enums[ c.spelling ] = Enum( c.get_definition() or c.canonical or c)

                elif c.kind == cidx.CursorKind.UNION_DECL:
                    ns.unions[ c.spelling ] = Union( c.get_definition() or c.canonical or c)

                elif c.kind == cidx.CursorKind.FUNCTION_TEMPLATE:
                    if c.spelling not in ns.templateFunctions:
                        ns.templateFunctions[ c.spelling ] = set( )

                    # fset is the set of functions named as the one we are visiting now
                    fset = ns.templateFunctions[ c.spelling ]
                    _addDefinitionOrPrototype( c, fset, TemplateFunctionDefinition,
                                               TemplateFunctionPrototype )

                elif c.kind == cidx.CursorKind.CLASS_TEMPLATE:
                    if c.spelling not in ns.templateClasses:
                        ns.templateClasses[ c.spelling ] = set( )
                    classTemplateDef =  ClassTemplateDef( c.get_definition() or c.canonical or c )
                    ns.templateClasses[ c.spelling ].add( classTemplateDef )

                elif c.kind == cidx.CursorKind.NAMESPACE:
                    cursorNamespaceHierarchy = getNamespaceHierarchy( c ) + [ c.spelling ]
                    try:
                        ns = self._getInnerNamespace( cursorNamespaceHierarchy )
                        ns.addDefinitions( c )
                    except (ValueError, KeyError):
                        ns = Namespace( c )
                        self.namespaces[ c.spelling ] = ns


    @property
    def hierarchy( self ):
        """
            Returns the namespace hierarchy including this namespace
        """
        return self.namespaceHierarchy + [ self.name ]

    @property
    def fullName( self ):
        """
            Returns the full name of this namespace
        """
        return '::'.join( self.hierarchy )

    def _getInnerNamespaceHierarchy( self, other ):
        pref = other[ :len( self.hierarchy ) ]
        if pref != self.hierarchy:
            raise ValueError( 'the argument is not a child namespace of self' )
        return other[ len( self.hierarchy ): ]

    def _getInnerNamespace( self, other ):
        innerHierarchy = self._getInnerNamespaceHierarchy( other )

        ns = self
        for nsname in innerHierarchy:
            ns = ns.namespaces[ nsname ]

        return ns

    def __repr__( self ):
        return 'Namespace({}, {})'.format( repr( self.name ), repr( self.defs ) )

    # builds a string representation of the namespace members
    def _membersStr( self ):
        functions = itertools.chain( *self.functions.values( ) )
        tfuncs    = itertools.chain( *self.templateFunctions.values( ) )
        tclasses  = itertools.chain( *self.templateClasses.values( ) )

        stuff     = itertools.chain( self.enums.values( ),
                                     self.typedefs.values( ),
                                     self.structs.values( ),
                                     self.classes.values( ),
                                     self.unions.values( ),
                                     tclasses,
                                     self.variables.values( ),
                                     functions,
                                     tfuncs,
                                     self.namespaces.values( ) )
        return '\n'.join( [ str( x ) + ';' for x in stuff ] )

    def __str__( self ):

        def indent( s ):
            lines = [ '\t' + l for l in s.split( '\n' ) ]
            return '\n'.join( lines )

        return 'namespace {} {{\n{}\n}}'.format( self.name,
                                                 indent( self._membersStr( ) ) )

    def _locals( self, dic, filepath ):
        res = { }
        for k, v in dic.items( ):
            if isinstance( v, set ):
                vset = set( )
                for e in v:
                    if e.location[ 0 ] == filepath:
                        vset.add( e )
                if vset:
                    res[ k ] = vset
            else:
                if v.location[ 0 ] == filepath:
                    res[ k ] = v
        return res

    @property
    def functions( self ):
        return self.defs[ 'functions' ]

    @property
    def templateFunctions( self ):
        return self.defs[ 'templateFunctions' ]

    @property
    def variables( self ):
        return self.defs[ 'variables' ]

    @property
    def typedefs( self ):
        return self.defs[ 'typedefs' ]

    @property
    def enums( self ):
        return self.defs[ 'enums' ]

    @property
    def structs( self ):
        return self.defs[ 'structs' ]

    @property
    def classes( self ):
        return self.defs[ 'classes' ]

    @property
    def templateClasses( self ):
        return self.defs[ 'templateClasses' ]

    @property
    def unions( self ):
        return self.defs[ 'unions' ]

    @property
    def namespaces( self ):
        return self.defs[ 'namespaces' ]

    def _localNamespaces( self, filepath ):
        localnss = { }
        for name, ns in self.namespaces.items( ):
            lns = ns.getLocals( filepath )
            if not lns.isEmpty():
                localnss[ name ] = lns
        return localnss

    def isEmpty( self ):
        return not ( self.variables or self.functions or self.templateFunctions or
                     self.variables or self.typedefs or self.enums or self.structs or
                     self.classes or self.templateClasses or self.unions or self.namespaces )

    def getLocals( self, filepath ):
        ns = Namespace( self._cursor, addDefinitions=False )

        ns.defs[ 'functions' ]          = self._locals( self.functions, filepath )
        ns.defs[ 'templateFunctions' ] = self._locals( self.templateFunctions, filepath )
        ns.defs[ 'variables' ]          = self._locals( self.variables, filepath )
        ns.defs[ 'typedefs' ]           = self._locals( self.typedefs, filepath )
        ns.defs[ 'enums' ]              = self._locals( self.enums, filepath )
        ns.defs[ 'structs' ]            = self._locals( self.structs, filepath )
        ns.defs[ 'classes' ]            = self._locals( self.classes, filepath )
        ns.defs[ 'templateClasses' ]   = self._locals( self.templateClasses, filepath )
        ns.defs[ 'unions' ]             = self._locals( self.unions, filepath )
        ns.defs[ 'namespaces' ]         = self._localNamespaces( filepath )

        return ns
# EOF
