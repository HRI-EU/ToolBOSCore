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


import unittest

from six import StringIO

from ToolBOSCore.Util import Any, FastScript


class TestExecInAllProjects( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_execInAllProjects( self ):
        cmd    = 'ExecInAllProjects.py "cat hello.txt"'
        output = StringIO()


        # run ExecInAllProjects.py
        FastScript.execProgram( cmd, stdout=output, stderr=output )


        # check result
        returned = output.getvalue()

        self.assertTrue( returned.find( 'Hello from "HelloWorld/1.0"' ) > 0 )
        self.assertTrue( returned.find( 'Hello from "HelloWorld/1.1"' ) > 0 )
        self.assertTrue( returned.find( 'Hello from "HelloWorld/1.2"' ) > 0 )
        self.assertTrue( returned.find( 'Hello from "Spam/42.0"'      ) > 0 )


if __name__ == '__main__':
    unittest.main()


# EOF
