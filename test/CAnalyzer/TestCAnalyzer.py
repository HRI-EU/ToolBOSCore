#!/usr/bin/env python
# encoding: utf-8
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
# Regression test for CAnalyzer

import itertools
import sys
import unittest

from ToolBOSCore.SoftwareQuality.CAnalyzer import CParser
from ToolBOSCore.Util.CAnalyzerElements import Enum, Field, FunctionDefinition, FunctionPrototype, MacroDefinition, \
    MacroFnDefinition, Struct, TemplateFunctionDefinition, TemplateParameter, Typedef, Variable, Namespace


class TestCAnalyzer( unittest.TestCase ):
    def assertNotEmpty( self, collection ):
        self.assertTrue( collection, '{} is empty'.format( repr( collection ) ) )

    def assertEmpty( self, collection ):
        self.assertFalse( collection, '{} is not empty'.format( repr( collection ) ) )

    # noinspection PyCompatibility
    def assertIsInstanceCompat( self, obj, cls ):
        """
           Python 3.0/3.1 compatibility wrapper for TestCase#assertIsInstance
        """
        if sys.version_info.major == 3 and sys.version_info.minor in (0, 1):
            self.assertTrue( isinstance( obj, cls ), '%s is not an instance of %r' % (repr( obj ), cls) )
        else:
            self.assertIsInstance( obj, cls )

    def setUp( self ):
        from ToolBOSCore.BuildSystem.Compilers import getIncludePaths
        includePaths      = getIncludePaths( 'clang', 'c++' ) or getIncludePaths( 'clang-3.8', 'c++' )
        includeDirectives = [ '-I' + ip for ip in includePaths ]
        self.parser       = CParser( 'test_canalyzer.cpp', langStd='c++11',
                                     verbose=True, isCPlusPlus=True,
                                     args=includeDirectives + [ '-xc++', '-std=c++11' ] )

    def test_variables( self ):
        self.assertIn( 'var1', self.parser.variables )
        var = self.parser.variables[ 'var1' ]
        self.assertIsInstanceCompat( var, Variable )
        self.assertEqual( var.name, 'var1' )
        self.assertEqual( var.type, 'int' )
        self.assertNotIn( '__var__', self.parser.variables )
        self.assertNotIn( 'foo', self.parser.variables )

    def test_function_foo( self ):
        self.assertIn( 'foo', self.parser.functions )
        self.assertNotIn( 'var1', self.parser.functions )

        fset = self.parser.functions[ 'foo' ]
        self.assertNotEmpty( fset )
        self.assertEqual( len( fset ), 1 )

        # function parameters
        fun = list( fset )[ 0 ]
        self.assertIsInstanceCompat( fun, FunctionDefinition )
        self.assertEqual( fun.name, 'foo' )
        self.assertNotEmpty( fun.params )
        self.assertEqual( len( fun.params ), 1 )
        param = fun.params[ 0 ]
        self.assertEqual( param.name, 'x' )
        self.assertEqual( param.type, 'int' )
        self.assertEqual( fun.returnType, 'int' )

        # function prototypes
        self.assertEqual( len( fun.prototypes ), 1 )
        proto = fun.prototypes[ 0 ]
        self.assertIsInstanceCompat( proto, FunctionPrototype )
        self.assertEqual( proto.name, 'foo' )
        self.assertEqual( proto.returnType, 'int' )
        self.assertEqual( len( proto.params ), 1 )
        self.assertEqual( proto.params[ 0 ].name, '' )
        self.assertEqual( proto.params[ 0 ].type, 'int' )

        # variadic
        self.assertFalse( fun.isVariadic )

    def test_function_bar( self ):
        self.assertIn( 'bar', self.parser.functions )

        fset = self.parser.functions[ 'bar' ]
        self.assertNotEmpty( fset )
        self.assertEqual( len( fset ), 2 )

        f1 = None
        f2 = None
        for f in fset:
            if len( f.params ) == 1:
                f1 = f
            elif len( f.params ) == 2:
                f2 = f

        self.assertIsNotNone( f1 )
        self.assertIsNotNone( f2 )

        self.assertFalse( f1.isVariadic )
        self.assertFalse( f2.isVariadic )

        # function parameters
        self.assertIsInstanceCompat( f1, FunctionDefinition )
        self.assertEqual( f1.name, 'bar' )
        self.assertNotEmpty( f1.params )
        f1_param_1 = f1.params[ 0 ]
        self.assertEqual( f1_param_1.name, 'baz' )
        self.assertEqual( f1_param_1.type, 'float' )
        self.assertEqual( f1.returnType, 'float' )

        # function prototypes
        self.assertEqual( len( f1.prototypes ), 3 )
        proto1 = f1.prototypes[ 0 ]
        self.assertIsInstanceCompat( proto1, FunctionPrototype )
        self.assertEqual( proto1.name, 'bar' )
        self.assertEqual( proto1.returnType, 'float' )
        self.assertEqual( len( proto1.params ), 1 )
        self.assertEqual( proto1.params[ 0 ].name, '' )
        self.assertEqual( proto1.params[ 0 ].type, 'float' )

        proto2 = f1.prototypes[ 1 ]
        self.assertIsInstanceCompat( proto2, FunctionPrototype )
        self.assertEqual( proto2.name, 'bar' )
        self.assertEqual( proto2.returnType, 'float' )
        self.assertEqual( len( proto2.params ), 1 )
        self.assertEqual( proto2.params[ 0 ].name, 'moo' )
        self.assertEqual( proto2.params[ 0 ].type, 'float' )

        proto3 = f1.prototypes[ 2 ]
        self.assertIsInstanceCompat( proto3, FunctionPrototype )
        self.assertEqual( proto3.name, 'bar' )
        self.assertEqual( proto3.returnType, 'float' )
        self.assertEqual( len( proto3.params ), 1 )
        self.assertEqual( proto3.params[ 0 ].name, 'myparam' )
        self.assertEqual( proto3.params[ 0 ].type, 'myfloat' )

    def test_function_variadicfn( self ):
        self.assertIn( 'variadicfn', self.parser.functions )
        self.assertNotIn( 'var1', self.parser.functions )

        fset = self.parser.functions[ 'variadicfn' ]
        self.assertNotEmpty( fset )
        self.assertEqual( len( fset ), 1 )

        # function parameters
        fun = list( fset )[ 0 ]
        self.assertIsInstanceCompat( fun, FunctionDefinition )
        self.assertEqual( fun.name, 'variadicfn' )
        self.assertNotEmpty( fun.params )
        self.assertEqual( len( fun.params ), 1 )
        param = fun.params[ 0 ]
        self.assertEqual( param.name, 'firstparam' )
        self.assertEqual( param.type, 'int' )
        self.assertEqual( fun.returnType, 'void' )

        # prototypes
        self.assertEmpty( fun.prototypes )

        # variadic
        self.assertTrue( fun.isVariadic )

    def test_typedef_myfloat( self ):
        typename = 'myfloat'
        self.assertIn( typename, self.parser.typedefs )
        myfloat = self.parser.typedefs[ typename ]
        self.assertIsInstanceCompat( myfloat, Typedef )
        self.assertEqual( myfloat.name, typename )
        self.assertEqual( myfloat.type, 'float' )

    def test_typedef_intptr( self ):
        typename = 'intptr'
        self.assertIn( typename, self.parser.typedefs )
        intptr = self.parser.typedefs[ typename ]
        self.assertIsInstanceCompat( intptr, Typedef )
        self.assertEqual( intptr.name, typename )
        self.assertIn( intptr.type, ('const int*', 'const int *') )

    def test_macro_MYMACRO( self ):
        macroname = 'MYMACRO'
        self.assertIn( macroname, self.parser.macros )
        self.assertNotIn( macroname, self.parser.fnmacros )

        mymacro = self.parser.macros[ macroname ]
        self.assertIsInstanceCompat( mymacro, MacroDefinition )
        self.assertEqual( mymacro.name, macroname )
        self.assertEqual( mymacro.body, 'extern "C" {' )

    def test_macrofn_MYMACROFN( self ):
        macroname = 'MYMACROFN'
        self.assertIn( macroname, self.parser.fnmacros )
        self.assertNotIn( macroname, self.parser.macros )

        mymacrofn = self.parser.fnmacros[ macroname ]
        self.assertIsInstanceCompat( mymacrofn, MacroFnDefinition )
        self.assertEqual( mymacrofn.name, macroname )
        self.assertEqual( mymacrofn.body, '(__x + __y)' )

        params = mymacrofn.params
        self.assertNotEmpty( params )
        self.assertEqual( len( params ), 2 )

        self.assertEqual( params[ 0 ], '__x' )
        self.assertEqual( params[ 1 ], '__y' )

    def test_enum_MyEnum( self ):
        enumname = 'MyEnum'
        self.assertIn( enumname, self.parser.enums )

        myenum = self.parser.enums[ enumname ]
        self.assertIsInstanceCompat( myenum, Enum )
        self.assertEqual( myenum.name, enumname )
        self.assertNotEmpty( myenum.values )
        self.assertEqual( len( myenum.values ), 3 )
        self.assertIn( 'Value1', myenum.values )
        self.assertIn( 'Value2', myenum.values )
        self.assertIn( 'Value3', myenum.values )

    def test_templatefn_adder( self ):
        fn_name = 'adder'
        self.assertIn( fn_name, self.parser.templateFunctions )

        fset = self.parser.templateFunctions[ fn_name ]
        self.assertNotEmpty( fset )
        self.assertEqual( len( fset ), 1 )

        # function parameters
        fun = list( fset )[ 0 ]
        self.assertIsInstanceCompat( fun, TemplateFunctionDefinition )
        self.assertEqual( fun.name, fn_name )
        self.assertNotEmpty( fun.params )
        self.assertEqual( len( fun.params ), 1 )
        param = fun.params[ 0 ]
        self.assertEqual( param.name, 'y' )
        self.assertEqual( param.type, 'T' )
        self.assertEqual( fun.returnType, 'T' )

        # template parameters
        self.assertNotEmpty( fun.templateParameters )
        self.assertEqual( len( fun.templateParameters ), 2 )

        tp1, tp2 = fun.templateParameters
        self.assertIsInstanceCompat( tp1, TemplateParameter )
        self.assertIsInstanceCompat( tp2, TemplateParameter )
        self.assertEqual( tp1.name, 'T' )
        self.assertEqual( tp2.name, 'X' )
        self.assertEqual( tp1.type, 'typename' )
        self.assertEqual( tp2.type, 'int' )

    def test_templatefn_coerce( self ):
        fn_name = 'coerce'
        self.assertIn( fn_name, self.parser.templateFunctions )

        fset = self.parser.templateFunctions[ fn_name ]
        self.assertNotEmpty( fset )
        self.assertEqual( len( fset ), 1 )

        # function parameters
        fun = list( fset )[ 0 ]
        self.assertIsInstanceCompat( fun, TemplateFunctionDefinition )
        self.assertEqual( fun.name, fn_name )
        self.assertNotEmpty( fun.params )
        self.assertEqual( len( fun.params ), 1 )
        param = fun.params[ 0 ]
        self.assertEqual( param.name, 'param' )
        self.assertEqual( param.type, 'T2' )
        self.assertEqual( fun.returnType, 'T1' )

        # template parameters
        self.assertNotEmpty( fun.templateParameters )
        self.assertEqual( len( fun.templateParameters ), 2 )

        tp1, tp2 = fun.templateParameters
        self.assertIsInstanceCompat( tp1, TemplateParameter )
        self.assertIsInstanceCompat( tp2, TemplateParameter )
        self.assertEqual( tp1.name, 'T1' )
        self.assertEqual( tp2.name, 'T2' )
        self.assertEqual( tp1.type, 'typename' )
        self.assertEqual( tp2.type, 'typename' )

    def field_test_helper( self, struct, fieldname, fieldtype, access ):
        self.assertIn( fieldname, struct.fields )
        field = struct.fields[ fieldname ]
        self.assertIsInstanceCompat( field, Field )
        self.assertEqual( field.name, fieldname )
        self.assertEqual( field.type, fieldtype )
        self.assertEqual( field.access, access )

    def constructor_test_helper( self, struct, ctor, params, access ):
        self.assertEqual( struct.name, ctor.name )
        self.assertEqual( ctor.access, access )
        for expected, actual in itertools.izip( params, ctor.params ):
            self.assertEqual( expected[ 0 ], actual.name )
            self.assertEqual( expected[ 1 ], actual.type )

    def method_test_helper( self, struct, methodname, params, returnType, access ):
        def matches( method ):
            if method.name == methodname and method.access == access and method.returnType == returnType:
                for expected, actual in itertools.izip( params, method.params ):
                    if expected[ 0 ] != actual.name or expected[ 1 ] != actual.type:
                        return False
                return True
            else:
                return False

        self.assertIn( methodname, struct.methods )
        mset = struct.methods[ methodname ]
        found = False
        for m in mset:
            if matches( m ):
                found = True

        self.assertTrue( found, 'No method matching {} {} {}({}) found.'.format( access,
                                                                                 returnType,
                                                                                 methodname,
                                                                                 ', '.join( map( str, params ) )
                                                                                 ) )

    def template_method_test_helper( self, struct, methodname, template_params, params, returnType, access ):
        def matches( method ):
            if method.name == methodname and method.access == access and method.returnType == returnType:
                for expected, actual in itertools.izip( params, method.params ):
                    if expected[ 0 ] != actual.name or expected[ 1 ] != actual.type:
                        return False
                for expected, actual in itertools.izip( template_params, method.templateParameters ):
                    if expected[ 0 ] != actual.name or expected[ 1 ] != actual.type:
                        return False
                return True
            else:
                return False

        self.assertIn( methodname, struct.templateFunctions )
        mset = struct.templateFunctions[ methodname ]
        found = False
        for m in mset:
            if matches( m ):
                found = True

        self.assertTrue( found, 'No method matching {} template<{}> {} {}({}) found.'.format( access,
                                                                                              template_params,
                                                                                              returnType,
                                                                                              methodname,
                                                                                              ', '.join(
                                                                                                  map( str, params ) )
                                                                                              ) )

    def test_struct_MyStruct( self ):
        structname = 'MyStruct'
        self.assertIn( structname, self.parser.structs )

        struct = self.parser.structs[ structname ]

        self.assertIsInstanceCompat( struct, Struct )
        self.assertEqual( struct.name, structname )
        self.assertEqual( struct.access, None )

        # fields
        self.assertNotEmpty( struct.fields )
        self.assertEqual( len( struct.fields ), 3 )
        self.field_test_helper( struct, 'foo', 'int', 'PRIVATE' )
        self.field_test_helper( struct, 'bar', 'float', 'PUBLIC' )
        self.field_test_helper( struct, 'baz', 'bool', 'PROTECTED' )

        # Constructors
        self.assertNotEmpty( struct.constructors )
        self.assertEqual( len( struct.constructors ), 2 )
        self.constructor_test_helper( struct, struct.constructors[ 0 ], [ ('x', 'int') ], 'PROTECTED' )
        self.constructor_test_helper( struct, struct.constructors[ 1 ], [ ('x', 'int'), ('y', 'float') ], 'PUBLIC' )

        # Methods
        self.assertNotEmpty( struct.methods )
        self.assertEqual( len( struct.methods ), 3 )
        self.method_test_helper( struct, 'print', [ ('message', 'char *') ], 'void', 'PUBLIC' )
        self.method_test_helper( struct, 'isBaz', [ ], 'bool', 'PROTECTED' )
        self.method_test_helper( struct, 'getFoo', [ ], 'int', 'PUBLIC' );

        # Template methods
        self.template_method_test_helper( struct, 'coerceFoo', [ ('T', 'typename') ], [ ], 'T', 'PUBLIC' )
        self.template_method_test_helper( struct, 'fooplussomething', [ ('N', 'int') ], [ ], 'int', 'PRIVATE' )

        # TODO: structs, classes, unions, enums, template structs, template classes, template unions

    def test_namespace(self):
        nsname = 'ns1'
        self.assertIn(nsname, self.parser.namespaces)

        ns = self.parser.namespaces[nsname]

        self.assertIsInstanceCompat(ns, Namespace)
        self.assertEqual(ns.name, nsname)

        self.assertIn( 'foo', ns.variables)
        self.assertEquals(ns.variables['foo'].type, 'float')

        self.assertIn( 'mystruct', ns.structs)

        self.assertIn( 'myclass', ns.classes)

        self.assertIn( 'myunion', ns.unions)

        self.assertIn( 'mytypedef', ns.typedefs)

        self.assertIn( 'myfunction', ns.functions)

        self.assertIn( 'mytemplatefunction', ns.templateFunctions)

        self.assertIn( 'mytemplateclass', ns.templateClasses)

        self.assertIn( 'ns2', ns.namespaces)

        self.assertNotIn('ns2fn', ns.functions)

        ns2 = ns.namespaces['ns2']

        self.assertIn( 'foo', ns2.variables)
        self.assertEquals(ns2.variables['foo'].type, 'float')

        self.assertIn( 'mystruct', ns2.structs)

        self.assertIn( 'myclass', ns2.classes)

        self.assertIn( 'myunion', ns2.unions)

        self.assertIn( 'mytypedef', ns2.typedefs)

        self.assertIn( 'myfunction', ns2.functions)

        self.assertIn( 'mytemplatefunction', ns2.templateFunctions)

        self.assertIn( 'mytemplateclass', ns2.templateClasses)

        self.assertIn('ns2fn', ns2.functions)

if __name__ == '__main__':
    unittest.main( )

# EOF
