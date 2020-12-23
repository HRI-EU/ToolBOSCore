#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Build System Tools - Windows symbol extractor
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


#----------------------------------------------------------------------------
# Includes
#----------------------------------------------------------------------------


import logging
import re
import sys

from ToolBOSCore.Util import Any
from ToolBOSCore.Util import ArgsManagerV2
from ToolBOSCore.Util import FastScript


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Extract the symbols of a Windows library and write them ' \
       'to stdout (or to file using "-o <filename>").'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-b', '--bits', default=32, type=int,
                    help='Win32 or Win64 symbols' )

argman.addArgument( '-i', '--input',
                    help='read raw dumpbin.exe output from file' )

argman.addArgument( '-o', '--output',
                    help='write symbols to file' )

argman.addArgument( '-s', '--symbol', default='',
                    help='force to add the given symbol' )

argman.addExample( '%(prog)s -i dumpbin.out -o symbols.def' )
argman.addExample( 'dumpbin.exe /SYMBOLS Foo.lib | %(prog)s -o Foo.def' )

args       = vars( argman.run() )
bits       = args['bits']
inputFile  = args['input']
outputFile = args['output']
verbose    = args['verbose']


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


exportSym = False
isData    = False
section   = ''
symbols   = {}


# Load all the user's predifined symbols
for sym in args['symbol'].split(':'):
    if len( sym ):
        symbols[ sym ] = isData

#
# Loop over the dumbin.exe lines we expect to find a sequence like
#
# 002 00000000 SECT1  notype       Static       | .drectve
# 004 00000000 SECT2  notype       Static       | .debug$S
# 006 00000000 SECT3  notype       Static       | .rdata
# 008 00000000 SECT3  notype       External     | ??_C@_0EB@NFPJKBDG@ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef@ (`string')
# 009 00000000 SECT4  notype       Static       | .rdata
# 00B 00000000 SECT4  notype       External     | ??_C@_06PNMEMOHD@?$CGapos?$DL?$AA@ (`string')
# 00C 00000000 SECT5  notype       Static       | .rdata
# 00E 00000000 SECT5  notype       External     | ??_C@_06DDLNFFBN@?$CGquot?$DL?$AA@ (`string')
#

# We are interested to know allocation directive: Static or External and the right part after pipe (|):
#
# For Static allocation the right part complete the allocation directive starting with dot (.). Therefore
# we are interested only to look at certain dot directive like .text*, .data* or .rdata* because it will
# decide where the next the symbols will be allocated.
#
# For External allocation, the right part specify function names, that can be mangled or not. We are interested
# in the first part just before the optional function argument list. If the function name starts with an underscore
# (_) and we are handling symbols for 32bit windows arch than we have to remove it because such architecture
# requires so. By the way this isn't required for the 64bit arch
#
# Regarding the UNDEF pattern in the section, basically it handle symbols defined as public: static class, so
# we need to take also them, but not the one starting with _imp_ (import from other dlls) or _Cxx (C++ exceptions)
#
# Finally some clue about the microsoft C++ mangling symbols starting with a certain pattern:
#
#  ?_7 - vftable
#  ?_8 - vbtable
#  ?_9 - vcall
#  ?_A - typeof
#  ?_B - local static guard
#  ?_C - string
#  ?_D - vbase destructor
#  ?_E - vector deleting destructor
#  ?_F - default constructor closure
#  ?_G - scalar deleting destructor
#  ?_H - vector constructor iterator
#  ?_I - vector destructor iterator
#  ?_J - vector vbase constructor iterator
#  ?_K - virtual displacement map
#  ?_L - eh vector constructor iterator
#  ?_M - eh vector destructor iterator
#  ?_N - eh vector vbase constructor iterator
#  ?_O - copy constructor closure
#  ?_P<name> - udt returning <name>
#  ?_Q - <unknown>
#  ?_R0 - RTTI Type Descriptor
#  ?_R1 - RTTI Base Class Descriptor at (a,b,c,d)
#  ?_R2 - RTTI Base Class Array
#  ?_R3 - RTTI Class Hierarchy Descriptor
#  ?_R4 - RTTI Complete Object Locator
#  ?_S - local vftable
#  ?_T - local vftable constructor closure
#  ?_U - new[]
#  ?_V - delete[]

reg     = "[0-9a-fA-F]+ (?P<length>([0-9a-fA-F]+)) (?P<table>(SECT[0-9A-F]+|UNDEF)).*notype.*(?P<alloc>(Static|External)) .*\| (?P<token>[\?\.\@\$_A-Za-z0-9]+)"

# This will filter the function name, we are interested only the part containing the symbol without @<number>
reg1    = "(?P<token>.*)@[0-9]+$"
filt    = re.compile( reg )
tokfilt = re.compile( reg1 )
Any.requireMsg( filt, "Invalid regex pattern \"%s\"" % reg )


if inputFile:
    Any.requireIsFileNonEmpty( inputFile )
    logging.debug( 'reading from %s', inputFile )
else:
    logging.debug( 'reading from stdin' )
    inputFile = sys.stdin

sectionNamePrefixes = ('.text$x', '.text$mn' , '.debug$S', '.debug$T')

with open( inputFile, 'r' ) as fd:
    for line in fd:
        res = filt.match( line )

        if res is None:
            continue

        # Get the allocation match
        alloc = res.group( 'alloc' )

        # Get the section length converting the string from hex to int
        length = int(res.group( 'length' ), 16 )

        # and then token part
        sym = res.group( 'token' )

        undefSym = True if res.group( 'table' ) == 'UNDEF' else False

        Any.requireMsg( alloc is not None, 'Unexpected output of dumpbin.exe' )
        Any.requireMsg( sym   is not None, 'Unexpected output of dumpbin.exe' )


        if verbose:
            print( 'dumpbin output: %s' % line.strip() )
            # print( 'alloc/sym:      %s %s' % ( alloc, sym ) )

        # check for allocation directive
        if 'Static' in alloc:
            # We are interested only in section allocation
            if sym.startswith( '.' ):
                section = sym

                if sym == '.text' or sym.startswith( '.data' ) or \
                   sym.startswith( '.bss' ) or sym in sectionNamePrefixes:

                    exportSym = True
                else:
                    exportSym = False

                if sym.startswith( '.data' ) or sym.startswith( '.bss' ):
                    isData = True
                else:
                    isData = False

                continue


        # This will detect global variables
        if 'Extern' in alloc and length > 0:
            exportSym = True


        # Look at Extern definition
        if 'Extern' in alloc and exportSym:
            # Check whether or not we have both public vectors and scalars
            # Both scalar and vector destructor couldn't be exported
            # floating point symbols must not be exported

            if ( undefSym and section == '.text' ) or \
               ( undefSym and section in sectionNamePrefixes and not sym.startswith( '?' ) ) or \
                sym.startswith( '??_G' ) or \
                sym.startswith( '??_E' ) or \
                sym.startswith( '??_M' ) or \
                sym.startswith( '?__type_info' ) or \
                sym.startswith( '_imp_' ) or \
                sym.startswith( '__imp_' ) or \
                sym.startswith( '_Cxx' ) or \
                sym.startswith( '__Cxx' ) or \
                '@@UAEPAXI@Z'   in sym or \
                '@@QAEPAXI@Z'   in sym or \
                '@AEPAXI@Z'     in sym or \
                '_fltused'      in sym or \
                'AEPAXI@Z'      in sym or \
                'DllMain'       in sym or \
                'exception@std' in sym or \
                'real@'         in sym:

                continue

            # Checks if the symbol terminate with @<number>
            res = tokfilt.match( sym )

            # and in case remove the @<number> but only if it isn't a mangled symbol
            if res is not None:
                newsym = res.group( 'token' )

                if not newsym.startswith( "?"):
                    sym = newsym


            # Win32 has the first _ (underscore) to remove
            if bits == 32 and sym.startswith( '_' ):
                sym = sym[1:]

            if sym in symbols:
                continue

            symbols[ sym ] = isData

            if verbose:
                # print( 'dumpbin output: %s' % line.strip() )
                print( "found symbol:   %s\n" % sym )

fd.close()

output = "EXPORTS\n"

for sym in symbols:
    output += "\t%s\n" % sym


if outputFile:
    logging.debug( 'writing %s', outputFile )
    FastScript.setFileContent( outputFile, output )
else:
    print( output )


# EOF
