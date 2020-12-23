# -*- coding: utf-8 -*-
#
#  Factories to deal with various revision control systems the same way
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

from ToolBOSCore.Tools import Git, SVN
from ToolBOSCore.Util  import Any


class VCS( object ):
    """
        Factory to create a Git or SVN instance auto-detected from the
        provided URL to an existing

           * SVN or Git repository,
           * SVN working copy or
           * Git working tree.
    """

    def local( self ):

        rcsInfoDir = self._detectInfoDir( os.getcwd() )

        if rcsInfoDir is None:
            raise EnvironmentError( 'No revision control system information found' )

        elif rcsInfoDir.endswith( '.svn' ):
            logging.debug( 'found SVN info in %s', rcsInfoDir )
            return SVN.WorkingCopy()

        elif rcsInfoDir.endswith( '.git' ):
            logging.debug( 'found Git info in %s', rcsInfoDir )
            return Git.LocalGitRepository()

        else:
            raise EnvironmentError( 'No revision control system information found' )


    def remote( self, url ):

        if url.startswith( 'svn+ssh://' ):
            return SVN.SVNRepository( url )

        elif url.startswith( 'https://' ) or url.endswith( '.git' ):
            return Git.RemoteGitRepository( url )

        else:
            raise EnvironmentError( 'Unexpected revision control URL' )


    def _detectInfoDir( self, path ):
        """
            Tries to recursively go upwards until it finds a ".svn" or ".git"
            directory, and returns the corresponding path or None.
        """
        svnDir = os.path.join( path, '.svn' )
        gitDir = os.path.join( path, '.git' )

        if os.path.exists( svnDir ):
            return svnDir

        elif os.path.exists( gitDir ):
            return gitDir

        else:

            if path == '' or path == '/':
                return None
            else:
                return self._detectInfoDir( os.path.split( path )[0] )


def auto( url=None ):
    """
        Convenience decorator, which depending on the URL provided returns
        a remote VCS instance, otherwise attempts to find a local VCS tree.
    """
    if url is None:
        return VCS().local()
    else:
        return VCS().remote( url )


#----------------------------------------------------------------------------
# Main
#----------------------------------------------------------------------------


if __name__ == '__main__':
    # print nothing but the revision number to stdout, called from
    # ToolBOSCore/2.0/CMakeLists.txt
    Any.setDebugLevel( 0 )


    rcs      = VCS().local()
    revision = rcs.getRevision()

    if not revision:
        revision = '0'

    print( revision )


# EOF
