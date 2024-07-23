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


import atexit
import collections.abc
import getpass
import glob
import io
import logging
import os
import platform
import re
import shutil
import socket
import sys


#----------------------------------------------------------------------------
# Public functions for assertion (condition checking)
#----------------------------------------------------------------------------


def require( condition ):
    """
        Throws an AssertionError if 'condition' evaluates to False.
    """
    assert condition


def requireMsg( condition, msg='' ):
    """
        Throws an AssertionError if 'condition' evaluates to False.
        You may pass human-readable details in 'msg'.
    """
    assert condition, msg


def isOptional( dummy ):
    """
        Only for consistency with all the other is*() functions.

        Always returns True.
    """
    return True


def requireOptional( dummy ):
    """
        Explicitly flags a function parameter to be of no use or not
        being necessary to check at all.

        Python-equivalent of ANY_OPTIONAL() from ToolBOS library.
    """
    pass


def isNotNone( obj ):
    """
        Returns a boolean whether 'obj' references 'None'.
    """
    return obj is not None


def requireIsNotNone( obj, msg=None ):
    """
        Throws an AssertionError if 'obj' references 'None'.
    """
    if msg is None:
        msg = "variable must not be 'None'"

    requireMsg( isNotNone( obj ), msg )


def isBool( obj ):
    """
        Returns a boolean whether 'obj' is of type 'bool'.
    """
    return isinstance( obj, bool )


def requireIsBool( obj ):
    """
        Throws an AssertionError if 'obj' is not of type 'bool'.
    """
    requireMsg( isBool( obj ),
                "variable is of type %s, expected 'bool'" % type( obj ) )


def isInt( obj ):
    """
        Returns a boolean whether 'obj' is of type 'int'.
    """
    return isinstance( obj, int )


def requireIsInt( obj ):
    """
        Throws an AssertionError if 'obj' is not of type 'int'.
    """
    requireMsg( isInt( obj ),
                "variable is of type %s, expected 'int'" % type( obj ) )


def isIntNotZero( obj ):
    """
        Returns a boolean whether 'obj' of type 'int' and is not zero.
    """
    return isInt( obj ) and obj != 0


def requireIsIntNotZero( obj ):
    """
        Throws an AssertionError if 'obj' is not of type 'int' or is zero.
    """
    requireIsInt( obj )
    requireMsg( isIntNotZero( obj ),
                "variable must not be zero" )


def isInRange( obj, minimum, maximum ):
    """
        Returns a boolean whether 'obj' is a number and between
        min and max (including min/max limits).
    """
    requireMsg( isInt( obj ) or isFloat( obj ), "%s: Not a number" % obj )

    if maximum < minimum:
        mimumum, maximum = maximum, minimum             # swap values

    return minimum <= obj <= maximum


def requireIsInRange( obj, minimum, maximum ):
    """
        Throws an AssertionError if 'obj' is not of type 'int' or is not
        within min and max (including min/max limits).
    """
    requireMsg( isInRange( obj, minimum, maximum ),
                "%s: Not within expected range (%s .. %s)" %
                ( obj, minimum, maximum ) )


def isFloat( obj ):
    """
        Returns a boolean whether 'obj' is of type 'float'.
    """
    return isinstance( obj, float )


def requireIsFloat( obj ):
    """
        Throws an AssertionError if 'obj' is not of type 'float'.
    """
    requireMsg( isFloat( obj ),
                "variable is not of type 'float'" )


def requireIsString( obj ):
    """
        Throws an AssertionError if 'obj' is not of type 'string'.
    """
    requireMsg( isString( obj ),
                "variable is of type '%s', expected a string" % type(obj) )


def isString( obj ):
    """
        Returns a boolean whether 'obj' is of type 'str'.
    """
    return isinstance( obj, str )


isText        = isString
requireIsText = requireIsString


def isTextNonEmpty( obj ):
    """
        Returns True if 'obj':
          - is a string
          - its length is zero and
          - does not only contain whitespaces
        otherwise returns False.
    """
    return isText( obj ) and len( obj ) > 0  and obj.strip() != ''


def requireIsTextNonEmpty( obj ):
    """
        Throws an AssertionError if:
          - 'obj' is not a string
          - its length is zero or
          - only contains whitespaces
    """
    requireIsText( obj )
    requireMsg( isTextNonEmpty( obj ),
                "string must not be empty" )


def isList( obj ):
    """
        Returns a boolean whether 'obj' is of type 'list'.
    """
    return isinstance( obj, list )


def requireIsList( obj ):
    """
        Throws an AssertionError if 'obj' is not of type 'list'.
    """
    requireMsg( isList( obj ),
                "variable is of type %s, expected 'list'" % type( obj ) )


def isListNonEmpty( obj ):
    """
        Returns a boolean whether 'obj' contains elements.
    """
    return isList( obj ) and len( obj ) > 0


def requireIsListNonEmpty( obj ):
    """
        Throws an AssertionError if 'obj' is not a list or does not contain
        elements.
    """
    requireIsList( obj )
    requireMsg( isListNonEmpty( obj ),
                'list must not be empty' )


def isDict( obj ):
    """
        Returns a boolean whether 'obj' is of type 'dict'.
    """
    return isinstance( obj, dict )


def requireIsDict( obj ):
    """
        Throws an AssertionError if 'obj' is not of type 'dict'.
    """
    requireMsg( isDict( obj ),
                "variable is of type %s, expected 'dict'" % type( obj ) )


def isDictNonEmpty( obj ):
    """
        Returns a boolean whether 'dict' is a list and contains
        elements.
    """
    return isDict( obj ) and len( obj ) > 0


def requireIsDictNonEmpty( obj ):
    """
        Throws an AssertionError if 'obj' is not a dict or does not contain
        elements.
    """
    requireIsDict( obj )
    requireMsg( isDictNonEmpty( obj ),
                'dict must not be empty' )


def isTuple( obj ):
    """
        Returns a boolean whether 'obj' is of type 'tuple'.
    """
    return isinstance( obj, tuple )


def requireIsTuple( obj ):
    """
        Throws an AssertionError if 'obj' is not of type 'tuple'.
    """
    requireMsg( isTuple( obj ),
                "variable is of type %s, expected 'tuple'" % type( obj ) )


def isIterable( obj ):
    """
        Returns a boolean whether 'obj' is iterable, e.g. is a collection,
        a collection view, a string, a generator, etc.
    """
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def requireIsIterable( obj ):
    """
        Throws an AssertionError if 'obj' is not iterable, e.g. of type
        'list' or 'tuple'.
    """
    requireMsg( isIterable( obj ),
                "type %s is not iterable" % type( obj ) )


def isSet( obj ):
    """
        Returns a boolean whether 'obj' is of either type 'set' or
        'frozenset'.
    """
    return isinstance( obj, set ) or isinstance( obj, frozenset )


def requireIsSet( obj, msg=None ):
    """
        Throws an AssertionError if 'obj' is neither of type 'set' nor
        'frozenset'.
    """
    msg = msg or "variable is of type %s, expected 'set' or 'frozenset'" % type( obj )
    requireMsg( isSet( obj ), msg )


def isIn( obj, container ):
    """
        Returns a boolean whether 'obj' is present in 'container'.
    """
    return obj in container


def requireIsIn( obj, container, msg=None ):
    """
        Throws an AssertionError if 'obj' is not present in 'container'.
    """

    msg = msg or '{}: No such object in {}'.format( obj, container )

    requireMsg( isIn( obj, container ), msg )


def isFileHandle( handle ):
    """
        Returns a boolean whether 'handle' points to an open file handle.
    """
    return isinstance( handle, io.IOBase )

def isFile( path ):

    """
        Returns a boolean whether 'path' points to a regular file.
    """
    return os.path.isfile( path )


def requireIsFile( path ):
    """
        Throws an AssertionError if 'path' does not point to a regular file.
    """
    requireIsTextNonEmpty( path )

    requireMsg( not os.path.isdir( path ),
                path + ": Is a directory, expected regular file" )

    requireMsg( isFile( path ), path + ": No such file" )


def isEmptyFile( path ):
    """
        Returns a boolean whether 'path' points to a regular file.

        Additionally, the size of the file must be zero.
    """
    requireIsText( path )
    return os.path.getsize( path ) == 0


def isFileNonEmpty( path ):
    """
        Returns a boolean whether 'path' points to a regular file.

        Additionally, the size of the file must be greater than zero.
    """
    requireIsText( path )
    return isFile( path) and os.path.getsize( path ) > 0


def requireIsFileNonEmpty( path ):
    """
        Throws an AssertionError if 'path' does not point to a regular file.

        Additionally, the size of the file must be greater than zero.
    """
    requireIsFile( path )
    requireMsg( isFileNonEmpty( path ), path + ': File is empty' )


def isDir( path ):
    """
        Returns a boolean whether 'path' points to a directory.
    """
    requireIsTextNonEmpty( path )
    return os.path.isdir( path )


def requireIsDir( path ):
    """
        Throws an AssertionError if 'path' does not point to a directory.
    """
    requireIsTextNonEmpty( path )

    requireMsg( os.path.exists( path ), path + ": No such directory" )
    requireMsg( isDir( path ), path + ": Not a directory" )


def isEmptyDir( path ):
    """
        Returns a boolean whether 'path' points to an empty directory.
    """
    requireIsTextNonEmpty( path )
    return glob.glob( path + '/*' ) == []


def requireIsEmptyDir( path ):
    """
        Throws an AssertionError if 'path' points to an empty directory.
    """
    requireIsTextNonEmpty( path )
    requireIsDir( path )
    requireMsg( isEmptyDir( path ), path + ": Directory is empty" )


def isDirNonEmpty( path ):
    """
        Returns a boolean whether 'path' points to a directory.
    """
    requireIsTextNonEmpty( path )
    return glob.glob( path + '/*' ) != []


isNonEmptyDir = isDirNonEmpty


def requireIsDirNonEmpty( path ):
    """
        Throws an AssertionError if 'path' does not point to a directory.
    """
    requireIsTextNonEmpty( path )
    requireIsDir( path )
    requireMsg( isDirNonEmpty( path ), path + ": Directory is empty" )


requireIsNonEmptyDir = requireIsDirNonEmpty


def isSymlink( path ):
    """
        Returns a boolean whether 'path' points to a symlink.
    """
    return os.path.islink( path )


def requireIsSymlink( path ):
    """
        Throws an AssertionError if 'path' does not point to a symlink.
    """
    requireIsTextNonEmpty( path )
    requireMsg( isSymlink( path ), path + ": Is not a symlink" )


def isExisting( path ):
    """
        Returns a boolean whether 'path' exists.
    """
    return os.path.exists( path )


def requireIsExisting( path ):
    """
        Throws an AssertionError if 'path' does not exist.
    """
    requireIsTextNonEmpty( path )
    requireMsg( isExisting( path ), path + ": No such file or directory" )


def requireIsNotExisting( path ):
    """
        Throws an AssertionError if 'path' already exists.
    """
    requireIsTextNonEmpty( path )
    requireMsg( not isExisting( path ), path + ": Already exists" )


def isMatching( string, pattern ):
    """
        Returns a boolean whether 'string' matches the given
        regular expression.

        Example:

          requireIsMatching( 'foo', '^oo' )

        will fail because 'foo' does not start with 'oo'.
    """
    requireIsTextNonEmpty( string )
    requireIsTextNonEmpty( pattern )

    return bool( re.match( pattern, string ) )


def requireIsMatching( string, pattern ):
    """
        Throws an AssertionError if 'string' does not match the given
        regular expression.

        Example:

          requireIsMatching( 'foo', '^oo' )

        will fail because 'foo' does not start with 'oo'.
    """
    requireIsTextNonEmpty( string )
    requireIsTextNonEmpty( pattern )

    requireMsg( isMatching( string, pattern ),
                "'%s' does not match expected regular expression '%s'" %
                ( string, pattern ) )


def isCallable( obj ):
    """
        Returns a boolean whether 'obj' is callable (read as function
        or method).
    """
    return callable( obj )


def requireIsCallable( obj ):
    """
        Throws an AssertionError if 'obj' is not callable (read as function
        or method).

        Example:
          func = getattr( CMakeWrapper, taskName )
          requireIsCallable( func )
    """
    requireMsg( isCallable( obj ),
                '%s: Not a callable function or method (%s)' %
                ( str( obj ), type( obj ) ) )


def isInstance( obj, classType ):
    """
        Returns a boolean whether 'obj' is an instance of class
        'classType' (not as string, pass as real class!).
    """
    return isinstance( obj, classType )


def requireIsInstance( obj, classType, msg=None ):
    """
        Throws an AssertionError if 'obj' is not instance of class
        'classType' (not as string, pass as real class!).

        Example: function requires string argument

          def myFunction( s ):
            requireIsInstance( s, str )
            [...]
    """
    requireIsNotNone( obj )

    msg = msg or '{} ({}): Not an instance of class "{}"'.format( str( obj ), type( obj ), classType )

    requireMsg( isInstance( obj, classType ), msg )


def isInstanceOrNone( obj, classType ):
    """
        Returns a boolean whether 'obj' is instance of class
        'classType' (not as string, pass as real class!), or None.

        This function can be used for checking parameters that must be of a
        certain class, or are permitted to be None to e.g. fallback to the
        defaults.
    """
    return isinstance( obj, classType ) or obj is None


def requireIsInstanceOrNone( obj, classType, msg=None ):
    """
        Throws an AssertionError if 'obj' is neither an instance of class
        'classType' (not as string, pass as real class!), nor None.

        This function can be used for checking parameters that must be of a
        certain class, or are permitted to be None to e.g. fallback to the
        defaults.
    """
    msg = msg or '{} ({}): Neither an instance of class "{}", nor None'.format( str( obj ), type( obj ), classType )

    requireMsg( isInstanceOrNone( obj, classType ), msg )


def isWritableDir( path ):
    """
        Returns a boolean whether 'path' is a writable directory.
    """
    return os.access( path, os.W_OK )


def requireIsWritableDir( path ):
    """
        Throws an AssertionError if 'path' is not a writable directory.
    """
    requireIsTextNonEmpty( path )
    requireIsDir( path )

    requireMsg( isWritableDir( path ),
                path + ": No writing permissions for this directory" )


#----------------------------------------------------------------------------
# Public functions for logging
#----------------------------------------------------------------------------


# always write messages to console

consoleFormatter = logging.Formatter( "[%(filename)s:%(lineno)d %(levelname)s] %(message)s" )
consoleHandler   = logging.StreamHandler()
consoleHandler.setFormatter( consoleFormatter )

# use same format as for writing to console
fileFormatter = consoleFormatter
fileHandler   = None

rootLogger = logging.getLogger()
rootLogger.addHandler( consoleHandler )

# default loglevel after importing py
#
# Note: If set to logging.DEBUG then all other Python modules may log a lot
#       of stuff, better keep logging.INFO here.
rootLogger.setLevel( logging.INFO )


# ensure flushing the streams at application exit
atexit.register( logging.shutdown )


def setOutputFile( filename, rotate=False, size=None, count=None ):
    """
        Adds another log handler which writes log lines to files.

        If 'filename' is None, writing to output file will be stopped.
        If 'rotate' is True, use `RotatingFileHandler` to rotate the log files
        once they reach `size` bytes (default 5 MB), a maximum of `count` times
        (default 5).

    """
    global fileHandler

    rootLogger = logging.getLogger()

    if filename is None:
        requireMsg( fileHandler, 'fileHandler not assigned, yet' )
        rootLogger.removeHandler( fileHandler )
    else:
        requireIsTextNonEmpty( filename )

        if rotate:
            from logging.handlers import RotatingFileHandler

            size  = size or (5 * 1024 * 1024) # 5 MB
            count = count or 5

            fileHandler = RotatingFileHandler( filename, maxBytes=size, backupCount=count )
        else:
            fileHandler = logging.FileHandler( filename )

        fileHandler.setFormatter( fileFormatter)
        rootLogger.addHandler( fileHandler )


def setDebugLevel( level ):
    """
        Set the verbosity level of the root logger.

        This is a convenience function, for advanced settings please do
        manually.

        You can pass either an integer (like the ToolBOS "FastScript. library)
        with ranges meaning 0==highest, 10==lowest, or pass a constant of
        the 'logging' module, such as logging.DEBUG.


        Critical messages only:
            setDebugLevel( 0 )
            setDebugLevel( logging.CRITICAL )

        Additionally regular progress info:
            setDebugLevel( 3 )
            setDebugLevel( logging.INFO )

        Verbose output for debugging:
            setDebugLevel( 5 )
            setDebugLevel( logging.DEBUG )
    """
    requireIsInt( level )

    # we assume that levels greater than 10 are ones passed by constants
    # such as logging.INFO
    #
    # levels below 10 are assumed to match the ToolBOS FastScript.library
    # which typically is between 0 and 10

    if level == 0:
        level = logging.CRITICAL
    elif level == 1:
        level = logging.WARNING
    elif level < 5:
        level = logging.INFO
    elif level < 10:
        level = logging.DEBUG
    else:
        # assume is a constant from the 'logging' module (values 10-50)
        pass

    rootLogger = logging.getLogger()
    rootLogger.setLevel( level )


def getDebugLevel():
    """
        Get the verbosity level of the root logger.

        This is a convenience function, for advanced settings please do
        manually.

        For compatibility returns values like the ToolBOS "FastScript. library
        with ranges meaning 0==highest, 10==lowest.
    """
    level = logging.getLogger().level

    if level <= 10:
        return 5
    elif level <= 20:
        return 3
    else:
        return 0


def log( level, message ):
    """
        This function makes using the 'logging' module similar to the
        ToolBOS macro "ANY_LOG".
    """
    requireIsInt( level )
    requireIsText( message )

    if level <= 0:
        logging.warning( message )
    elif level < 5:
        logging.info( message )
    else:
        logging.debug( message )


def logVerbatim( level, message ):
    """
        This function is similar to log() except that it does not print
        the typical logline preamble.

        Use it to log verbatim.
    """
    if level <= getDebugLevel():
        consoleHandler.stream.write( message + '\n' )


def addStreamLogger( stream, debugLevel, preamble=True ):
    """
        By providing a file-like object the log messages of the checkers
        can be captured. 'stream' could be a StringIO instance.

        'debugLevel' should be provided as constant from the 'logging'-
        framework, f.i. logging.INFO or logging.DEBUG
    """
    if preamble:
        formatString = "[%(filename)s:%(lineno)d %(levelname)s] %(message)s"
    else:
        formatString = "%(message)s"


    streamFormatter = logging.Formatter( formatString )
    logHandler      = logging.StreamHandler( stream )
    logHandler.setFormatter( streamFormatter )
    logHandler.setLevel( debugLevel )

    rootLogger.addHandler( logHandler )


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
    requireIsTextNonEmpty( path )
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
    requireIsTextNonEmpty( path )
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
    requireIsTextNonEmpty( path )
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
        used to exclude certain directories (such as "build" and ".git") in
        the following example:

            excludePattern = re.compile( "(build|.git)" )
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
    requireIsTextNonEmpty( src )
    requireIsTextNonEmpty( dst )
    requireIsFile( src )

    dstDir = os.path.dirname( dst )
    mkdir( dstDir )

    os.rename( src, dst )
    requireIsFile( dst )


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

    requireIsTextNonEmpty( src )
    requireIsTextNonEmpty( dst )
    requireIsInRange( maxAttempts, 1, 100 )
    requireIsInRange( waitSeconds, 1, 3600 )

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
    requireIsTextNonEmpty( symlink )
    requireIsTextNonEmpty( target )        # allow initially broken links
    requireIsBool( dryRun )

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
    requireIsText( path )

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
            requireIsDir( path )
        else:
            raise


def getFileOwner( path ):
    """
        Returns the username (if possible) of the owner of the specified
        file or directory. If the username cannot be retrieved, the
        numerical user ID will be used as fallback.
    """
    from pwd import getpwuid

    requireIsTextNonEmpty( path )

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
    requireIsTextNonEmpty( filename )
    requireIsText( content )

    dirName = os.path.dirname( filename )

    if dirName and not os.path.isdir( dirName ):
        mkdir( dirName )

    f = open( filename, "w" )
    f.write( content )
    f.close()


def findFiles( path, regexp=None, ext=None ):
    """
        Returns a list with all files in 'path' whoms names match a certain
        pattern. Pattern can be:

          * regexp:   a precompiled regular expression object
          * ext:      file has a certain extension, e.g. ".c" (mind the dot!)

        Note that both 'regexp' and 'ext' can be scalar values as well
        as lists. In such case, any of the expression (or extension) must
        match.
    """
    fileList = []

    # recursively search for files
    for root, dirs, files in os.walk( path ):

        for entry in files:
            path    = os.path.join( root, entry )
            fileExt = os.path.splitext( entry )[1]

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
    requireIsTextNonEmpty( filename )

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
    requireIsTextNonEmpty( cmd )

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
    requireIsTextNonEmpty( cmd )

    if host is not None:
        requireIsTextNonEmpty( host )

    if workingDir is not None:
        requireIsTextNonEmpty( workingDir )


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
    requireIsTextNonEmpty( varName )

    value = getEnv( varName )

    if value is None:
        if default is None:
            if not isTextNonEmpty( value ):
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
    if isText( varNameOrMap ):                # set single variable
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

            setEnv_withExpansion( 'EXAMPLE_ROOT',
                                  '${SIT}/External/Example/1.0' )

            setEnv_withExpansion( 'PATH',
                                  '${EXAMPLE_ROOT}/bin:${PATH}' )

            will first define EXAMPLE_ROOT as absolute path to Example/1.0
            (replacing ${SIT} by its current environment value)
            and in a second step prepend the absolute path to Example's
            "bin"-directory to the current value of ${PATH}.
    """
    requireIsTextNonEmpty( varName )
    requireIsTextNonEmpty( varValue )

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
    requireIsTextNonEmpty( varName )
    requireIsText( s )

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
    requireIsTextNonEmpty( varName )
    requireIsText( s )

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
        with a leading '0o' prefix!
    """
    requireIsTextNonEmpty( path )
    requireIsIntNotZero( dirPermission  )
    requireIsIntNotZero( filePermission )

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
    requireIsTextNonEmpty( path )

    dirPerms  = 0o555
    filePerms = 0o444

    chmodRecursive( path, dirPerms, filePerms )


def readWriteChmod( path ):
    """
        Set read-write permissions to the given path recursively.
    """
    requireIsTextNonEmpty( path )

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

    requireIsTextNonEmpty( path )    # do not check if exists
    requireIsTextNonEmpty( groupName )
    requireIsIntNotZero( mode )

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

    requireIsTextNonEmpty( path )
    requireIsTextNonEmpty( groupName )

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
    requireIsTextNonEmpty( string )
    requireIsTextNonEmpty( varName )
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
    requireIsText( string )                 # might be empty

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
    requireIsTextNonEmpty( string )
    requireIsTextNonEmpty( envName )
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
    """
    requireIsText( string )

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
    requireIsList( nestedList )

    resultList = list( flatten( nestedList ) )
    requireIsList( resultList )

    return resultList


def flatten( i ):
    """
        Flattens an iterable into a one-dimensional list, using generators.
    """
    for x in i:
        if isinstance( x, collections.abc.Iterable ) and not isinstance( x, ( str, bytes ) ):
            yield from flattenList( x )
        else:
            yield x


def removeDuplicates( aList ):
    """
        Removes all duplicate elements from a list.
    """
    requireIsList( aList )
    return list( dict.fromkeys( aList ) )


def reduceList( nestedList ):
    """
        Flattens a nested list into a one-dimensional list and removes
        all duplicate elements.
    """
    requireIsList( nestedList )
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
    requireIsList( nestedList )
    result = ''

    if level > 20:              # loop guard
        raise ValueError

    for i, entry in enumerate( nestedList ):
        if isText( entry ):
            entryPadding = levelPadding + '%c---' % _getTreeChar( nestedList, i )
            result += "%s%s\n" % ( entryPadding, entry )
        elif isList( entry ):
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

    requireIsInstance( startTime, datetime.datetime )

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

    requireIsTextNonEmpty( msg )

    lines = wrap( msg )
    finalMsg = '\n\t' + '\n\t'.join( lines ) + '\n'

    raise SystemExit( "\033[1m%s\033[0m\n" % finalMsg )


def tryImport( modules ):
    """
        Checks that the provided modules can be imported.
        Stops with a message to the user if some are not found.
    """
    import importlib

    if isText( modules ):
        modules = [ modules ]

    requireIsIterable( modules )

    notFound = set()

    for moduleName in modules:
        requireIsTextNonEmpty( moduleName )

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
    requireIsList( searchList )
    lastStringIndex = _getLastStringInList( searchList )

    if index < lastStringIndex:
        treeChar = '|'
    elif index == lastStringIndex:
        treeChar = '`'
    else:
        treeChar = ' '

    return treeChar


def _getLastStringInList( searchList ):
    requireIsList( searchList )
    index = 0

    for i in range( 0, len(searchList) ):
        if isinstance( searchList[i], str ):
            index = i

    return index


# EOF
