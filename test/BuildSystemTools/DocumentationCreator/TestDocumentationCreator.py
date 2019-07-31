#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  launches the unit testing
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


import os
import tempfile
import unittest

from six  import StringIO

from ToolBOSCore.BuildSystem.DocumentationCreator import DocumentationCreator
from ToolBOSCore.Packages.PackageCreator        import PackageCreator_C_Library
from ToolBOSCore.Util                             import FastScript
from ToolBOSCore.Util                             import Any



class TestDocumentationCreator( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_makeDocumentation( self ):
        tmpDir         = tempfile.mkdtemp( prefix='test-' )
        packageName    = 'HelloWorld'
        packageVersion = '42.0'
        projectRoot    = os.path.join( tmpDir, packageName, packageVersion )


        # create package on-the-fly
        PackageCreator_C_Library( packageName, packageVersion,
                                  outputDir=tmpDir ).run()

        Any.requireIsDirNonEmpty( tmpDir )

        # create docu
        output = StringIO() if Any.getDebugLevel() <= 3 else None
        d = DocumentationCreator( projectRoot, stdout=output, stderr=output )
        d.generate()


        # check result
        Any.requireIsDirNonEmpty(  os.path.join( projectRoot, 'doc' ) )
        Any.requireIsDirNonEmpty(  os.path.join( projectRoot, 'doc/html' ) )
        Any.requireIsFileNonEmpty( os.path.join( projectRoot, 'doc/html/index.html' ) )
        Any.requireIsFileNonEmpty( os.path.join( projectRoot, 'doc/html/doxygen.css' ) )
        Any.requireIsFileNonEmpty( os.path.join( projectRoot, 'doc/html/doxygen.png' ) )

        FastScript.remove( tmpDir )


if __name__ == '__main__':
    unittest.main()


# EOF
