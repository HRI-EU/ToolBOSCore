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


import io
import logging
import re
import urllib.parse

from ToolBOSCore.Settings import ProcessEnv
from ToolBOSCore.Util     import Any, FastScript

FastScript.tryImport( 'gitlab' )
import gitlab

# suppress SSL certification check warnings
import urllib3
urllib3.disable_warnings()


class GitLabServer( object ):

    def __init__( self, serverURL:str, token:str ):
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

        self._token     = token
        self._serverURL = serverURL
        self._gl        = gitlab.Gitlab( serverURL, ssl_verify=False, private_token=token )
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


    def getProjectsInGroup( self, groupName:str ) -> list:
        """
            Returns a list of all projects (repositories) within
            the given group. Items are of type GitLab instances.
        """
        Any.requireIsTextNonEmpty( groupName )

        resultList = []

        for project in self.getProjects():
            if project.namespace['path'] == groupName:
                resultList.append( project )

        return resultList


    def getProjectNamesInGroup( self, groupName:str ) -> list:
        """
            Returns a list of all project names (repository names) within
            the given group. Items are of type 'str'.
        """
        Any.requireIsTextNonEmpty( groupName )

        projectList = self.getProjectsInGroup( groupName )
        resultList  = []

        for project in projectList:
            resultList.append( project.name )

        return sorted( resultList )


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


    def getProjects( self ):
        """
            Returns a list of handles to all GitLab repositories.
        """
        try:
            return self._gl.projects.list( all=True, as_list=True )
        except gitlab.GitlabGetError as e:
            raise ValueError( e )


    def getProjectID( self, path:str ) -> int:
        """
            Returns the integer ID used internally by GitLab.
        """
        Any.requireIsTextNonEmpty( path )

        project = self.getProject( path )
        Any.requireIsInt( project.id )

        return project.id


    def getUserList( self ) -> list:
        """
            Returns a list with all user accounts on the server.

            Each entry in the returned list contains a dictionary of
            attributes.
        """
        result = self._gl.users.list( all=True, as_list=True )
        Any.requireIsListNonEmpty( result )

        return result


    def setVariable( self, projectID:int, variable:str, value:str ):
        """
            Sets the given GitLab project variable for the project
            to the provided value.

            Example:
                set( 200, 'remove_source_branch_after_merge', 'true' )

            Note that the value is a string, not a boolean.
        """
        Any.requireIsIntNotZero( projectID )
        Any.requireIsTextNonEmpty( variable )
        Any.requireIsTextNonEmpty( value )

        ProcessEnv.requireCommand( 'curl' )

        cmd = f'curl --insecure -X PUT -d {variable}={value} ' + \
              f'"{self._serverURL}/api/v4/projects/{projectID}?private_token={self._token}"'

        verbose = Any.getDebugLevel() > 3
        output  = None if verbose else io.StringIO()

        FastScript.execProgram( cmd, stdout=output, stderr=output )


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

        tmp             = urllib.parse.urlsplit( repoURL )
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


# EOF
