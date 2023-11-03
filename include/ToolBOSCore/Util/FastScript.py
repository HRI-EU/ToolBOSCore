# -*- coding: utf-8 -*-
#
#  convenience functions for frequently used scripting operations
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


import getpass
import logging
import os
import platform
import re
import shutil
import socket
import sys

from ToolBOSCore.Util import Any


#----------------------------------------------------------------------------
# Filesystem access
#----------------------------------------------------------------------------


def getDirsInDir( path = '.', excludePattern = None, onError = None ):
    r"""
        Return all directories within a specified one, except "." and "..".
        You may specify a regular expression for directories to be excluded:

        path:           absolute or relative path to directory

        excludePattern: regular expression object that will be
                        used to match against the found element, e.g.:

                        excludePattern = re.compile( "\d+.\d+" )
                        dirList = getDirsInDir( "/tmp", excludePattern )

        onError:        You may pass a function callback that will be called
                        upon errors, e.g. permission denied. This function needs
                        to take a single path parameter. If omitted, an
                        OSError will be raised upon errors.

        Returns a list of all directories (except "." and "..") within the
        specified path. If the directory does not exist, is empty or if all
        subdirectories match the exclude-blacklist then the result list will
        be empty.

    """
    Any.requireIsTextNonEmpty( path )
    subdirList = []

    if not os.path.isdir( path ):
        return subdirList

    try:
        for item in os.listdir( path ):
            if os.path.isdir( os.path.join( path, item ) ):
                if excludePattern:
                    if excludePattern.search( item ) is None:
                        # exclude pattern does not match, so file can be added
                        subdirList.append( item )
                    else:
                        # exclude pattern matches --> skip
                        pass
                else:
                    subdirList.append( item )
    except OSError:
        if onError:
            onError( path )
        else:
            raise

    return subdirList


def getDirsInDirRecursive( path = '.',
                           excludePattern = None,
                           keepSubDirs    = True,
                           onError        = None ):
    r"""
        Unlike to FastScript.getDirsInDir() this one recursively returns all
        directories within a given one. You may specify a regular expression
        for directories to be excluded. If "keepSubDirs" is True the path to
        the subdirectories will be preserved, if False only the leaf names
        will be returned.

        'excludePattern' must be a regular expression object that will be
        used to match against the found element, e.g.:

            excludePattern = re.compile( r"\d+.\d+" )
            dirList = getDirsInDirRecursive( "/tmp", excludePattern )

        If the directory does not exist, is empty or if all subdirectories
        match the exclude-blacklist then the result list will be empty.

        You may pass a function callback that will be called upon errors,
        e.g. permission denied. This function needs to take a single
        path parameter. If omitted, an OSError will be raised upon errors.
    """
    Any.requireIsTextNonEmpty( path )
    result = []

    if not os.path.isdir( path ):
        return result

    for item in os.listdir( path ):
        # skip symlinks which are also returned by os.listdir():
        joinedPath = os.path.join( path, item )

        if os.path.islink( joinedPath ):
            continue

        if os.path.isdir( joinedPath ):
            if excludePattern is None or \
               ( excludePattern is not None and excludePattern.search( item ) is None ):

                subDirList = []

                try:
                    subDirList = getDirsInDirRecursive( joinedPath,
                                                        excludePattern,
                                                        keepSubDirs,
                                                        onError )
                except OSError:
                    if onError:
                        onError( joinedPath )
                    else:
                        raise

                if keepSubDirs == True or len( subDirList ) == 0:
                    result.append( joinedPath )

                result.extend( subDirList )

    return result


def getFilesInDir( path, excludePattern = '' ):
    """
        Returns all files within a specified directory. You may specify a
        regular expression for filenames to be excluded.

        This function is pretty equal to Python's glob.glob() and might be
        removed in the future.
    """
    Any.requireIsTextNonEmpty( path )
    subdirList = []

    if not os.path.isdir( path ):
        return subdirList

    for item in os.listdir( path ):
        if os.path.isfile( os.path.join( path, item ) ):
            if excludePattern == '' or re.search( excludePattern, item ) is None:
                subdirList.append( item )

    return subdirList


def getFilesInDirRecursive( path, excludePattern = None ):
    """
        Returns a set of all files that can be recursively found under 'path'.

        'excludePattern' must be a regular expression object that will be
        used to exclude certain directories (such as "build" and ".svn") in
        the following example:

            excludePattern = re.compile( "(build|.svn)" )
            fileList = getFilesInDirRecursive( "Package/1.0", excludePattern )
    """
    result  = set()
    subDirs = getDirsInDirRecursive( path, excludePattern )

    # files directly within 'path'
    for fileName in getFilesInDir( path ):
        result.add( os.path.join( path, fileName ) )

    # files within subdirectories
    for subDir in subDirs:
        for fileName in getFilesInDir( subDir ):
            result.add( os.path.join( subDir, fileName ) )

    return result


def changeDirectory( path ):
    """
        Changes the current working directory.
    """
    logging.debug( 'cd %s', path )
    os.chdir( path )


def rename( src, dst ):
    """
        Renames/moves a files from "src" path to "dst" path.

        In contrast to Python's os.rename() function this checks the
        validity of the "src" filename first, and requires that the "dst"
        file has been successfully written.
    """
    Any.requireIsTextNonEmpty( src )
    Any.requireIsTextNonEmpty( dst )
    Any.requireIsFile( src )

    dstDir = os.path.dirname( dst )
    mkdir( dstDir )

    os.rename( src, dst )
    Any.requireIsFile( dst )


def remove( path, dryRun=False, ignoreErrors=False ):
    """
        Removes/unlinks the file or directory "path". If "path" is a
        directory, it will be deleted recursively (caution!).
    """
    if os.path.isfile( path ) or os.path.islink( path ):

        if dryRun:
            logging.debug( '[DRY-RUN] rm %s', path )
        else:
            logging.debug( 'rm %s', path )
            os.remove( path )

    elif os.path.isdir( path ):

        if dryRun:
            logging.debug( '[DRY-RUN] rm -R %s', path )
        else:
            logging.debug( 'rm -R %s', path )
            shutil.rmtree( path, ignoreErrors )


def copy( src, dst ):
    """
        If 'src' is a file, it will be copied. In case of symlinks the
        content (!) is copied, not the link itself.

        If 'src' is a directory, it will be copied recursively.
    """
    if os.path.isdir( src ):
        logging.debug( 'cp -R %s %s', src, dst )
        shutil.copytree( src, dst )
    else:
        logging.debug( 'cp %s %s', src, dst )
        shutil.copy2( src, dst )    # this also copies file meta-infos


def copyWithRetry( src, dst, maxAttempts=3, waitSeconds=2 ):
    """
        Decorator for copy() which attempts to re-try the copy operation
        for the given amount of attempts, with the given delay time in
        between.

        This is a not-so-nice but practical workaround for NFS hiccups.
    """
    import time

    Any.requireIsTextNonEmpty( src )
    Any.requireIsTextNonEmpty( dst )
    Any.requireIsInRange( maxAttempts, 1, 100 )
    Any.requireIsInRange( waitSeconds, 1, 3600 )

    i = 0

    while i < maxAttempts:

        i += 1

        try:
            copy( src, dst )
            break                   # we managed to get here --> success

        except ( FileNotFoundError, OSError ) as e:
            logging.debug( 'problem while copying: %s', e )

            if i >= maxAttempts:
                raise

            else:
                logging.debug( 'trying again in %ss...', waitSeconds )
                time.sleep( waitSeconds )


def link( target, symlink, dryRun=False ):
    """
        Creates a symlink, incl. all the necessary paths to it,
        and also prints a debug message.
    """
    Any.requireIsTextNonEmpty( symlink )
    Any.requireIsTextNonEmpty( target )        # allow initially broken links
    Any.requireIsBool( dryRun )

    # create destination directory (if it does not exist, yet)
    if not dryRun:
        mkdir( os.path.dirname( symlink ) )

    # remove any existing link under that name (if existing)
    if not dryRun:
        remove( symlink )

    # create symlink
    if dryRun:
        logging.debug( '[DRY-RUN] ln -s %s %s', target, symlink )
    else:
        logging.debug( 'ln -s %s %s', target, symlink )
        os.symlink( target, symlink )


def mkdir( path, verbose=False ):
    """
        Creates the directory "path", with all intermediate directories to
        this path if they do not exist, yet (like the "mkdir -p <path>" on
        the GNU/Linux shell).

        This is a convenience wrapper around os.makedirs(): If the directory
        already exists this function returns silently.

        If the directory can't be created, an exception will be thrown.
    """
    Any.requireIsText( path )

    if not path:
        return

    if verbose:
        logging.info( 'mkdir -p %s', path )
    else:
        logging.debug( 'mkdir -p %s', path )

    try:
        os.makedirs( path )
    except ( AssertionError, OSError ) as details:

        if details.errno == 17:                     # 17 = directory exists
            # ensure it's really a directory and not a file
            Any.requireIsDir( path )
        else:
            raise


def getFileOwner( path ):
    """
        Returns the username (if possible) of the owner of the specified
        file or directory. If the username cannot be retrieved, the
        numerical user ID will be used as fallback.
    """
    from pwd import getpwuid

    Any.requireIsTextNonEmpty( path )

    ownerID   = os.stat( path ).st_uid
    ownerName = getpwuid( ownerID ).pw_name

    return ownerName


def printPermissionDenied( path ):
    logging.warning( '%s: Permission denied', path )


def ignore( _ ):
    pass


def getDirSize( path ):
    """
        Returns the size occupied by a certain directory and all its
        files and subdirectories inside.

        This is an equivalent to "du -s" on the shell.

        Size is returned in Bytes.
    """
    size = 0
    for root, dirs, files in os.walk( path ):
        for f in files:
            fullPath = os.path.join( root, f )
            try:
                size +=  os.path.getsize( fullPath )
            except OSError:
                logging.debug( "can't stat: %s", fullPath )

    return size


#----------------------------------------------------------------------------
# File I/O
#----------------------------------------------------------------------------


def getFileContent( filename, splitLines = False, asBinary=False ):
    """
        Returns the whole content of a file as a single long string
        (default) or as a list of lines if "splitLines=True".
        If `asBinary` is set to True, the contents of the file are returned as
        a byte array.
    """
    if not os.path.isfile( filename ):
        raise IOError( "%s: No such file" % filename )

    if asBinary:
        mode = 'rb'
    else:
        mode = 'r'

    with open( filename, mode ) as f:
        logging.debug( 'reading file: %s', filename )
        return f.readlines() if splitLines else f.read()


def setFileContent( filename, content ):
    """
        Writes "content" (of type 'str' or 'unicode') to the specified file.
    """
    Any.requireIsTextNonEmpty( filename )
    Any.requireIsText( content )

    dirName = os.path.dirname( filename )

    if dirName and not os.path.isdir( dirName ):
        mkdir( dirName )

    f = open( filename, "w" )
    f.write( content )
    f.close()


def serializeToFile( filename, obj ):
    """
        This function serializes 'object' into 'filename'.

        Attention: If the specified file exists it will be overwritten.
    """
    from pickle import Pickler

    from ToolBOSCore.External.atomicfile import AtomicFile


    Any.requireIsTextNonEmpty( filename )

    with AtomicFile( filename, 'wb' ) as f:          # Pickle uses binary streams
        Pickler( f ).dump( obj )


def deserializeFromFile( filename ):
    """
        Deserializes the content from 'filename' and returns it as
        Python object.
    """
    from pickle import Unpickler
    Any.requireIsTextNonEmpty( filename )

    try:
        f = open( filename, 'rb' )              # Pickle uses binary streams
        obj = Unpickler( f ).load()
        f.close()
    except EOFError as details:
        raise IOError( details )

    return obj


def findFiles( path, regexp=None, ext=None, excludeSVN=True ):
    """
        Returns a list with all files in 'path' whoms names match a certain
        pattern. Pattern can be:

          * regexp:   a precompiled regular expression object
          * ext:      file has a certain extension, e.g. ".c" (mind the dot!)

        Note that both 'regexp' and 'ext' can be scalar values as well
        as lists. In such case, any of the expression (or extension) must
        match.

        If 'excludeSVN=True', files under ".svn" are skipped.
    """
    fileList = []

    # recursively search for files
    for root, dirs, files in os.walk( path ):

        for entry in files:
            path    = os.path.join( root, entry )
            fileExt = os.path.splitext( entry )[1]

            # skip SVN files (if requested)
            if excludeSVN == True and path.find( '.svn' ) != -1:
                continue

            # found a file with requested extension
            if isinstance(ext,str) and ext == fileExt:
                fileList.append( path )

            elif isinstance(ext,list) or isinstance(ext,tuple):
                if fileExt in ext:
                    fileList.append( path )

            elif isinstance(regexp,list) or isinstance(regexp,tuple):
                for exp in regexp:
                    if exp.search( entry ):
                        fileList.append( path )
                        break

            # found a file matching regexp
            elif regexp:
                if regexp.search( entry ):
                    fileList.append( path )


    return fileList


#----------------------------------------------------------------------------
# Inter-process communication
#----------------------------------------------------------------------------


def execFile( filename ):
    """
        Evaluates/executes the content of the specified file which must
        contain valid Python code.

        If the code in this file declares any variables then their values
        are returned in a map.
    """
    Any.requireIsTextNonEmpty( filename )

    # redundant check removed for performance reasons:
    # open() itself will raise an IOError if file not present,
    # avoid superfluous underlying stat() which is especially noticable
    # when batch-loading a number of files
    #
    # if not os.path.isfile( filename ):
    #     raise IOError( "%s: No such file" % filename )

    result = {}
    with open( filename ) as fd:
        exec( fd.read(), None, result)

    return result


def execProgram( cmd, workingDir = None, host = 'localhost',
                 stdin = None, stdout = None, stderr = None,
                 username = None, encoding = 'utf8' ):
    """
        Executes another program/command.

        You may redirect input/output streams by providing StringIO instances.
        The input argument is passed to Popen.communicate() and thus to the subprocess’s stdin.
        If used it must be a byte sequence, or a string if encoding is specified.

        If 'host' is different from the default 'localhost' or the actual
        hostname, an SSH tunnel will be opened and the command executed
        remotely. 'host' can also be an IPv4/IPv6 address.

        A 'username' can be specified to execute as a certain user. This
        is most useful via SSH, on local machines only 'root' can do that.
        Normal users will get prompted for a password in such case.

        Restrictions on SSH:
          * no check if 'workingDir' exists
          * server must listen on default port 22
          * authorized_keys must be configured with no passphrase

        Returns the exit code of the program. Raises an exception if it is
        not zero.
    """
    Any.requireIsTextNonEmpty( cmd )

    from shlex      import split
    from subprocess import CalledProcessError
    from subprocess import PIPE
    from subprocess import Popen
    from subprocess import STDOUT

    cmd, localWorkingDir = getCommandLine( cmd, workingDir, host, username )
    logging.debug( 'executing: %s', cmd )

    # execvp() will not accept unicode strings
    try:
        posix = platform.system().lower() != 'windows'

        if posix:
            # When running on Windows, there is no need to split the
            # command line with shlex.
            # See discussion on TBCORE-1496
            cmd   = split( cmd, posix=posix )   # array of parameters
    except ValueError as details:
        logging.error( 'parsing command line failed: %s', cmd )
        logging.error( details )
        raise ValueError( details )

    inData    = None
    inStream  = None
    outStream = None
    errStream = None

    if stdin:
        inStream = PIPE

        if encoding is None:
            inData = stdin
        else:
            inData = stdin.read()

    if stdout:
        outStream = PIPE

    if stderr:
        if stdout == stderr:
            errStream = STDOUT
        else:
            errStream = PIPE


    p = Popen( cmd, stdin=inStream, stdout=outStream,
               stderr=errStream, cwd=localWorkingDir,
               encoding=encoding )


    ( outData, errData ) = p.communicate( inData )

    sys.stdout.flush()
    sys.stderr.flush()

    if stdout and outData:
        if encoding is None:
            stdout.writelines( str( outData ) )
        else:
            stdout.writelines( outData )

        stdout.flush()

    if stderr and errData:
        stderr.writelines( errData )
        stderr.flush()

    if p.returncode != 0:
        raise CalledProcessError( p.returncode, cmd )

    return p.returncode


def getCommandLine( cmd, workingDir=None, host=None, user=None ):
    """
        Returns a tuple of the appropriate SSH-wrapped commandline to
        execute the given command on the specified host, and the working
        directory to pass to Popen(), hence:

           ( command, workingDir )

        If 'host' is the current machine, the plain 'cmd' will be
        returned and the workingDir will be None.
    """
    Any.requireIsTextNonEmpty( cmd )

    if host is not None:
        Any.requireIsTextNonEmpty( host )

    if workingDir is not None:
        Any.requireIsTextNonEmpty( workingDir )


    localHostname = socket.gethostname()

    if host in ( None, 'localhost', '127.0.0.1', '::1', localHostname ):

        resultWorkingDir = workingDir

        if user:
            resultCmd  = 'su - %s -c "%s"' % ( user, cmd )
        else:
            resultCmd  = cmd

    else:

        if not workingDir:
            workingDir = os.getcwd()

        # disable fingerprint check to avoid interactive prompt
        # in case the hostkey has changed
        sshOpts = '-o BatchMode=yes -o StrictHostKeyChecking=no'

        if user:
            resultCmd = "ssh %s -X %s@%s 'cd %s; %s'" % \
                     (sshOpts, user, host, workingDir, cmd)
        else:
            resultCmd = "ssh %s -X %s 'cd %s; %s'" % \
                     (sshOpts, host, workingDir, cmd)


        # unset the working dir. so that Popen() will not get it as
        # argument (because we don't want to set workingDir of the local
        # SSH process, but instead we have injected the "cd ..." into the
        # remote command above)
        resultWorkingDir = None


    return resultCmd, resultWorkingDir


def getEnv( varName=None ):
    """
        If called without parameter this function returns a deep copy of
        the whole environment map (not just references).

        If the parameter 'varName' is given it only returns a string with
        the value of that variable. If there is no such environment variable
        it will return 'None'.
    """
    if varName:
        try:
            return os.environ[ varName ]
        except KeyError:
            return None
    else:
        return os.environ


def getEnvChk( varName, default=None ):
    """
        Like FastScript.getEnv, with additional support for a default parameter.

        If the requested 'varName' is not found in the environment and no default
        parameter is specified, an EnvironmentError is raised.
    """
    Any.requireIsTextNonEmpty( varName )

    value = getEnv( varName )

    if value is None:
        if default is None:
            if not Any.isTextNonEmpty( value ):
                raise EnvironmentError( '%s: empty environment variable' % varName )
        else:
            return default
    else:
        return value


def setEnv( varNameOrMap, varValue = '' ):
    """
        This function can be used to set the process environment variables.

        a) If 'varNameOrMap' is of type 'dict' (a whole map of environment
           variables mapped to their values), it will set the environment
           to this. The second parameter is ignored in such case.
               Please note that all environment variables will be modified,
           even those not present in the map (those effectively get deleted).

        b) If 'varNameOrMap' is of type "str" it will set an environment
           variable with this name. Optionally you can specify 'varValue' of
           type 'str' to assign a value to this environment variable.
    """
    if Any.isText( varNameOrMap ):                # set single variable
        logging.debug( 'export %s="%s"', varNameOrMap, varValue )
        os.environ[ varNameOrMap ] = varValue
    else:                                         # set whole map
        os.environ.clear()
        os.environ.update( varNameOrMap )


def setEnv_withExpansion( varName, varValue ):
    """
        This function can be used to set a particular process environment
        variable.

        Unlike setEnv(), which works verbatim, this function also searches
        for environment variables inside 'varValue' and in case replaces
        them first.

        Example:

            setEnv_withExpansion( 'MATLAB_ROOT',
                                  '${SIT}/External/Matlab/8.4' )

            setEnv_withExpansion( 'PATH',
                                  '${MATLAB_ROOT}/bin:${PATH}' )

            will first define MATLAB_ROOT as absolute path to Matlab/8.4
            (replacing ${SIT} by its current environment value)
            and in a second step prepend the absolute path to Matlab's
            "bin"-directory to the current value of ${PATH}.
    """
    Any.requireIsTextNonEmpty( varName )
    Any.requireIsTextNonEmpty( varValue )

    setEnv( varName, os.path.expandvars( varValue ) )


def unsetEnv( varName = False ):
    """
        This function can be used to delete all or a particular environment
        variable.

        a) If 'varName' is specified, it will only delete this environment
           variable.

           Please note: If the variable was already present before starting
           this process, it will still be present in your shell after
           terminating this process. Deleting environment variables from
           within Python will only have effect within this particular process.

        b) If the 'varName' parameter is omitted, all environment variables
           will be deleted (caution!). This might not be useful ;-)

        The function silently catches the exception if there is no variable
        with the given name.
    """
    if isinstance( varName, str ):                # remove single variable
        try:
            logging.debug( 'unset %s', varName )
            del os.environ[ varName ]
        except KeyError:
            pass
    else:
        os.environ.clear()                        # clear whole process env.


def appendEnv( varName, s ):
    """
        Adds 's' at the end of the existing value of the given env.var.
        If 'varName' was not defined it will be created.

        Example:
              append( 'PATH', ':/path/to/foo' )
    """
    Any.requireIsTextNonEmpty( varName )
    Any.requireIsText( s )

    oldValue = getEnv( varName )

    if oldValue:
        newValue = oldValue + s
    else:
        newValue = s

    setEnv( varName, newValue )


def prependEnv( varName, s ):
    """
        Adds 's' at the beginning of the existing value of the given env.var.
        If 'varName' was not defined it will be created.

        Example:
              prepend( 'PATH', '/path/to/foo:' )
    """
    Any.requireIsTextNonEmpty( varName )
    Any.requireIsText( s )

    oldValue = getEnv( varName )

    if oldValue:
        newValue = s + oldValue
    else:
        newValue = s

    setEnv( varName, newValue )


#----------------------------------------------------------------------------
# Security & Permissions
#----------------------------------------------------------------------------


def chmodRecursive( path, dirPermission, filePermission ):
    """
        Changes the attributes (permissions) of the file or directory
        <path> recursively so that the given path has permissions as specified in
        <dirPermission> and <filePermission>.

        For example, to make a directory writeable for all HRI-EU members:
        FastScript.setPermissions( '/path', 0o775, 0o664 )

        ATTENTION: <dirPermission> and <filePermission> needs to be passed as octal number,
         with a leading '0o' prefix to support Python 2 and 3.
    """
    Any.requireIsTextNonEmpty( path )
    Any.requireIsIntNotZero( dirPermission  )
    Any.requireIsIntNotZero( filePermission )

    for dirpath, dirs, files in os.walk( path ):
        for item in dirs:
            path = os.path.join( dirpath, item )
            logging.debug( "chmod %o %s", dirPermission, path )
            os.chmod( path, dirPermission )

        for item in files:
            path = os.path.join( dirpath, item )
            logging.debug( "chmod %o %s", filePermission, path )
            os.chmod( os.path.join( dirpath, item ), filePermission )


def readOnlyChmod( path ):
    """
        Set read only permissions to the given path recursively.
    """
    Any.requireIsTextNonEmpty( path )

    dirPerms  = 0o555
    filePerms = 0o444

    chmodRecursive( path, dirPerms, filePerms )


def readWriteChmod( path ):
    """
        Set read-write permissions to the given path recursively.
    """
    Any.requireIsTextNonEmpty( path )

    dirPerms  = 0o775
    filePerms = 0o664

    chmodRecursive( path, dirPerms, filePerms )


def setGroupPermission( path, groupName, mode ):
    """
        Changes the attributes (permissions) of the file or directory
        <path> so that the given group has permissions as specified in
        <mode>.

        For example, to make a directory writeable for all HRI-EU members:
        FastScript.setGroupPermission( '/path', 'users', 0775 )

        ATTENTION: <mode> needs to be passed as octal number with a
                   leading zero!

        If an operation failed e.g. due to insufficient rights it will be
        silently ignored! If you need to catch such cases please use
        the 'os' module directly. We are also not checking if <path>
        exists at all.
            The only known exception will be if the specified group
        does not exist.
    """
    from grp import getgrnam

    Any.requireIsTextNonEmpty( path )    # do not check if exists
    Any.requireIsTextNonEmpty( groupName )
    Any.requireIsIntNotZero( mode )

    groupID = getgrnam( groupName ).gr_gid

    try:
        os.chmod( path, mode )
    except OSError:
        pass

    try:
        os.chown( path, -1, groupID )     # -1 == don't change userID
    except OSError:
        pass


def chgrpRecursive( path, groupName ):
    """
        Changes the group of the file or directory <path> recursively
        so that the given path and files are owned by the group specified in
        <groupName>. Given group <groupName> has to exist.

        For example, to make a directory owned by the group 'hriasc':
        FastScript.chgrpRecursive( '/path', 'hriasc' )
    """
    from grp import getgrnam

    Any.requireIsTextNonEmpty( path )
    Any.requireIsTextNonEmpty( groupName )

    try:
        groupid = getgrnam( groupName ).gr_gid
    except KeyError:
        raise OSError( '%s: No such group' % groupName )

    userid = -1
    os.chown( path, userid, groupid )

    for dirpath, dirs, files in os.walk( path ):
        for item in dirs:
            path = os.path.join( dirpath, item )
            logging.debug( "chgrp %s %s", groupName, path )
            os.chown( path, userid, groupid )

        for item in files:
            path = os.path.join( dirpath, item )
            logging.debug( "chgrp %s %s", groupName, path )
            os.chown( os.path.join( dirpath, item ), userid, groupid )


def getCurrentUserID():
    """
        Returns the UID of the current process.
    """
    from pwd import getpwnam

    return getpwnam( getpass.getuser() ).pw_uid


def getCurrentUserName():
    """
        Returns the login name for the UID of the current process.
    """
    return getpass.getuser()


def getCurrentUserFullName():
    """
        Returns the full name for the UID of the current process.
    """
    from pwd import getpwnam

    return getpwnam( getpass.getuser() ).pw_gecos


def getCurrentGroupID():
    """
        Returns the primary GID of the user running the current process.
    """
    from pwd import getpwnam

    return getpwnam( getpass.getuser() ).pw_gid


def getCurrentGroupName():
    """
        Returns the primary group name of the user running the current
        process.
    """
    from grp import getgrgid

    return getgrgid( getCurrentGroupID() ).gr_name


#----------------------------------------------------------------------------
# String processing
#----------------------------------------------------------------------------


def expandVar( string, varName ):
    """
        This function retrieves the value of the environment variable
        "varName". Then it searches for "${varName}" in "string" and
        replaces it with the actual value, e.g.:

            str  = '${SIT}/DevelopmentTools/ToolBOSCore'
            path = FastScript.expandVar( str, 'SIT' )

        "path" will then be e.g. "/hri/sit/latest/DevelopmentTools/ToolBOSCore"
    """
    Any.requireIsTextNonEmpty( string )
    Any.requireIsTextNonEmpty( varName )
    value = getEnv( varName )

    if not value:
         return string
    else:
         return string.replace( "${" + varName + "}", value )


def expandVars( string ):
    """
        Loops over all environment variables in the process environment,
        and searches for "${varName}" in "string" and replaces it with the
        actual value, e.g.:

            str  = '${SIT}/users/${USER}'
            path = FastScript.expandVars( str )

        "path" will then be e.g. "/hri/sit/latest/users/torvalds".
    """
    Any.requireIsText( string )                 # might be empty

    if len(string) == 0:
        return string

    for varName, value in os.environ.items():
        string = string.replace( "${" + varName + "}", value )

    return string


def collapseVar( string, envName ):
    """
        This function retrieves the value of the environment variable
        "envName". Then it searches for this value in "string" and
        replaces it with "${envName}", e.g.:

            path   = "/hri/sit/latest/DevelopmentTools/ToolBOSCore"
            result = FastScript.collapseVar( path, 'SIT' )

        "result" will then be '${SIT}/DevelopmentTools/ToolBOSCore'
    """
    Any.requireIsTextNonEmpty( string )
    Any.requireIsTextNonEmpty( envName )
    envValue = getEnv( envName )

    # logging.info( envValue )
    # logging.info( type(envValue) )

    if not envValue:
        return string
    else:
        return string.replace( envValue, "${" + envName + "}" )


def countCharacters( string ):
    """
        Returns the number of different characters within given string.

        Example:  countCharacters( 'abcabc' ) would return 3.

        This is a re-implementation of PHP's count_chars() function.
    """
    Any.requireIsText( string )

    tmp = {}

    for char in string:
        try:
            tmp[ char ] += 1        # increment number of occurrences
        except KeyError:
            tmp[ char ] = 1         # first time found

    return len( tmp.keys() )


#----------------------------------------------------------------------------
# List processing
#----------------------------------------------------------------------------


def flattenList( nestedList ):
    """
        Flattens a nested list into a one-dimensional list.
    """
    from ToolBOSCore.External.Flatten import flatten

    Any.requireIsList( nestedList )
    return flatten( nestedList )


def removeDuplicates( aList ):
    """
        Removes all duplicate elements from a list.
    """
    from ToolBOSCore.External.f5 import f5

    Any.requireIsList( aList )
    return f5( aList )


def reduceList( nestedList ):
    """
        Flattens a nested list into a one-dimensional list and removes
        all duplicate elements.
    """
    Any.requireIsList( nestedList )
    resultList = flattenList( nestedList )
    resultList = removeDuplicates( resultList )

    return resultList


def getTreeView( nestedList, level = 0, levelPadding = '' ):
    """
        Returns a string representation of the given (optionally nested)
        list.

        The parameters 'level' and 'levelPadding' are only internally used
        for recursion and should not be set by the user.
    """
    Any.requireIsList( nestedList )
    result = ''

    if level > 20:              # loop guard
        raise ValueError

    for i, entry in enumerate( nestedList ):
        if Any.isText( entry ):
            entryPadding = levelPadding + '%c---' % _getTreeChar( nestedList, i )
            result += "%s%s\n" % ( entryPadding, entry )
        elif Any.isList( entry ):
            entryPadding = levelPadding + '%c   ' % _getTreeChar( nestedList, i )
            result += getTreeView( entry, level + 1, entryPadding )
        else:
            raise TypeError


    return result


#----------------------------------------------------------------------------
# Time functions
#----------------------------------------------------------------------------


def isoTime( dt=None ):
    """
        Returns a string with human-readable ISO 8601 time format of the
        provided datetime-instance (or current time if omitted).
    """
    import time

    if dt is None:
        dt = now()

    naive  = dt.strftime( '%Y-%m-%d %H:%M:%S' )
    offset = time.strftime( '%z' )

    return '%s %s' % ( naive, offset )


def now():
    """
        Returns the current time as datetime object.
    """
    from datetime import datetime

    return datetime.now()


def startTiming():
    """
        Returns a time object for measuring code execution times.
        In fact, it is the same as FastScript.now().
    """
    return now()


def stopTiming( startTime ):
    """
        Prints the elapsed time from 'startTime' to now.
        Useful for measuring code execution times.
    """
    import datetime

    Any.requireIsInstance( startTime, datetime.datetime )

    stopTime = now()
    logging.debug( 'elapsed time: %s', stopTime - startTime )


#----------------------------------------------------------------------------
# Misc
#----------------------------------------------------------------------------


def prettyPrintError( msg ):
    """
        Throws a SystemExit exception which shows 'msg' as red text on
        the console.
    """
    from textwrap import wrap

    Any.requireIsTextNonEmpty( msg )

    lines = wrap( msg )
    finalMsg = '\n\t' + '\n\t'.join( lines ) + '\n'

    raise SystemExit( "\033[1m%s\033[0m\n" % finalMsg )


def tryImport( modules ):
    """
        Checks that the provided modules can be imported.
        Stops with a message to the user if some are not found.
    """
    import importlib

    if Any.isText( modules ):
        modules = [ modules ]

    Any.requireIsIterable( modules )

    notFound = set()

    for moduleName in modules:
        Any.requireIsTextNonEmpty( moduleName )

        try:
            importlib.import_module( moduleName )
        except ModuleNotFoundError:
            notFound.add( moduleName )


    if notFound:
        raise SystemExit( 'Python module(s) not installed: %s' % \
                          ' '.join( sorted( notFound ) ) )


#----------------------------------------------------------------------------
# Private functions
#----------------------------------------------------------------------------


def _getTreeChar( searchList, index ):
    Any.requireIsList( searchList )
    lastStringIndex = _getLastStringInList( searchList )

    if index < lastStringIndex:
        treeChar = '|'
    elif index == lastStringIndex:
        treeChar = '`'
    else:
        treeChar = ' '

    return treeChar


def _getLastStringInList( searchList ):
    Any.requireIsList( searchList )
    index = 0

    for i in range( 0, len(searchList) ):
        if isinstance( searchList[i], str ):
            index = i

    return index


# EOF
