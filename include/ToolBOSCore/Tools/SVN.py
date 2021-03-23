# -*- coding: utf-8 -*-
#
#  functions to manage SVN working copies and repositories
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
import subprocess
import urllib.parse

from ToolBOSCore.Settings import ToolBOSConf
from ToolBOSCore.Storage  import AbstractVCS
from ToolBOSCore.Util     import Any
from ToolBOSCore.Util     import FastScript


class SVNRepository( AbstractVCS.RemoteRepository ):

    def __init__( self, url ):
        Any.requireIsMatching( url, ".*://.*" )
        Any.requireMsg( url[0] != "'", 'invalid repository URL' )
        Any.requireMsg( url[0] != '"', 'invalid repository URL' )

        # get rid of legacy hostnames
        url = url.replace( 'svnhost', 'hri-svn' )

        # use FQDN
        url = url.replace( 'hri-svn/', 'hri-svn.honda-ri.de/' )

        super( SVNRepository, self ).__init__( url )

        self._allowedHosts = ToolBOSConf.getConfigOption( 'SVN_allowedHosts' )


    def checkout( self, revision='HEAD', output=None ):
        """
            Fetches the specified revison from the given URL (which needs to
            point to a valid SVN repository).

            If the username to use for connecting to the server does not match
            your current username (e.g. on HRI-EU's Ext.SVN server), please
            use insertUsernameIntoURL() prior to this call.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        # suppress interactive password prompt for Ext.SVN (if any),
        # see JIRA ticket TBCORE-904
        oldValue = FastScript.getEnv( 'SVN_SSH' )

        if oldValue and not '-oBatchMode' in oldValue:
            # if SVN_SSH was already set then *append* our settings
            newValue = oldValue + ' -oBatchMode=yes'
        else:
            # set SVN_SSH
            newValue = 'ssh -oBatchMode=yes'

        FastScript.setEnv( 'SVN_SSH', newValue )

        cmd = self.getSourceCodeCommand( revision )

        return FastScript.execProgram( cmd, stdout=output, stderr=output )


    @classmethod
    def composeURL( cls, server, repositoryPath, category, packageName ):
        """
            Returns a string with the repository URL composed of the
            provided parts.
        """
        # Any.requireIsTextNonEmpty( server )    # None means local machine
        Any.requireIsTextNonEmpty( repositoryPath )
        Any.requireIsTextNonEmpty( category )
        Any.requireIsTextNonEmpty( packageName )

        if server:
            repositoryURL = 'svn+ssh://%s%s/%s/%s' % ( server, repositoryPath,
                                                       category, packageName )
        else:
            repositoryURL = 'file://%s/%s/%s' % ( repositoryPath,
                                                  category, packageName )

        return repositoryURL


    def create( self ):
        """
            Creates a new SVN repository.

            If the repository shall be on another server than 'localhost',
            SSH will be used to tunnel the execution of commands.
        """
        from ToolBOSCore.Packages import ProjectProperties

        tmp1        = urllib.parse.urlsplit( self.url )
        server      = tmp1.netloc
        repoDir     = tmp1.path

        server      = None if server == '' else server

        if server:                            # if not set create on localhost
            Any.requireIsTextNonEmpty( server )

        Any.requireIsTextNonEmpty( repoDir )

        repoRoot, category, packageName = ProjectProperties.splitPath( repoDir )
        repoParent                      = os.path.dirname( repoDir )

        logging.debug( 'repoRoot:     %s', repoRoot )
        logging.debug( 'repoParent:   %s', repoParent )
        logging.debug( 'repoDir:      %s', repoDir )
        logging.debug( 'category:     %s', category )
        logging.debug( 'package name: %s', packageName )
        logging.debug( 'server:       %s', server )

        logging.info( 'creating directory structure' )
        cmd = "mkdir -p %s" % repoDir
        FastScript.execProgram( cmd, host=server, workingDir='/' )

        logging.info( 'creating new repository' )
        cmd = "svnadmin create --fs-type fsfs %s" % packageName
        FastScript.execProgram( cmd, host=server, workingDir=repoParent )


        # verify that it exists now
        Any.requireMsg( self.exists(),
                           "failed to create repository (reason is unclear)" )


        # As decided by HRI-EU's Security Group in April 2009, new SVN
        # repositories will be protected from world access by default.
        # Beside the owner, only the same group can access repositories.
        # Manual interference is necessary to change this upon demand.

        if server:
            groupName = FastScript.getCurrentGroupName()

            logging.info( 'granting group read-permission (%s)', groupName )
            cmd = "chmod 2770 db db/transactions db/revs db/revprops && " + \
                "chmod 660 db/write-lock && chmod 750 hooks && "        + \
                "chmod 770 locks && chmod o-r * && chmod o-w * && "     + \
                "chmod o-x * && chmod -R g-w db && chmod 0750 ."

            FastScript.execProgram( cmd, host=server, workingDir=repoDir )
        else:
            logging.warning( 'setting repository permissions on local ' + \
                             'filesystem not implemented, yet' )


    def getHostName( self ):
        """
            Returns the hostname / FQDN / IP address as specified in the
            URL.
        """
        Any.requireIsTextNonEmpty( self.url )

        saneUrl = self._removeUsernameFromURL( self.url )
        Any.requireIsTextNonEmpty( saneUrl )

        hostName = urllib.parse.urlsplit( saneUrl ).netloc

        # in case of repositories located at 'file:///' a hostname won't
        # be found, hence do not require it
        # Any.requireIsTextNonEmpty( hostName )

        return hostName


    def getRepositoryName( self ):
        """
            Returns the name of a repository which can be different from
            the package name, e.g.:

            URL = svn+ssh://user@host/path/to/Foo

            returns: "Foo"
        """
        Any.requireIsTextNonEmpty( self.url )

        repoName = os.path.basename( self.url )
        Any.requireIsTextNonEmpty( repoName )

        return repoName


    def getSourceCode( self, revision='HEAD' ):
        return self.checkout( revision)


    def getSourceCodeCommand( self, revision='HEAD' ):
        Any.requireIsTextNonEmpty( self.url )

        if revision == 'HEAD':
            cmd = "svn co %s" % self.url
        else:
            cmd = "svn co -r %s %s" % ( revision, self.url )

        return cmd


    def exists( self ):
        """
            Checks if there is already a repository at the defined URL.

            Returns 'True' if repository exists, 'False' if not.
            Raises a ValueError if the repository exists but permission
            are denied.
        """
        Any.requireIsTextNonEmpty( self.url )

        output = io.StringIO()
        cmd    = "svn ls %s" % self.url
        status = None

        try:
            status = FastScript.execProgram( cmd, stdout=output, stderr=output )
        except subprocess.CalledProcessError:
            pass    # error handling is done later based upon status + details

        msg = output.getvalue()

        if status is None and msg.find( 'Permission denied' ) != -1:
            raise ValueError( msg )

        elif status is None and msg.find( 'No repository found' ) != -1:
            return False

        elif status is None and msg.find( 'not a working copy' ) != -1:
            return False

        elif status is None and msg.find( 'Unable to open an ra_local session to URL' ) != -1:
            return False

        elif status == 0 and \
             msg.find( 'Permission denied' ) == -1 and \
             msg.find( 'No repository found' ) == -1:
            return True

        else:
            # should never come here unless SVN utility output or return code
            # semantics changed
            return RuntimeError( 'script error, please report to ToolBOS developers' )


    def setConfiguredUserName( self ):
        """
            If a particular account has to be used to log into the server
            this function will auto-insert the username found in ToolBOS.conf
            for this server (if any).

            If no username was configured for the given server fall back to
            clean URL without any username (even if there was one before).
        """
        Any.requireIsTextNonEmpty( self._hostName )

        mapping  = ToolBOSConf.getConfigOption( 'serverAccounts' )
        Any.requireIsDict( mapping )

        userName = None


        for candidate, account in mapping.items():

            if self._hostName.find( candidate ) != -1:
                userName = account
                logging.info( 'found configured username=%s for server=%s',
                              userName, self._hostName )
                break


        self.setUserName( userName )
        logging.debug( 'modified URL: %s', self.url )


    def setUserName( self, username ):
        """
            Sets the URL to the given 'username'.

            If 'username' is None, the name will be removed (if present),
            leading to a sane URL.
        """
        self.url = self._removeUsernameFromURL( self.url )

        if username:
            self.url = self._insertUsernameIntoURL( self.url, username )


    def _insertUsernameIntoURL( self, url, username ):
        """
            If a particular account has to be used to log into the server
            specified in 'url', you can inject a "<username>@" using this
            function, e.g.:

                url = 'svn+ssh://svnext/Libraries/Spam/42.0'
                url = insertUsernameIntoURL( url, 'monthy' )

            will return 'svn+ssh://monthy@svnext/Libraries/Spam/42.0'.

            Note: The function works with other protocols such as "http://"
                  as well, e.g. as used by Git.
        """
        Any.requireIsTextNonEmpty( url )

        urlData = list( urllib.parse.urlsplit( url )[ : ] )
        urlData[1] = '%s@%s' % ( username, urlData[1] )

        result     = urllib.parse.urlunsplit (urlData )
        Any.requireIsTextNonEmpty( result )

        return result


    def _removeUsernameFromURL( self, url ):
        """
            Attempts to remove the "username@" part from self.url, e.g.:

              urlA = 'https://marijke@server/DevelopmentTools/ToolBOSCore.git'
              urlB = 'https://server/DevelopmentTools/ToolBOSCore.git'

            would in both cases return:

              'https://server/DevelopmentTools/ToolBOSCore.git'

            Note: The function works with other protocols such as "svn+ssh://"
                  as well, e.g. as used by Subversion.
        """
        Any.requireIsTextNonEmpty( url )

        result = url
        tmp    = re.search( '(.*)://.*?@(.*)', self.url )

        if tmp:
            result = '%s://%s' % ( tmp.group(1), tmp.group(2) )
            Any.requireIsTextNonEmpty( result )

        return result


class VersionedItem( object ):

    def __init__( self ):
        self.lastCommit = None
        self.path       = None
        self.props      = None
        self.revision   = None
        self.type       = None


    def __str__( self ):
        return 'rev=%d type=%s path=%s' % ( self.revision, self.type, self.path )


class WorkingCopy( AbstractVCS.AbstractWorkingTree ):

    def __init__( self ):
        super( WorkingCopy, self ).__init__()

        self.items             = set()
        self.repository        = None
        self.revision          = -1              # revision of "." directory

        self._infoOutput       = None
        self._repoRootFromInfo = None
        self._repoUrlFromInfo  = None
        self._revFromInfo      = None


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
            cmd = 'svn add %s' % item
            FastScript.execProgram( cmd, stdout=output, stderr=output )


    def commitUpstream( self, message, output=None, fileList=None ):
        """
            Commits changes within the current working copy to the repository.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).

            If 'fileList' is a list of files and/or directories, only they
            will get committed (so they will be passed as argument to
            "svn commit"). By default all modified files will be committed.
        """
        Any.requireIsTextNonEmpty( message )

        cmd = 'svn ci -m "%s"' % message

        if fileList:
            cmd = "%s %s" % ( cmd, ' '.join( fileList ) )

        if self._dryRun:
            logging.warning( "DRY-RUN: won't commit anything" )
            logging.debug( "command: %s", cmd )
        else:
            FastScript.execProgram( cmd, stdout=output, stderr=output )


    def consistencyCheck( self ):
        """
            Performs a check if the working copy is clean, e.g. for
            performing a global SIT installation.

            If everything is OK just passes and returns None, otherwise
            returns the modifications.

            If there are problems returns a tuple of three elements:
               1. descriptive short error message
               2. detailed description of the problem
               3. suggested solution
        """
        self._retrieveFileStatus()

        for item in self.items:
            if item.type != 'unversioned':

                if item.revision != -1 and item.revision != self.revision:
                    s1 = 'SVN consistency check failed'
                    s2 = '%s: SVN rev. found=%d (expected=%d)' % \
                          ( item.path, item.revision, self.revision )
                    s3 = 'Working copy has files in different revisions, ' \
                          'please sync them first. Maybe "svn up" is ' \
                          'sufficient, otherwise see "svn st -u" for details.'

                    return s1, s2, s3

                if item.type != 'normal':
                    s1 = 'SVN consistency check failed'
                    s2 = '"%s" %s but not committed' % ( item.path, item.type )
                    s3 = 'Working copy has uncommitted changes, see ' \
                          '"svn st" for details.'

                    return s1, s2, s3


    def diff( self, output=None ):
        """
            Invokes "svn diff" to yield changes within the local working copy.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        FastScript.execProgram( "svn diff", stdout=output, stderr=output )


    def getRepositoryRoot( self ):
        """
            Extracts the SVN repository root out of the provided "svn info"
            output.
        """
        self._retrieveMetaInfo()
        Any.requireIsTextNonEmpty( self._repoRootFromInfo )

        return self._repoRootFromInfo


    def getRepositoryURL( self ):
        """
            Extracts the SVN repository URL out of the provided "svn info"
            output.
        """
        self._retrieveMetaInfo()
        Any.requireIsTextNonEmpty( self._repoUrlFromInfo )

        return self._repoUrlFromInfo


    def getRevision( self ):
        """
            Extracts the SVN revision out of the provided "svn info" output.
        """
        self._retrieveMetaInfo()
        Any.requireIsInt( self._revFromInfo )

        return self._revFromInfo


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
            cmd = 'svn rm %s' % item
            FastScript.execProgram( cmd, stdout=output, stderr=output )


    def status( self, againstServer=False, output=None, verbose=False, xml=False ):
        """
            Invokes "svn st" (or "svn st -u" if againstServer=True).

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        if againstServer:
            cmd = "svn st -u"
        else:
            cmd = "svn st"

        if verbose:
            cmd += ' -v'

        if xml:
            cmd += ' --xml'

        FastScript.execProgram( cmd, stdout=output, stderr=output )


    def update( self, output=None ):
        """
            Updates the current working copy.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        cmd = 'svn up'

        if self._dryRun:
            logging.warning( "DRY-RUN: won't alter working copy" )
            logging.debug( "cmd: %s", cmd )
        else:
            FastScript.execProgram( cmd, stdout=output, stderr=output )


    def _retrieveMetaInfo( self ):
        """
            Invokes "svn info" within a working copy.

            If 'output' is a StringIO object, the command's output will be
            redirected there (otherwise printed on screen).
        """
        if not self._infoOutput:

            output = io.StringIO()


            # Temporarily unset the LANG environment variable, in order to always
            # get English output. Otherwise the "svn info" output might be German
            # or Japanese which would break the later parsing, see TBCORE-59.

            origEnv = FastScript.getEnv( 'LANG' )

            if origEnv:
                FastScript.unsetEnv( 'LANG' )

            cmd = 'svn info'
            FastScript.execProgram( cmd, stdout=output, stderr=output )

            if origEnv:
                FastScript.setEnv( 'LANG', origEnv )


            self._infoOutput = output.getvalue()

            self._repoRootFromInfo = re.search( r"Repository Root: (\S+)\n",
                                                self._infoOutput ).group(1)

            logging.debug( 'found SVN repository root: %s',
                           self._repoRootFromInfo )

            self._repoUrlFromInfo = re.search( r"URL: (\S+)\n",
                                               self._infoOutput ).group(1)

            logging.debug( 'found SVN repository URL: %s',
                           self._repoUrlFromInfo )

            self._revFromInfo = int( re.search( r"Revision\s?: (\d+?)\s",
                                self._infoOutput ).group(1) )

            logging.debug( 'found SVN revision: %d', self._revFromInfo )

        return self._infoOutput


    def _retrieveFileStatus( self, againstServer=False ):
        """
            Queries information about the working copy and fills
            internal members, such as self.items
        """
        from xml.dom import minidom

        Any.requireIsBool( againstServer )

        output = io.StringIO()
        self.status( againstServer, output, verbose=True, xml=True )

        Any.requireIsTextNonEmpty( output.getvalue() )
        dom = minidom.parseString( output.getvalue() )

        for entry in dom.getElementsByTagName( 'entry' ):

            wcStatusData    = entry.getElementsByTagName( 'wc-status' )[0]

            try:
                dom             = wcStatusData.getElementsByTagName( 'commit' )[0]

                commit          = AbstractVCS.Commit()
                commit.author   = dom.getElementsByTagName( 'author' )[0]
                commit.date     = dom.getElementsByTagName( 'date' )[0]
                commit.revision = int( dom.getAttribute( 'revision' ) )

            except IndexError:
                commit          = None

            item            = VersionedItem()
            item.lastCommit = commit
            item.path       = entry.getAttribute( 'path' )
            item.props      = wcStatusData.getAttribute( 'props' )
            item.type       = wcStatusData.getAttribute( 'item' )

            try:
                item.revision = int( wcStatusData.getAttribute( 'revision' ) )
            except ValueError:
                item.revision = -1

            # use the revision of "." as the wc's main revision
            if item.path == '.':
                self.revision = item.revision

            self.items.add( item )


# EOF
