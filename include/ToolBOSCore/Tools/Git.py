# -*- coding: utf-8 -*-
#
#  functions to manage Git repositories
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
import os
import re
import urllib.parse

from ToolBOSCore.Settings import ToolBOSConf
from ToolBOSCore.Storage  import AbstractVCS
from ToolBOSCore.Util     import Any, FastScript


class LocalGitRepository( AbstractVCS.AbstractWorkingTree ):

    _modifiedFileExpr = re.compile( r'^\sM\s(.+)$' )


    def __init__( self ):
        super( LocalGitRepository, self ).__init__()


    def add( self, fileList, output=None ):
        """
            Flags the given files and/or directories to be added for later
            commit.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        if not Any.isIterable( fileList ):
            fileList = [ fileList ]

        for item in fileList:
            cmd = 'git add %s' % item
            FastScript.execProgram( cmd, stdout=output, stderr=output )


    def commitLocal( self, message, output=None, fileList=None ):
        """
            Commits changes within the current working tree to the local
            repository.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).

            If 'fileList' is a list of files and/or directories, only they
            will get committed (so they will be passed as argument to
            "git commit"). By default all modified files will be committed.
        """
        Any.requireIsTextNonEmpty( message )

        cmd = 'git ci -m "%s"' % message

        if fileList:
            cmd = "%s %s" % ( cmd, ' '.join( fileList ) )

        if self._dryRun:
            logging.warning( "DRY-RUN: won't commit anything" )
            logging.debug( "command: %s", cmd )
        else:
            FastScript.execProgram( cmd, stdout=output, stderr=output )


    def commitUpstream( self, message, output=None, fileList=None ):
        self.commitLocal( message, output, fileList )
        self.push()


    def consistencyCheck( self ):
        """
            Performs a check if the working tree is clean, e.g. for
            performing a global SIT installation.

            If everything is OK just passes and returns None, otherwise
            returns the modifications.

            If there are problems returns a tuple of three elements:
               1. descriptive short error message
               2. detailed description of the problem
               3. suggested solution
        """
        tmp = io.StringIO()
        cmd = 'git status --porcelain'

        FastScript.execProgram( cmd, stdout=tmp )

        output = tmp.getvalue()
        Any.requireIsText( output )

        modifiedFiles = set()

        for line in output.splitlines():
            tmp = self._modifiedFileExpr.match( line )

            if tmp is not None:
                modifiedFiles.add( tmp.group(1) )

        if modifiedFiles:
            s1 = 'Git consistency check failed'
            s2 = 'modified files not committed (%s)' % ','.join( sorted(modifiedFiles) )
            s3 = 'Working tree has uncommitted changes, see "git status" for details.'

            return s1, s2, s3


    def diff( self, output=None ):
        """
            Invokes "git diff" to yield changes within the local working copy.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        FastScript.execProgram( "git diff", stdout=output, stderr=output )


    def fetch( self, output=None ):
        """
            Retrieve new commits from the remote peer.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        cmd = 'git fetch'

        if self._dryRun:
            logging.warning( "DRY-RUN: won't transfer anything" )
            logging.debug( "cmd: %s", cmd )
        else:
            FastScript.execProgram( cmd, stdout=output, stderr=output )


    def getCurrentBranch( self ):
        """
            Returns the name of the current branch (e.g. "master").

            May return None, for example if repo is in 'Detached HEAD'
            state.
        """
        output = io.StringIO()
        cmd    = 'git rev-parse --abbrev-ref HEAD'

        FastScript.execProgram( cmd, stdout=output, stderr=output )

        result = output.getvalue().strip()
        logging.debug( 'found Git branch name: %s', result )

        return result


    def getLastCommit( self, short=False ):
        """
            Retrieves the ID of the last commit, in either normal (= long)
            or short form.

            Returns ID of last commit as string, or raises error if not a Git
            repository.
        """
        Any.requireIsBool( short )

        output = io.StringIO()

        if short:
            cmd = "git rev-parse --short HEAD"
        else:
            cmd = "git rev-parse HEAD"

        FastScript.execProgram( cmd, stdout=output, stderr=output )

        result = output.getvalue().strip()
        logging.debug( 'found Git commit ID: %s', result )

        return result


    def getOrigin( self ):
        """
            Returns the URL of the 'origin' (fetch direction).
        """
        tmp = io.StringIO()

        FastScript.execProgram( 'git remote -v', stdout=tmp )
        output = tmp.getvalue()
        # Any.requireIsTextNonEmpty( output )  # repo may not have any remote

        if output:
            for line in output.splitlines():
                tmp = re.match( r"^origin\s+(.*)\s\(fetch\)", line )

                if tmp:
                    return tmp.group(1)

        raise ValueError( 'this Git repository has no "origin" remote peer configured')


    def detectRepositoryRoot( self, path=None ):
        """
            From any given path that points *within* a repo, this function
            tries to find the root directory by searching the current
            and parent directories for a '.git' subdirectory.

            If path is omitted (None), search starts at the current working
            directory.
        """
        if not path:
            path = os.getcwd()

        Any.requireIsDir( path )

        gitDirPath = os.path.join( path, '.git' )

        if os.path.exists( gitDirPath):
            return path

        if path == '' or path == '/':
            result = None
        else:
            result = self.detectRepositoryRoot( os.path.split( path )[0] )

        return result


    def getRepoRelativePath( self, path=None ):
        """
            Returns the relative path from the repository root to the
            provided path, e.g. to locate a package's top-level-directory.

            If path is omitted (None) assume the current working directory.
        """
        if not path:
            path = os.getcwd()

        Any.requireIsDir( path )

        repoRoot = self.detectRepositoryRoot()

        if repoRoot is None:
            raise ValueError( 'unable to detect repository root' )
        else:
            Any.requireIsDir( repoRoot )

        relPath = path.replace( repoRoot, '' )
        Any.requireIsText( relPath )

        # remove leading slash (untypical for relative paths)
        if relPath.startswith( '/' ):
            relPath = relPath[1:]

        return relPath


    def getRevision( self ):
        return self.getLastCommit( short=True )


    def push( self, remote='origin' ):
        logging.warning( 'PUSHING NOT IMPLEMENTED, YET' )


    def remove( self, fileList, output=None ):
        """
            Flags the given files and/or directories to be removed with
            the next commit.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        if not Any.isIterable( fileList ):
            fileList = [ fileList ]

        for item in fileList:
            cmd = 'git rm %s' % item
            FastScript.execProgram( cmd, stdout=output, stderr=output )


    def switchToBranch( self, branch, output=None ):
        """
            Switches bare repository to the given branch.

            Hint: Better use WorkingTree.switchToBranch()
        """
        Any.requireIsTextNonEmpty( branch )

        cmd = 'git symbolic-ref HEAD refs/heads/' + branch

        FastScript.execProgram( cmd, stdout=output, stderr=output )


    def update( self, output=None ):
        """
            Alias for fetch() to satisfy AbstractVCS.update() interface.
        """
        return self.fetch( output )


class RemoteGitRepository( AbstractVCS.RemoteRepository ):

    def __init__( self, url ):
        Any.requireIsTextNonEmpty( url )

        super( RemoteGitRepository, self ).__init__( url )

        self._allowedHosts = ToolBOSConf.getConfigOption( 'Git_allowedHosts' )


    def clone( self, output=None ):
        """
            Clones the repository at the given URL.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        cmd = self.getSourceCodeCommand()
        FastScript.execProgram( cmd, stdout=output, stderr=output )


    def forceSSH( self ):
        """
            In case of HTTP(S), rewrite the URL to use SSH instead.

            Has no effect if it was already SSH.
        """
        if self.url.startswith( 'http' ):
            tokens = urllib.parse.urlsplit( self.url )

            # remove username from net location, if present
            tmp = re.match( '^.+@(.+)$', tokens.netloc )

            if tmp is None:
                host = tokens.netloc
            else:
                host = tmp.group(1)


            path   = tokens.path[1:]    # omit leading '/'
            result = 'git@%s:%s' % ( host, path )

            logging.info( 'use SSH instead: %s', result )
            self.url = result


    def getHostName( self ):
        """
            Returns the hostname / FQDN / IP address as specified in the
            URL.
        """
        Any.requireIsTextNonEmpty( self.url )

        if self.url.startswith( 'http' ):
            hostName = self._getHostName_HTTP()

        elif self.url.startswith( 'git@' ):
            hostName = self._getHostName_SSH()

        else:
            raise ValueError( 'unexpected protocol in %s' % self.url )

        return hostName


    def getRepositoryName( self ):
        """
            Returns the name of a repository which can be different from
            the package name, e.g.:

            URL = git@dmz-gitlab.honda-ri.de:ToolBOS/BasicComponents.git

            returns: "BasicComponents"
        """
        Any.requireIsTextNonEmpty( self.url )

        tmp      = os.path.basename( self.url )
        Any.requireIsTextNonEmpty( tmp )

        repoName = tmp.replace( '.git', '' )
        Any.requireIsTextNonEmpty( repoName )

        return repoName


    def getSourceCode( self, *unused ):
        return self.clone()


    def getSourceCodeCommand( self, asSubModule=False ):
        Any.requireIsBool( asSubModule )
        Any.requireIsTextNonEmpty( self.url )

        if asSubModule:
            cmd = 'git submodule add %s' % self.url
        else:
            cmd = 'git clone %s' % self.url

        return cmd


    def setUserName( self, username ):
        """
            Sets the URL to the given 'username'.

            If 'username' is None, the name will be removed (if present),
            leading to a sane URL.
        """
        logging.info( 'Git backend: no need to set username=%s', username )


    def _getHostName_HTTP( self ):
        Any.requireIsTextNonEmpty( self.url )

        netloc = urllib.parse.urlsplit( self.url ).netloc
        Any.requireIsTextNonEmpty( netloc )

        # remove leading 'username@' if present
        if '@' in netloc:
            tmp      = re.search( '@(.+)', netloc )
            hostName = tmp.group(1)
            Any.requireIsTextNonEmpty( hostName )

        else:
            hostName = netloc

        return hostName


    def _getHostName_SSH( self ):
        Any.requireIsTextNonEmpty( self.url )

        pattern = '^git@(.+):.+$'
        tmp     = re.match( pattern, self.url )

        if tmp is None:
            raise ValueError( '%s does not match pattern: %s' % \
                              ( self.url, pattern ) )

        else:
            hostName = tmp.group( 1 )
            Any.requireIsTextNonEmpty( hostName )

            return hostName


class WorkingTree( AbstractVCS.AbstractWorkingTree ):

    def __init__( self ):
        super( WorkingTree, self ).__init__()

        self._repo = LocalGitRepository()


    def switchToBranch( self, branch, output=None ):
        """
            Switches to the given branch.
        """
        Any.requireIsTextNonEmpty( branch )

        cmd = 'git checkout %s' % branch

        FastScript.execProgram( cmd, stdout=output, stderr=output )


def git2https( gitURL:str ) -> str:
    """
        Translates an URL in form "[git+ssh://]git@<host>:<group>/<project>.git"
        into the form "https://<host>/<group>/<project>".

        If the URL already starts with 'https://' then the same string
        is used.

        In all cases (incl. URL started with 'https://') the function
        ensures that the returned HTTPS URL contains a trailing '.git'.
    """
    Any.requireIsTextNonEmpty( gitURL )

    if gitURL.startswith( 'https://' ):
        httpsURL = gitURL

    else:
        # leading 'git+ssh://' can be omitted
        if gitURL.startswith( 'git+ssh://' ):
            tmp1 = gitURL.replace( 'git+ssh://', '' )
        else:
            tmp1 = gitURL

        Any.requireIsMatching( tmp1, '^git@.+' )

        # replace the ':' by '/'
        tmp2 = tmp1.replace( ':', '/' )

        # replace 'git@' by 'https//'
        httpsURL = tmp2.replace( 'git@', 'https://' )


    # ensure HTTPS URL ends with '.git'
    if not httpsURL.endswith( '.git' ):
        httpsURL += '.git'

    return httpsURL


# EOF
