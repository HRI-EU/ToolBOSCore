# -*- coding: utf-8 -*-
#
#  Programmatically create a copyright header for source files
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


def getCopyright( lang=None ):
    """
        Returns copyright information of this package.

        'lang' must be either None, "bash" or "python"

        This function just returns the lines of the copyright notice,
        no leading or trailing '#' lines. Use getCopyrightHeader()
        when generating code files.
    """
    lines = ( 'Copyright (C)',
              'Honda Research Institute Europe GmbH',
              'Carl-Legien-Str. 30',
              '63073 Offenbach/Main',
              'Germany',
              '',
              'UNPUBLISHED PROPRIETARY MATERIAL.',
              'ALL RIGHTS RESERVED.' )


    if lang == 'bash' or lang == 'python':
        text = ''

        for line in lines:
            if line:
                text += '#  %s\n' % line
            else:
                text += '#\n'
    else:
        text = '\n'.join( lines )

    return text


def getCopyrightHeader( lang, description ):
    """
        Returns a full-featured copyright header, including shebang,
        description, and two trailing newlines.
    """
    if lang == 'bash':
        shebang = '#!/bin/bash'
    elif lang == 'python':
        shebang = '#!/usr/bin/env python\n# -*- coding: utf-8 -*-'
    else:
        return ValueError( "invalid argument for parameter 'lang'" )

    c      = getCopyright( lang )        # already contains trailing '#'
    result = '''%s
#
#  %s
#
%s#\n#\n\n\n''' % ( shebang, description, c )

    return result


# EOF
