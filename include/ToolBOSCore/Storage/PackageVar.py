# -*- coding: utf-8 -*-
#
#  packageVar.cmake writer
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


import os

from ToolBOSCore.Storage.AbstractWriter import AbstractWriter
from ToolBOSCore.Storage.SIT            import strip


class PackageVarCmakeWriter( AbstractWriter ):

    def addLeadIn( self ):
        return '''#
#  Exported CMake settings
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

'''


    def addDependencies( self ):
        result = '''
#----------------------------------------------------------------------------
# Dependencies
#----------------------------------------------------------------------------


# please include here the packages this one depends on
# (one bst_find_package() per dependency), e.g:
# bst_find_package(DevelopmentTools/ToolBOSCore/2.0)

'''
        for dep in self.details.dependencies:
            if dep.startswith( 'sit://' ):
                canonicalPath = strip( dep )
                result += 'bst_find_package(%s)\n' % canonicalPath

        return result + '\n'


    def addBuildSystemInfo( self ):

        result = '''
#----------------------------------------------------------------------------
# Build specification
#----------------------------------------------------------------------------


# locations of headerfiles, e.g.:
# include_directories($ENV{SIT}/DevelopmentTools/ToolBOSCore/2.0/include)

include_directories($ENV{SIT}/%s/include)

''' % self.details.canonicalPath

        if os.path.exists( 'lib' ):
            comment = ''
        else:
            comment = '# '


        result += '''
# locations of libraries, e.g.:
# link_directories($ENV{SIT}/DevelopmentTools/ToolBOSCore/2.0/lib/$ENV{MAKEFILE_PLATFORM})

%(comment)slink_directories($ENV{SIT}/%(canonicalPath)s/lib/$ENV{MAKEFILE_PLATFORM})


# libraries to link (shared libs without "lib" prefix and filename extension), e.g.:
# list(APPEND BST_LIBRARIES_SHARED ToolBOSCore)
# list(APPEND BST_LIBRARIES_STATIC $ENV{SIT}/path/to/libFoo${CMAKE_STATIC_LIBRARY_SUFFIX})

%(comment)slist(APPEND BST_LIBRARIES_SHARED %(packageName)s)
%(comment)slist(APPEND BST_LIBRARIES_STATIC $ENV{SIT}/%(canonicalPath)s/lib/$ENV{MAKEFILE_PLATFORM}/lib%(packageName)s${CMAKE_STATIC_LIBRARY_SUFFIX})


''' % { 'canonicalPath': self.details.canonicalPath,
        'comment':       comment,
        'packageName':   self.details.packageName }

        return result

    def addLeadOut( self ):
        return '# EOF\n'


# EOF
