# -*- coding: utf-8 -*-
#
#  convenience functions for using the Mako template engine
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

from mako.lookup import TemplateLookup

from ToolBOSCore.Util import Any, FastScript


# location of Mako templates
templateDir = os.path.join( FastScript.getEnv( 'TOOLBOSCORE_ROOT' ),
                            'etc/mako-templates' )


def run( srcFile, dstFile, values ):
    """
        Runs the templating engine, applying the given values
        onto the template file 'srcFile', writing results into 'dstFile'.
    """
    Any.requireIsFile( srcFile )
    Any.requireIsText( dstFile )
    Any.requireIsDict( values )

    logging.info( 'processing %s', dstFile )

    # First determine the directory of the template file, and tell Mako
    # to search there. In a second step tell Mako to search for a template
    # file in this search path.
    #
    # This is the only solution to get Mako's "include" working.

    lookup   = TemplateLookup( directories=[ os.path.dirname( srcFile ) ] )
    template = lookup.get_template( os.path.basename( srcFile ) )

    dstContent = template.render( **values )
    Any.requireIsText( dstContent )

    FastScript.mkdir( os.path.dirname( dstFile ) )  # ensure dst dir. exists
    FastScript.setFileContent( dstFile, dstContent )
    Any.requireIsFile( dstFile )

    # Mako does not set the executable-flag on the generated output file.
    if os.access( srcFile, os.X_OK ):                  # if executable
        os.chmod( dstFile, os.stat( srcFile )[0] )     # copy mode bits


# EOF
