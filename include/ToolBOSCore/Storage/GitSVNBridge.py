# -*- coding: utf-8 -*-
#
#  Git-style access to SVN repositories
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

from ToolBOSCore.Tools import Git, SVN
from ToolBOSCore.Util  import Any
from ToolBOSCore.Util  import FastScript


class GitSVNBridge( Git.LocalGitRepository ):


    def __init__( self, url ):
        Any.requireIsTextNonEmpty( url )

        self._svnRepo = SVN.SVNRepository( url )

        super( GitSVNBridge, self ).__init__()


    def clone( self, output=None ):
        """
            Clones the full content of the SVN repository into a local Git
            repository.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        oldcwd      = os.getcwd()
        packageName = os.path.basename( self._svnRepo.url )
        Any.requireIsTextNonEmpty( packageName )

        FastScript.mkdir( packageName )
        FastScript.changeDirectory( packageName )

        cmd = "git svn init %s" % self._svnRepo.url
        FastScript.execProgram( cmd, stdout=output, stderr=output )

        cmd = "git svn fetch"
        FastScript.execProgram( cmd, stdout=output, stderr=output )

        FastScript.changeDirectory( oldcwd )


    def checkIsOnMasterServer( self ):
        return self._svnRepo.isOnMasterServer()


    def setUserName( self, username ):
        """
            Sets the URL to the given 'username'.

            If 'username' is None, the name will be removed (if present),
            leading to a sane URL.
        """
        self._svnRepo.setUserName( username )


# EOF
