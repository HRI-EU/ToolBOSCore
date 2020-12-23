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


import logging

from ToolBOSCore.Util import Any


def getDefaultLanguageStandard( platform ):
    """
        Returns a dictionary that contains the default -std switch for the compiler
        used to build the package.
    """
    compilers = _getCompilers( platform )
    if compilers is not None:
        return {
            'c'  : _getCCompilerDefaultStd( compilers[ 'c' ] ) or 'c99',
            'c++': _getCPPCompilerDefaultStd( compilers[ 'c++' ] ) or 'c++11'
        }
    else:
        logging.warning('Cannot detect the compilers used to build the project.')
        logging.warning('Try rebuilding your project with')
        logging.warning('   $ BST.py -db')
        logging.warning('Defaulting to "-std=c99" for C, "-std=c++0x" for C++.')
        return {
            'c'  : 'c99',
            'c++': 'c++0x'
        }


# this function parses the make files to get the currently used compiler
def _getCompilers( platform ):
    """
        Get currently used C and C++ compilers.
    """
    from ToolBOSCore.Util.FastScript import getFileContent

    compilersTxtPath = 'build/{}/compilers.txt'.format( platform )

    if Any.isFile( compilersTxtPath ) and Any.isFileNonEmpty( compilersTxtPath ):
        content                = getFileContent( compilersTxtPath )
        cCompiler, cxxCompiler = content.split( '::' )

        return { 'c': cCompiler.strip( ), 'c++': cxxCompiler.strip( ) }
    else:
        return None


def _preprocessString( compiler, string, lang ):
    """
        Preprocess a string with the given compiler.
    """
    import io

    from subprocess import CalledProcessError
    from ToolBOSCore.Util.FastScript import execProgram

    inp = io.StringIO( string )
    out = io.StringIO( )

    try:
        execProgram( '{} -x{} -E -'.format( compiler, lang ),
                     stdin=inp,
                     stdout=out )

        return out.getvalue( )
    except CalledProcessError as e:
        logging.error( 'Unable to run the preprocessor: %s.', e )

    return None


def _getCCompilerDefaultStd( compiler ):
    """
        Gets the default -std switch for the C language used by the given
        compiler.
    """
    output = _preprocessString( compiler, '__STDC_VERSION__\n__STRICT_ANSI__', 'c' )
    if output is not None:
        lines = [ l for l in output.split( '\n' ) if l ]

        if len( lines ) >= 2:
            lines      = lines[ -2: ]
            version    = lines[ 0 ]
            strictAnsi = lines[ 1 ]

            return _decodeCStd( version, strictAnsi )

    logging.error( 'Cannot get default C language standard.' )
    return None


def _getCPPCompilerDefaultStd( compiler ):
    """
        Gets the default -std switch for the C++ language used by the given
        compiler.
    """
    output = _preprocessString( compiler, '__cplusplus\n__STRICT_ANSI__', 'c++' )
    if output is not None:
        lines = [ l for l in output.split( '\n' ) if l ]

        if len( lines ) >= 2:
            lines      = lines[ -2: ]
            version    = lines[ 0 ]
            strictAnsi = lines[ 1 ]
            return _decodeCPPStd( version, strictAnsi )

    logging.error( 'Cannot get default C++ language standard.' )
    return None


def _decodeCStd( version, strictAnsi ):
    """
        Decodes the C standard given the values of the macros
        __STDC_VERSION__ and __STRICT_ANSI__
    """
    retVal = None

    if version == '__STDC_VERSION__' and strictAnsi == '1':
        retVal = 'c90'

    elif version == '199409L' and strictAnsi == '1':
        retVal = 'iso9899:199409'

    elif version == '199901L' and strictAnsi == '1':
        retVal = 'c99'

    elif version == '201112L' and strictAnsi == '1':
        retVal = 'c11'

    elif version == '__STDC_VERSION__' and strictAnsi == '__STRICT_ANSI__':
        retVal = 'gnu90'

    elif version == '199901L' and strictAnsi == '__STRICT_ANSI__':
        retVal = 'gnu99'

    elif version == '201112L' and strictAnsi == '__STRICT_ANSI__':
        retVal = 'gnu11'

    elif version == '201710L' and strictAnsi == '__STRICT_ANSI__':
        retVal = 'gnu17'

    else:
        logging.warning( 'Cannot decode default language standard for C. (__STDC_VERSION__ = %s __STRICT_ANSI__ = %s)',
                         version, strictAnsi )

    return retVal


def _decodeCPPStd( version, strictAnsi ):
    """
        Decodes the C standard given the values of the macros
        __cplusplus and __STRICT_ANSI__
    """
    retVal = None

    if version == '199711L' and strictAnsi == '1':
        retVal = 'c++03'

    elif version == '199711L' and strictAnsi == '__STRICT_ANSI__':
        retVal = 'gnu++03'

    elif version == '201103L' and strictAnsi == '1':
        retVal = 'c++11'

    elif version == '201103L' and strictAnsi == '__STRICT_ANSI__':
        retVal = 'gnu++11'

    elif version == '201402L' and strictAnsi == '1':
        retVal = 'c++14'

    elif version == '201402L' and strictAnsi == '__STRICT_ANSI__':
        retVal = 'gnu++14'

    elif version == '201500L' and strictAnsi == '1':
        retVal = 'c++1z'

    elif version == '201500L' and strictAnsi == '__STRICT_ANSI__':
        retVal = 'gnu++1z'
    else:
        logging.warning('Cannot decode default language standard for C++.')

    return retVal

def getIncludePaths(compiler, lang):
    """
        Get the standard include paths for the given compiler and language ('c'
        or 'c++').
    """
    import io

    from ToolBOSCore.Util.FastScript import execProgram
    from subprocess import CalledProcessError

    def matchSearchPathStart(l):
        return l.strip() != '#include <...> search starts here:'

    def matchSearchPathEnd(l):
        return l.strip() != 'End of search list.'

    import itertools
    lines = _preprocessString( compiler, '', lang ).split('\n')

    inp = io.StringIO( '' )
    out = io.StringIO( )
    err = io.StringIO( )

    try:
        execProgram( '{} -x{} -E -Wp,-v -'.format( compiler, lang ),
                     stdin=inp,
                     stdout=out,
                     stderr=err )

        lines = err.getvalue().split( '\n' )

        it = itertools.dropwhile( matchSearchPathStart , lines )
        it = itertools.islice( it, 1, None )
        it = itertools.takewhile( matchSearchPathEnd , it )

        return [ p.strip() for p in it ]

    except CalledProcessError as e:
        logging.error( 'Unable to run the preprocessor: %s.', e )

    return None


# EOF
