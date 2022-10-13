# -*- coding: utf-8 -*-
#
#  Asserts and very comon basics functions such as logging
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
import io
import os

from atexit import register
from glob   import glob
from re     import match

try:
    _FILE_TYPES = (io.IOBase, file)
except NameError:
    _FILE_TYPES = (io.IOBase,)

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
        Returns a boolean whether or not 'obj' references 'None'.
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
        Returns a boolean whether or not 'obj' is of type 'bool'.
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
        Returns a boolean whether or not 'obj' is of type 'int'.
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
        Returns a boolean whether or not 'obj' of type 'int' and is not zero.
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
        Returns a boolean whether or not 'obj' is a number and between
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
        Returns a boolean whether or not 'obj' is of type 'float'.
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
        Returns a boolean whether or not 'obj' is of type 'str'.
    """
    return isinstance( obj, str )


# legacy leftovers from Python 2/3 migration when there was a need to
# distinguish 8-bit char strings from Unicode strings
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
        Returns a boolean whether or not 'obj' is of type 'list'.
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
        Returns a boolean whether or not 'obj' contains elements.
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
        Returns a boolean whether or not 'obj' is of type 'dict'.
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
        Returns a boolean whether or not 'dict' is a list and contains
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
        Returns a boolean whether or not 'obj' is of type 'tuple'.
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
        Returns a boolean whether or not 'obj' is iterable, e.g. is a collection,
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
        Returns a boolean whether or not 'obj' is of either type 'set' or
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
        Returns a boolean whether or not 'obj' is present in 'container'.
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
        Returns a boolean whether or not 'handle' points to an open file handle.
    """
    return isinstance( handle, _FILE_TYPES )

def isFile( path ):

    """
        Returns a boolean whether or not 'path' points to a regular file.
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
        Returns a boolean whether or not 'path' points to a regular file.

        Additionally, the size of the file must be zero.
    """
    requireIsText( path )
    return os.path.getsize( path ) == 0


def isFileNonEmpty( path ):
    """
        Returns a boolean whether or not 'path' points to a regular file.

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
        Returns a boolean whether or not 'path' points to a directory.
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
        Returns a boolean whether or not 'path' points to an empty directory.

        There must not be any files or directories beside the '.' and
        '..' hardlinks.
    """
    requireIsTextNonEmpty( path )
    return glob( path + '/*' ) == []


def requireIsEmptyDir( path ):
    """
        Throws an AssertionError if 'path' points to an empty directory.

        There must not be any files or directories beside the '.' and
        '..' hardlinks.
    """
    requireIsTextNonEmpty( path )
    requireIsDir( path )
    requireMsg( isEmptyDir( path ), path + ": Directory is empty" )


def isDirNonEmpty( path ):
    """
        Returns a boolean whether or not 'path' points to a directory.

        Additionally, the directory must contain at least one entry beside
        the '.' and '..' hardlinks.
    """
    requireIsTextNonEmpty( path )
    return glob( path + '/*' ) != []


isNonEmptyDir = isDirNonEmpty


def requireIsDirNonEmpty( path ):
    """
        Throws an AssertionError if 'path' does not point to a directory.

        Additionally, the directory must contain at least one entry beside
        the '.' and '..' hardlinks.
    """
    requireIsTextNonEmpty( path )
    requireIsDir( path )
    requireMsg( isDirNonEmpty( path ), path + ": Directory is empty" )


requireIsNonEmptyDir = requireIsDirNonEmpty


def isSymlink( path ):
    """
        Returns a boolean whether or not 'path' points to a symlink.
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
        Returns a boolean whether or not 'path' exists.
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
        Returns a boolean whether or not 'string' matches the given
        regular expression.

        Example:

          Any.requireIsMatching( 'foo', '^oo' )

        will fail because 'foo' does not start with 'oo'.
    """
    requireIsTextNonEmpty( string )
    requireIsTextNonEmpty( pattern )

    return bool( match( pattern, string ) )


def requireIsMatching( string, pattern ):
    """
        Throws an AssertionError if 'string' does not match the given
        regular expression.

        Example:

          Any.requireIsMatching( 'foo', '^oo' )

        will fail because 'foo' does not start with 'oo'.
    """
    requireIsTextNonEmpty( string )
    requireIsTextNonEmpty( pattern )

    requireMsg( isMatching( string, pattern ),
                "'%s' does not match expected regular expression '%s'" %
                ( string, pattern ) )


def isCallable( obj ):
    """
        Returns a boolean whether or not 'obj' is callable (read as function
        or method).
    """
    # PY3k Note: Python 3.0/3.1 don't have callable() but it's back in 3.2
    return callable( obj )


def requireIsCallable( obj ):
    """
        Throws an AssertionError if 'obj' is not callable (read as function
        or method).

        Example:
          func = getattr( CMakeWrapper, taskName )
          Any.requireIsCallable( func )
    """
    requireMsg( isCallable( obj ),
                '%s: Not a callable function or method (%s)' %
                ( str( obj ), type( obj ) ) )


def isInstance( obj, classType ):
    """
        Returns a boolean whether or not 'obj' is an instance of class
        'classType' (not as string, pass as real class!).
    """
    return isinstance( obj, classType )


def requireIsInstance( obj, classType, msg=None ):
    """
        Throws an AssertionError if 'obj' is not instance of class
        'classType' (not as string, pass as real class!).

        Example: function requires string argument

          def myFunction( s ):
            Any.requireIsInstance( s, str )
            [...]
    """
    requireIsNotNone( obj )

    msg = msg or '{} ({}): Not an instance of class "{}"'.format( str( obj ), type( obj ), classType )

    requireMsg( isInstance( obj, classType ), msg )


def isInstanceOrNone( obj, classType ):
    """
        Returns a boolean whether or not 'obj' is instance of class
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
        Returns a boolean whether or not 'path' is a writable directory.
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

# default loglevel after importing Any.py
#
# Note: If set to logging.DEBUG then all other Python modules may log a lot
#       of stuff, better keep logging.INFO here.
rootLogger.setLevel( logging.INFO )


# ensure flushing the streams at application exit

register( logging.shutdown )


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

        You can pass either an integer (like the ToolBOS "Any" library)
        with ranges meaning 0==highest, 10==lowest, or pass a constant of
        the 'logging' module, such as logging.DEBUG.


        Critical messages only:
            Any.setDebugLevel( 0 )
            Any.setDebugLevel( logging.CRITICAL )

        Also regular progress info:
            Any.setDebugLevel( 3 )
            Any.setDebugLevel( logging.INFO )

        Verbose output for debugging:
            Any.setDebugLevel( 5 )
            Any.setDebugLevel( logging.DEBUG )
    """
    requireIsInt( level )

    # we assume that levels greater than 10 are ones passed by constants
    # such as logging.INFO
    #
    # levels below 10 are assumed to match the ToolBOS Any library
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

        For compatibility returns values like the ToolBOS "Any" library
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


# EOF
