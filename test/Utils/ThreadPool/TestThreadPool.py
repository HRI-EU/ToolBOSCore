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


import logging
import unittest

from ToolBOSCore.Util import Any, FastScript, ThreadPool


class TestThreadPool( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )


    def test_main(self):
        tp = ThreadPool.ThreadPool()

        tp.add( self._printA )
        tp.add( self._printB )
        tp.add( self._printC )

        tp.run()


    def _printA( self ):
        i = 0

        while i < 1000:
            logging.info( 'A' )
            i += 1


    def _printB( self ):
        i = 0

        while i < 1000:
            logging.info( 'B' )
            i += 1


    def _printC( self ):
        i = 0

        while i < 1000:
            logging.info( 'C' )
            i += 1


if __name__ == '__main__':
    unittest.main()


# EOF
