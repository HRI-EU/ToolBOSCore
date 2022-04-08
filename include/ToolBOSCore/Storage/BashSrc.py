# -*- coding: utf-8 -*-
#
#  BashSrc writer
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
import os

from ToolBOSCore.Packages import PackageDetector
from ToolBOSCore.Storage  import SIT
from ToolBOSCore.Util     import Any, TemplateEngine


class BashSrcWriter( object ):

    def __init__( self, details, overrides=None ):
        """
            This constructor uses an existing PackageDetector instance
            to avoid multiple detection of package meta-information
            (for each derived subclass BashSrcWriter etc.)

            You may provide a dict with values overriding the auto-detected
            values, mainly intended for unittesting purposes.
        """
        Any.require( isinstance( details, PackageDetector.PackageDetector ) )
        Any.requireIsList( details.inheritedProjects )
        sitDependencies = '('
        first           = True

        for inheritedProject in details.inheritedProjects:
            if not first:
                sitDependencies += '\n                  '

            sitDependencies += "'" + SIT.strip( inheritedProject ) + "'"
            first            = False

        sitDependencies += ')'

        # replacement map etc. passed to templating engine
        self.values  = { 'hasLibDir'      : os.path.isdir( details.libDir ),
                         'packageCategory': details.packageCategory,
                         'packageName'    : details.packageName,
                         'packageVersion' : details.packageVersion,
                         'userSrcBashCode': details.userSrcBashCode,
                         'userSrcAlias'   : details.userSrcAlias,
                         'userSrcEnv'     : details.userSrcEnv,
                         'sitDependencies': sitDependencies }

        if overrides:
            Any.requireIsDictNonEmpty( overrides )
            self.values.update( overrides )


    def write( self, outputFile ):
        logging.info( 'generating %s', os.path.relpath( outputFile, os.getcwd() ) )

        srcFile = os.path.join( TemplateEngine.templateDir, 'BST', 'BashSrc.mako' )
        dstFile = outputFile

        TemplateEngine.run( srcFile, dstFile, self.values )


# EOF
