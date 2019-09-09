#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Imports the right modules depending on Python 2.x / 3.x
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


#----------------------------------------------------------------------------
# Includes
#----------------------------------------------------------------------------


import sys
import unittest
import six
import base64
from ToolBOSCore.Util import Any

if six.PY2:
    from StringIO import StringIO

    from urlparse import urlparse
    from urlparse import urlsplit
    from urlparse import urlunsplit
else:
    from io import StringIO

    from urllib.parse import urlparse
    from urllib.parse import urlsplit
    from urllib.parse import urlunsplit


if six.PY2:
    STDIN_BIN = sys.stdin
else:
    STDIN_BIN = sys.stdin.buffer

def getInput( prompt ):
    if sys.version[0] == '2':
        return raw_input( prompt )
    else:
        return input( prompt )


class TestCaseCompat( unittest.TestCase ):
    """
        A subclass of unittest.TestCase that provides a compatibility layer for
        different python versions.
    """
    # noinspection PyCompatibility
    def assertIsInstance( self, obj, cls, msg=None ):
        """
           Python 3.0/3.1 compatibility wrapper for TestCase#assertIsInstance
        """
        if sys.version_info.major == 3 and sys.version_info.minor in (0, 1):
            self.assertTrue( isinstance( obj, cls ),
                             '%s is not an instance of %r' % (repr( obj ), cls) )
        else:
            super(TestCaseCompat, self).assertIsInstance( obj, cls, msg )

    def assertIn( self, member, container ):
        """
           Python 2.6 compatibility wrapper for TestCase#assertIn
        """
        if sys.version_info.major == 2 and sys.version_info.minor == 6:
            self.assertTrue( member in container,
                             '%s not found in %s' % (repr( member ), repr( container )) )
        else:
            super( TestCaseCompat, self ).assertIn( member, container )

    def assertLineWiseEqual( self, input1, input2, removeIndent=False, collapseInternalWhitespace=False ):

        def _applyWhitespaceChanges( text ):
            retval = text.strip().split( '\n' )

            if collapseInternalWhitespace:
                retval = [ e.replace(r'\s+', ' ') for e in retval ]

            if removeIndent:
                retval = [ e.strip() for e in retval ]

            return retval

        _input1 = _applyWhitespaceChanges( input1 )
        _input2 = _applyWhitespaceChanges( input2 )

        self.assertEqual( _input1, _input2 )


# noinspection PyCompatibility
def base64encode( text ):
    """
        Compatibility wrapper around base64 encoding.
    """
    if Any.isUnicode( text ):
        encoded = text.encode( 'utf8' )
    else:
        encoded = text

    if six.PY2:
        # pylint: disable=deprecated-method
        base64bytes = base64.encodestring( encoded )
    else:
        base64bytes = base64.encodebytes( encoded )

    return base64bytes.decode('utf8').strip()




# EOF
