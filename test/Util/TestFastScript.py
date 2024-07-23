#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  launches the unit testing
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


import collections.abc
import unittest

from ToolBOSCore.Util import FastScript


class TestArgManagerV2( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            FastScript.setDebugLevel( 1 )


    def test_flatten_simple(self):
        inData   = [ 'sit://External/msinttypes/1.0',
                     'sit://External/pthreads4w/1.0',
                     'sit://External/cutest/1.5' ]

        expected = [ 'sit://External/msinttypes/1.0',
                     'sit://External/pthreads4w/1.0',
                     'sit://External/cutest/1.5' ]

        resultList     = FastScript.flattenList( inData )
        resultIterator = FastScript.flatten( inData )

        self.assertListEqual( resultList, expected )
        self.assertIsInstance( resultIterator, collections.abc.Iterator )


    def test_flatten_nested(self):
        inData = [ 'sit://Libraries/ToolBOSLib/4.0',
                   [ 'sit://External/msinttypes/1.0',
                     'sit://External/pthreads4w/1.0',
                     'sit://External/cutest/1.5' ],
                   'sit://Libraries/BPLLight/1.1',
                   [ 'deb://libfftw3-bin' ],
                   'sit://External/libxml2/2.6' ]

        expected = [ 'sit://Libraries/ToolBOSLib/4.0',
                     'sit://External/msinttypes/1.0',
                     'sit://External/pthreads4w/1.0',
                     'sit://External/cutest/1.5',
                     'sit://Libraries/BPLLight/1.1',
                     'deb://libfftw3-bin',
                     'sit://External/libxml2/2.6' ]


        resultList     = FastScript.flattenList( inData )
        resultIterator = FastScript.flatten( inData )

        self.assertListEqual( resultList, expected )
        self.assertIsInstance( resultIterator, collections.abc.Iterator )


if __name__ == '__main__':
    unittest.main()


# EOF
