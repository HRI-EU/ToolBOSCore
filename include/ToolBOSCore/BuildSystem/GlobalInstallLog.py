# -*- coding: utf-8 -*-
#
#  Global install log handler
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
#  A global install log message is represented by a file within the
#  directory ${SIT}/Temporary/GlobalInstallLogfiles.
#
#  Please use this script to generate log entries as the internal structure
#  of the files is subject to change (facade pattern).
#
#


import logging
import os.path

from datetime import datetime
from getpass  import getuser
from time import time

from ToolBOSCore.Packages.ProjectProperties import splitPath
from ToolBOSCore.Storage.SIT                import getRootPath
from ToolBOSCore.Util.FastScript            import mkdir
from ToolBOSCore.Util.FastScript            import setFileContent
from ToolBOSCore.Util                       import Any
from xml.sax                                import saxutils


class GlobalInstallLog( object ):
    """
        This class handles a single globalinstall log entry.
    """
    def __init__( self, packagePath, isFirstInstall, msgType, message ):
        """
            Creates a new global install log entry instance.
        """
        Any.requireIsTextNonEmpty( packagePath )
        Any.requireIsBool( isFirstInstall )
        Any.requireIsTextNonEmpty( msgType )
        Any.requireIsIn( msgType, ( 'NEW', 'FIX', 'DOC', 'IMP' ) )

        self._date            = datetime.now().strftime( "%Y-%m-%d&nbsp;%H:%M:%S" )
        self._installRoot     = ''
        self._packageCategory = ''
        self._packageName     = ''
        self._packageVersion  = ''
        self._maintainer      = getuser()
        self._isFirstInstall  = False
        self._msgType         = 'NEW'
        self._message         = ''
        self._fileName        = None
        self._fileExt         = 'xml'


        ( self._packageCategory, self._packageName, self._packageVersion ) = \
            splitPath( packagePath )


        Any.requireIsTextNonEmpty( self._packageCategory )
        Any.requireIsTextNonEmpty( self._packageName )
        Any.requireIsTextNonEmpty( self._packageVersion )


        self.setIsFirstInstall( isFirstInstall )
        self.setMsgType( msgType )
        self.setMessage( message )

        sitRootPath = getRootPath()
        timestamp   = int( time() )

        getFileName = lambda t: os.path.join( sitRootPath, 'Temporary',
                                              'GlobalInstallLogfiles',
                                              'GlobalInstall_%d.%s' % \
                                              ( timestamp, self._fileExt ) )
        fileName    = getFileName( timestamp )

        while os.path.exists( fileName ):
            logging.debug( 'global log entry %d exists, increasing to %d',
                           timestamp, timestamp + 1 )

            # if a logfile of this name already exists, try increasing the
            # timestamp
            timestamp += 1
            fileName   = getFileName( timestamp )

        self.setFileName( fileName )


    def setIsFirstInstall( self, isFirstInstall ):
        """
            You should set this boolean to true to mark the package as
            "new" upon the very first installation.
        """
        Any.requireIsBool( isFirstInstall )
        self._isFirstInstall = isFirstInstall


    def setMsgType( self, msgType ):
        """
            A globalinstall log entry can be of the following type:

              "NEW": if mostly new features have been implemented
              "FIX": for bugfixes, corrections, clean-up of misbehaviors
              "DOC": if only documentation has been touched (no code changes)
        """
        whitelist = [ 'NEW','FIX','DOC','IMP' ]

        Any.requireIsTextNonEmpty( msgType )
        Any.requireMsg( msgType in whitelist,
                        'invalid message type, must be one out of ' + \
                        ', '.join(whitelist) )

        self._msgType = msgType


    def setMessage( self, message ):
        """
            The reason for the installation shown to the other users.

            It is useful if you also state implications or sideeffects which
            the users should note. Do not necessarily write what you changed
            but what the users will experience, e.g. a certain bug was
            fixed rather than "added some condition to a regular expression".
        """
        Any.requireIsTextNonEmpty( message )
        Any.requireMsg( len( message ) < 2000, 'message must not exceed 2000 characters' )


        # replace newlines by blanks
        message = message.replace( '\n', ' ' )


        # 2010-07-22  Marijke Stein
        #
        # If the message is sth. like 'NEW: ....', assume that the message
        # type is given in-line.
        chkMsgType = message[:3]

        if chkMsgType == 'NEW' or chkMsgType == 'FIX' or chkMsgType == 'DOC':
            self.setMsgType( chkMsgType )
            self._message = message[5:]
        else:
            self._message = message


    def getLogContent( self ):
        """
            Returns a string representation of the whole message as it will
            be written to the logfile.
        """
        # Note: On Windows os.path.join() uses backslash '\'. But the logfile
        #       format is specified using forward slashes, f.i. used by
        #       GlobalInstallLog.php for parsing.

        now  = datetime.now()
        data = dict()

        data['date']           = now.strftime( "%Y-%m-%d" )
        data['time']           = now.strftime( "%H:%M:%S" )
        data['package']        = self._packageCategory + '/' + self._packageName + '/' + self._packageVersion
        data['maintainer']     = self._maintainer
        data['isFirstInstall'] = self._isFirstInstall
        data['msgType']        = self._msgType
        data['message']        = saxutils.escape(self._message)


        result= '''<GlobalInstallLog>
    <date>%(date)s</date>
    <time>%(time)s</time>
    <package>%(package)s</package>
    <maintainer>%(maintainer)s</maintainer>
    <isFirstInstall>%(isFirstInstall)s</isFirstInstall>
    <msgType>%(msgType)s</msgType>
    <message>%(message)s</message>
</GlobalInstallLog>\n''' % data

        return result


    def getFileName( self ):
        """
            Returns the path to the logfile where the data will be stored.
        """
        Any.requireIsTextNonEmpty( self._fileName )

        return self._fileName


    def setFileName( self, fileName ):
        """
            You may specify an output file path (e.g. for debugging
            purposes).
        """
        Any.requireIsTextNonEmpty( fileName )

        self._fileName = fileName


    def getInfoTable( self ):
        """
            Prints a summary of all data (e.g. for debugging purposes).
        """
        table  = "------------------\n"
        table += "Log entry details:\n"
        table += "------------------\n\n"

        table += "%-20s: %s\n" % ( 'category',        self._packageCategory )
        table += "%-20s: %s\n" % ( 'package name',    self._packageName )
        table += "%-20s: %s\n" % ( 'package version', self._packageVersion )
        table += "\n"
        table += "%-20s: %s\n" % ( 'maintainer',      self._maintainer )
        table += "%-20s: %s\n" % ( 'date',            self._date )
        table += "%-20s: %s\n" % ( 'first install',   self._isFirstInstall )
        table += "%-20s: %s\n" % ( 'message type',    self._msgType )
        table += "%-20s: %s\n" % ( 'message',         self._message )
        table += "\n"

        return table


    def writeFile( self, dryRun = False ):
        """
            Performs the actual writing of the log data to the file.

            If 'dryRun' is True no file will be written but the theoretical
            fileName and its content is printed to stdout. No physical
            writes are performed.
        """
        fileName = self.getFileName()
        content  = self.getLogContent()


        if dryRun:
            print( "fileName:", fileName )
            print( "content:", content )
        else:
            dirName = os.path.dirname( fileName )

            if not os.path.isdir( dirName ):
                mkdir( dirName )
                logging.debug( 'chmod 0777 %s', dirName )
                os.chmod( dirName, 0o0777 )

            setFileContent( fileName, content )
            logging.debug( 'chmod 0644 %s', fileName )
            os.chmod( fileName, 0o644 )


# EOF
