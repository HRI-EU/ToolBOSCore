#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  run pylint on given file and get code issues
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


from typing import Type

from ToolBOSCore.Util import Any, FastScript

FastScript.tryImport( 'pylint' )
from pylint.lint import Run as linter


def getPylintResult( file: str, pylintConf: str ) -> linter:
    """
        invokes pylint programmatically and returns instance of pylint.lint.Run class

        Args:
            file      : path to the python file
            pylintConf: pylint configuration file,
                        Default: $TOOLBOSCORE_ROOT/etc/pyproject.toml
                        user can configure path to this file via pkgInfo.py as:
                        'pylintConf' = 'path/to/pyproject.toml/file'
        Returns:
            pylintResult: instance of pylint.lint.Run class
    """
    Any.requireIsTextNonEmpty( file )
    Any.requireIsTextNonEmpty( pylintConf )

    # Somewhere between pylint 2.4 and 2.9 an 'exit'-argument was added.
    #
    # Adding this try-block for Python 2.7 (pylint 2.4.4).
    # Without exit=False pylint terminates the Python process!
    try:
        pylintResult = linter( args=[ file, '--rcfile=' + pylintConf ], exit=False )
    except TypeError:
        raise EnvironmentError( 'pylint 2.9 or higher is required' )

    return pylintResult


def getTotalPylintIssues( pylintResult: linter  ) -> int:
    """
        takes instance of pylint.lint.Run class as input and returns
        number of code issues found by the pylint

        Args:
            pylintResult: instance of pylint.lint.Run class
        Returns:
            codeIssues: number of code issues found by pylint for a given file
    """

    Any.requireIsInstance( pylintResult, linter )

    pylintStats = pylintResult.linter.stats

    # pylint >= 2.12, PyLinter.stats has been changed from dict to class
    # To support the backward compatability, check type and access the lint stats.

    if isinstance( pylintStats, dict ):
        codeIssues  = pylintStats[ 'error' ] + pylintStats[ 'warning' ]
    else:
        codeIssues  = pylintStats.error + pylintStats.warning

    return codeIssues


# EOF
