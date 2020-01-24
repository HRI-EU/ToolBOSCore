# -*- coding: utf-8 -*-
#
#  Manage GitLab repositories via REST API
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
import re

from ToolBOSCore.Util import Any, FastScript, VersionCompat

FastScript.tryImport( 'gitlab' )
import gitlab

# suppress SSL certification check warnings
import urllib3
urllib3.disable_warnings()


class GitLabServer( object ):

    def __init__( self, serverURL, token ):
        """
            Establishes a connection to the specified GitLab server
            using the 'gitlab' Python module.

            Should the URL be a HTTPS resource, SSL certificates will not
            be checked.

            'serverURL' should be in form 'http[s]://host.domain'

            'token' needs to be a pre-configured private access token
        """
        Any.requireIsTextNonEmpty( serverURL )
        Any.requireIsMatching( serverURL, '^http.+' )

        self._gl = gitlab.Gitlab( serverURL, ssl_verify=False, private_token=token )
        Any.requireIsInstance( self._gl, gitlab.Gitlab )


    def getDeployKeys( self ):
        """
            Returns all global deploy keys as a dict mapping
            'key title' --> ID.
        """
        result = {}

        for key in self._gl.deploykeys.list():
            Any.requireIsTextNonEmpty( key.title )
            Any.requireIsIntNotZero( key.id )

            result[ key.title ] = key.id

        return result


    def getProject( self, path ):
        """
            Returns a dict with plenty of information about a certain
            GitLab repository.
        """
        Any.requireIsTextNonEmpty( path )

        try:
            result = self._gl.projects.get( path )
            Any.requireIsInstance( result, gitlab.v4.objects.Project )
            return result

        except gitlab.GitlabGetError as e:
            raise ValueError( '%s: %s' % ( path, e ) )


class GitLabRepo( object ):

    _splitProjectExpr = re.compile( '^/(\S+/\S+)\.git$' )

    def __init__( self, repoURL, token ):
        """
            Establishes a connection to the specified GitLab server
            using the 'gitlab' Python module.

            'repoURL' should be a complete repository URL in the form
            'http[s]://server/group/project.git'

            Should the URL be a HTTPS resource, SSL certificates will not
            be checked.

            path = '<groupName>/><projectName>'

            'token' needs to be a pre-configured private access token
        """
        Any.requireIsTextNonEmpty( repoURL )
        Any.requireIsMatching( repoURL, '^http.+\.git' )
        Any.requireIsTextNonEmpty( token )

        tmp             = VersionCompat.urlsplit( repoURL )
        Any.requireIsTextNonEmpty( tmp.scheme )
        Any.requireIsTextNonEmpty( tmp.netloc )
        Any.requireIsTextNonEmpty( tmp.path )

        serverURL       = '%s://%s' % ( tmp.scheme, tmp.netloc )
        Any.requireIsTextNonEmpty( serverURL )

        match           = self._splitProjectExpr.match( tmp.path )
        Any.requireIsNotNone( match )

        path            = match.group(1)
        Any.requireIsTextNonEmpty( path )
        Any.requireIsMatching( path, '^[A-Za-z0-9].+/.+[A-Za-z0-9]$' )

        self._gls       = GitLabServer( serverURL, token )
        Any.requireIsInstance( self._gls, GitLabServer )

        self._project   = self._gls.getProject( path )
        Any.requireIsInstance( self._project, gitlab.v4.objects.Project )

        self._projectID = self._project.id
        Any.requireIsIntNotZero( self._projectID )


    def enableDeployKey( self, keyID ):
        Any.requireIsIntNotZero( keyID )

        logging.debug( 'adding deployKey=%d to project=%s',
                       keyID, self._project.path_with_namespace )

        self._project.keys.enable( keyID )


    def getProject( self ):
        """
            Returns a dict with plenty of information about a certain
            GitLab repository, given in the form
        """
        result = self._project.attributes
        Any.requireIsDictNonEmpty( result )

        return result


def git2https( gitURL ):
    """
        Translates an URL in form "git@<host>:<group>/<project>.git" into
        the form "https://<host>/<group>/<project>".
    """
    Any.requireIsTextNonEmpty( gitURL )
    Any.requireIsMatching( gitURL, '^git@.+' )

    # replace the ':' by '/'
    tmp = gitURL.replace( ':', '/' )

    # replace 'git@' by 'https//'
    httpsURL = tmp.replace( 'git@', 'https://' )

    # ensure it ends with '.git'
    if not httpsURL.endswith( '.git' ):
        httpsURL += '.git'

    return httpsURL


# EOF
