# -*- coding: utf-8 -*-
#
#  Abstract class for various revision control systems
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
import urllib.parse

from ToolBOSCore.Util import Any, FastScript


class AbstractVCS( object ):

    def __init__( self ):
        self.working = None
        self.parent  = None


    def getRevision( self ):
        raise NotImplementedError()


class AbstractWorkingTree( object ):

    def __init__( self ):
        super( AbstractWorkingTree, self ).__init__()

        self._dryRun = FastScript.getEnv( 'DRY_RUN' ) == 'TRUE'


    def add( self, fileList, output=None ):
        raise NotImplementedError()


    def commitUpstream( self, message, output=None, fileList=None ):
        raise NotImplementedError()


    def consistencyCheck( self ):
        raise NotImplementedError()


    def diff( self, output=None ):
        raise NotImplementedError()


    def remove( self, fileList, output=None ):
        raise NotImplementedError()


    def setDryRun( self, boolean ):
        """
            If 'dryRun' is True, nothing will actually happen but the command
            is just printed (for debugging purposes).
        """
        Any.requireIsBool( boolean )

        self._dryRun = boolean

        logging.debug( 'VCS operating in dry-run mode: %s', self._dryRun )


    def switchToBranch( self, branch, output=None ):
        raise NotImplementedError()


    def update( self, output=None ):
        raise NotImplementedError()


class Repository( object ):

    def __init__( self ):
        self.url     = None


class LocalRepository( Repository ):

    def __init__( self ):
        super( LocalRepository, self ).__init__()


    def add( self, fileList, output=None ):
        raise NotImplementedError()


    def commitUpstream( self, message, output=None, fileList=None ):
        raise NotImplementedError()


    def diff( self, output=None ):
        raise NotImplementedError()


    def remove( self, msg, fileList=None ):
        raise NotImplementedError()


class RemoteRepository( Repository ):

    def __init__( self, url ):
        Any.requireIsTextNonEmpty( url )

        super( RemoteRepository, self ).__init__()

        self.url           = url
        self._hostName     = self.getHostName()
        self._allowedHosts = set()


    def checkIsOnMasterServer( self ):
        """
            Issues a warning message if the URL does not point to a
            repository hosted on allowed servers, as listed in
            ToolBOS.conf.

            See TBCORE-1135 for details.
        """
        if not self.isOnMasterServer():
            logging.warning( '' )
            logging.warning( 'Package is not maintained on any known server!' )
            logging.warning( '' )
            logging.warning( 'Allowed host(s):' )

            for hostName in sorted( self._allowedHosts ):
                logging.warning( '    * %s', hostName )

            logging.warning( '' )


    def getHostName( self ):
        """
            Returns the hostname / FQDN / IP address as specified in the
            URL.
        """
        raise NotImplementedError()


    def getRepositoryName( self ):
        """
            Returns the name of a repository which can be different from
            the package name.
        """
        raise NotImplementedError()


    def getSourceCode( self, revision ):
        """
            Get the source code from the repository onto local disk,
            no matter how this is achieved by the backend.
        """
        raise NotImplementedError()


    def getSourceCodeCommand( self, *params ):
        """
            Returns the command the user would have to invoke on commandline
            to fetch the source code from the repository, e.g.:

            'git clone <url>'
            'svn co <url>'
        """
        raise NotImplementedError()


    def isOnMasterServer( self ):
        """
            Issues a warning message if the URL does not point to a
            repository hosted on allowed servers, as listed in
            ToolBOS.conf.

            See TBCORE-1135 for details.
        """
        Any.requireIsTextNonEmpty( self._hostName )

        logging.debug( 'searching for %s in %s',
                       self._hostName, self._allowedHosts )

        for candidate in self._allowedHosts:

            # by using startswith() we match single hostnames and FQDN
            if candidate.startswith( self._hostName ):
                return True

        return False


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

        urlData    = list( urllib.parse.urlsplit( url )[ : ] )
        urlData[1] = '%s@%s' % ( username, urlData[1] )

        result     = urllib.parse.urlunsplit( urlData )
        Any.requireIsTextNonEmpty( result )

        return result


class Commit( object ):

    def __init__( self ):
        self.author    = None
        self.date      = None
        self.revision  = None


# EOF
