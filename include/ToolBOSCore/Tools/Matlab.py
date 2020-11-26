#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Matlab source-code analysis
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

from six import StringIO
from ToolBOSCore.Settings            import ProcessEnv
from ToolBOSCore.Settings            import ToolBOSConf
from ToolBOSCore.Util                import Any
from ToolBOSCore.Util                import FastScript


#----------------------------------------------------------------------------
# Public API
#----------------------------------------------------------------------------


MESSAGES = {}


class MatlabMessage( object ):

    def __init__( self, msgid, severity, message ):
        self.id             = msgid
        self.severity       = severity
        self.message        = message
        MESSAGES[ self.id ] = self


    def __repr__( self ):
        return "[{0}, {1}, \"{2}\"]".format( self.id, self.severity,
                                             self.message )


#
# Preload a set of Matlab messages, which has been generated via matlab code
#
# allmsg = codecheck(filename, '-allmsg')
#

MatlabMessage(' INTER', 0, "========== Internal Message Fragments ==========")
MatlabMessage(' MSHHH', 7, "this is used for %#ok and should never be seen!")
MatlabMessage('  BAIL', 7, "done with run due to error")
MatlabMessage('  M2LN', 7, "L <line #> (C <line #>)")
MatlabMessage('  M3LN', 7, "L <line #> (C <line #>-<line #>)")
MatlabMessage('  M4LN', 7, "L <line #> (C <line #>) and L <line #> (C <line #>)")
MatlabMessage('  M6LN', 7, "L <line #> (C <line #>-<line #>) and L <line #> (C <line #>-<line #>)")
MatlabMessage(' IFILE', 7, "<FILE>")
MatlabMessage(' IPATH', 7, "<FILE>")
MatlabMessage(' Ifile', 7, "<file>")
MatlabMessage(' INAME', 7, "<NAME>")
MatlabMessage(' Iname', 7, "<name>")
MatlabMessage(' INUMB', 7, "<number>")
MatlabMessage(' ILINE', 7, "<line #>")
MatlabMessage(' IRESW', 7, "<reserved word>")
MatlabMessage(' IFUNC', 7, "<FUNCTION>")
MatlabMessage(' IOPER', 7, "<operator>")
MatlabMessage(' IOPTN', 7, "<option>")
MatlabMessage(' INTRN', 0, "========== Serious Internal Errors and Assertions ==========")
MatlabMessage(' NOLHS', 3, "Left side of an assignment is empty.")
MatlabMessage(' BDLEX', 4, "Code Analyzer bug: lexer returns unknown token.")
MatlabMessage(' ASSRT', 4, "This file caused problems during an earlier run of Code Analyzer.")
MatlabMessage(' FXBAD', 3, "Fix message cannot find its trigger message.")
MatlabMessage(' TMMSG', 4, "More than 50,000 Code Analyzer messages were generated, leading to some being deleted.")
MatlabMessage(' TMNOD', 4, "Code Analyzer node table exceeded due to complexity of this program.")
MatlabMessage('MXASET', 4, "Expression is too complex for code analysis to complete.")
MatlabMessage(' NOMEM', 4, "Code Analyzer has run out of memory.")
MatlabMessage(' INERR', 4, "An internal Code Analyzer consistency check has failed (Code Analyzer bug!).")
MatlabMessage(' XJOIN', 4, "Code Analyzer bug: unexpected JOIN.")
MatlabMessage(' NULLA', 4, "Code Analyzer bug: Null pointer in ASET.")
MatlabMessage(' XOTHR', 4, "Code Analyzer bug: unexpected OTHERWISE.")
MatlabMessage(' XELSE', 4, "Code Analyzer bug: unexpected ELSE.")
MatlabMessage(' XCASE', 4, "Code Analyzer bug: unexpected CASE.")
MatlabMessage(' XCTCH', 4, "Code Analyzer bug: unexpected CATCH.")
MatlabMessage(' TOPLP', 4, "Code Analyzer bug: unexpected left parenthesis.")
MatlabMessage(' TOPCL', 4, "Code Analyzer bug: call at top level.")
MatlabMessage(' XSUBF', 4, "Code Analyzer bug: unexpected subfunction.")
MatlabMessage(' XFUNC', 4, "Code Analyzer bug: badly formed function file.")
MatlabMessage(' TMPAR', 4, "Code Analyzer bug: multiple parents for node.")
MatlabMessage(' XSUBS', 4, "Code Analyzer bug: unexpected partial subscript.")
MatlabMessage(' XTABL', 4, "Code Analyzer bug: table format error.")
MatlabMessage('   XID', 4, "Code Analyzer bug: invalid ID index.")
MatlabMessage('  XIDP', 4, "Code Analyzer bug: ID points to missing entry.")
MatlabMessage(' XSTID', 4, "Code Analyzer bug: symbol table link is bad.")
MatlabMessage(' XSTPT', 4, "Code Analyzer bug: symbol table list error.")
MatlabMessage('  XNOU', 4, "Code Analyzer bug: missing use in table.")
MatlabMessage(' XQUOT', 4, "Code Analyzer bug: unexpected quote in table.")
MatlabMessage(' NOUSE', 4, "Code Analyzer bug: Cannot find source of use conflict.")
MatlabMessage(' NOLST', 4, "Code Analyzer bug: missing list entry.")
MatlabMessage(' NONUK', 4, "Code Analyzer bug: unexpected need to remove quote.")
MatlabMessage('  NODS', 4, "Code Analyzer bug: data structure corruption.")
MatlabMessage(' XVAR2', 4, "Code Analyzer bug: linking var twice.")
MatlabMessage(' XCALL', 4, "Code Analyzer bug: unexpected CALL.")
MatlabMessage(' XDCAL', 4, "Code Analyzer bug: unexpected DCALL.")
MatlabMessage(' XSB2E', 4, "Code Analyzer bug: subscript seen too early.")
MatlabMessage(' XDOPE', 4, "Code Analyzer bug: dope field seen for non-ID.")
MatlabMessage(' XDUAL', 4, "Code Analyzer bug: Dual data structure error.")
MatlabMessage('  XFOR', 4, "Code Analyzer bug: badly constructed FOR.")
MatlabMessage(' XUPLV', 4, "Code Analyzer bug: missing list in uplevel.")
MatlabMessage(' UPFCN', 4, "Code Analyzer bug: uplevel of function defn.")
MatlabMessage(' XTREE', 4, "Code Analyzer bug: bad parse tree.")
MatlabMessage(' XTRCL', 4, "Code Analyzer bug: bad tree turning to call.")
MatlabMessage(' XMISS', 4, "Code Analyzer bug: no missing entries in scripts.")
MatlabMessage('  XOUT', 4, "Code Analyzer bug: bad outer scope entry.")
MatlabMessage('UNKTAG', 4, "Code Analyzer bug: unknown message tag=<NAME>.")
MatlabMessage('TAGARG', 4, "Code Analyzer bug: wrong number of arguments for message tag=<NAME>.")
MatlabMessage('UNKARG', 4, "Code Analyzer bug: unknown argument format=<NAME>.")
MatlabMessage('TNDMSG', 4, "Code Analyzer bug: did not find My-Lint message tag.")
MatlabMessage(' LIN2L', 3, "A source file line is too long for Code Analyzer.")
MatlabMessage('  QUIT', 4, "Earlier syntax errors confused Code Analyzer (or a possible Code Analyzer bug).")
MatlabMessage('XTPATH', 1, "A message path leads to an null node.")
MatlabMessage('XTAPTH', 1, "An autofix command has an inappropriate argument.")
MatlabMessage(' FILER', 0, "========== File Errors ==========")
MatlabMessage(' NOSPC', 4, "File <FILE> is too large or complex to analyze.")
MatlabMessage('  MBIG', 4, "File <FILE> is too big for Code Analyzer to handle.")
MatlabMessage(' NOFIL', 4, "File <FILE> cannot be opened for reading.")
MatlabMessage(' NOFWR', 4, "File <FILE> cannot be opened for writing.")
MatlabMessage(' MDOTM', 4, "Filename <FILE> must end in .m or .M.")
MatlabMessage(' BDFIL', 4, "Filename <FILE> is not formed from a valid MATLAB identifier.")
MatlabMessage(' M2LNG', 4, "Filename <FILE> exceeds maximum length.")
MatlabMessage(' RDERR', 4, "Unable to read file <FILE>.")
MatlabMessage(' MCDIR', 2, "Class name <name> and @directory name do not agree: <FILE>.")
MatlabMessage(' MCFIL', 2, "Class name <name> and file name do not agree: <file>.")
MatlabMessage(' CFERR', 1, "Cannot open or read the Code Analyzer settings from file <FILE>. Using default settings instead.")
MatlabMessage(' XFERR', 1, "Cannot open or read the Code Analyzer extension file '<FILE>'.")
MatlabMessage(' XTERR', 1, "An error happened with extension file '<FILE>' at <line #>: file ignored.")
MatlabMessage(' SNERR', 0, "========== Syntax Errors ==========")
MatlabMessage(' BDOPT', 2, "Option <name> is ignored because it is invalid.")
MatlabMessage(' BADCH', 3, "Invalid character(s).")
MatlabMessage(' BADFP', 3, "Invalid floating-point constant.")
MatlabMessage(' BADOT', 3, "Use of two dots (..) is an invalid MATLAB construction.")
MatlabMessage(' BADNE', 3, "'Not Equals' is spelled ~= in MATLAB, not !=.")
MatlabMessage(' STRIN', 3, "A quoted string is unterminated.")
MatlabMessage(' INBLK', 3, "A block comment is unterminated at the end of the file.")
MatlabMessage(' RESWD', 3, "Invalid use of a reserved word.")
MatlabMessage(' REDEF', 2, "<name> might be used incompatibly or redefined.")
MatlabMessage('  TLEV', 1, "<reserved word> could be very inefficient unless it is a top-level statement in its function.")
MatlabMessage(' UNSET', 3, "Invalid use of <operator> on the left side of an assignment.")
MatlabMessage(' LHROW', 3, "The left side of an assignment cannot have multiple rows (';').")
MatlabMessage(' EOFER', 3, "Program might end prematurely (or an earlier error confused Code Analyzer).")
MatlabMessage(' MDEEP', 4, "Parentheses, brackets, and braces are nested too deeply.")
MatlabMessage(' DEEPC', 4, "Block comments are nested too deeply.")
MatlabMessage(' DEEPN', 4, "Functions are nested too deeply.")
MatlabMessage(' DEEPS', 4, "Statements are nested too deeply.")
MatlabMessage(' NOPAR', 3, "Invalid syntax at <operator>. Possibly, a ), }, or ] is missing.")
MatlabMessage(' TWOCM', 2, "A comma cannot immediately follow another comma.")
MatlabMessage(' ROWLN', 2, "All matrix rows must be the same length.")
MatlabMessage(' NOBRK', 2, "BREAK can only be used in a FOR or WHILE block, or within a script.")
MatlabMessage('  CONT', 3, "CONTINUE is only valid in a FOR or WHILE loop.")
MatlabMessage(' COLND', 2, "END or Colon can only be used to index arrays. This might be an incorrect use.")
MatlabMessage(' NOCLS', 2, "DOT in function name is only valid in methods of a class")
MatlabMessage(' GPFST', 2, "A GLOBAL or PERSISTENT declaration must precede first use.")
MatlabMessage(' NPERS', 2, "A PERSISTENT declaration is not valid in scripts.")
MatlabMessage(' DSARG', 2, "The DRANGE function must have 1, 2, or 3 arguments.")
MatlabMessage(' FNEST', 3, "FUNCTION keyword use is invalid here. This might cause later messages about END.")
MatlabMessage(' ENDCT', 3, "An END might be missing, possibly matching <reserved word>.")
MatlabMessage(' SYNER', 3, "Parse error at <reserved word>: usage might be invalid MATLAB syntax.")
MatlabMessage(' SBTMP', 3, "Cannot call or index into a temporary array.")
MatlabMessage('  CFIG', 2, "The Code Analyzer settings file, <FILE>, has an error on line <line #>.")
MatlabMessage('BADNOT', 2, "Using ~ to ignore a value is not permitted in this context.")
MatlabMessage('ENDPAR', 3, "Invalid syntax at end of file. Possibly, the indicated bracket is not matched.")
MatlabMessage('  PFOR', 0, "========== PARFOR Messages ==========")
MatlabMessage(' PFRNG', 1, "The range of a PARFOR statement must be increasing consecutive integers.")
MatlabMessage(' PFNST', 2, "PARFOR or SPMD cannot be used inside another PARFOR loop.")
MatlabMessage('  PFDF', 2, "FOR with DRANGE (old PARFOR) cannot be used inside a PARFOR loop.")
MatlabMessage('  PFBR', 2, "BREAK and RETURN statements cannot be used inside a PARFOR loop.")
MatlabMessage('  PFLD', 2, "The LOAD function can only be used to assign an output structure in a PARFOR loop.")
MatlabMessage('  PFSV', 2, "SAVE cannot be called in a PARFOR loop.")
MatlabMessage('  PFGP', 2, "The GLOBAL or PERSISTENT variable <name> should not be set inside a PARFOR loop.")
MatlabMessage('  PFGV', 1, "Using GLOBAL variable <name> in a PARFOR loop could fail because it accesses a worker machine's global area.")
MatlabMessage(' PFEVB', 1, "Using EVALIN('base') or ASSIGNIN('base') inside a PARFOR loop refers to the worker machines' base workspaces.")
MatlabMessage(' PFEVC', 2, "EVALIN('caller') and ASSIGNIN('caller') are invalid inside of a PARFOR loop.")
MatlabMessage('PFNAIO', 1, "<NAME> with zero input arguments should not be used inside a PARFOR loop.")
MatlabMessage('PFNACK', 1, "<NAME> should not be used inside a PARFOR loop.")
MatlabMessage(' PFUIX', 2, "The index variable <name> might be used after the PARFOR loop, but it is unavailable after the loop.")
MatlabMessage(' PFOUS', 1, "The output variable <name> might not be used after the PARFOR loop.")
MatlabMessage(' PFIIN', 1, "The input variable <name> should be initialized before the PARFOR loop.")
MatlabMessage(' PFUNK', 2, "The PARFOR loop cannot run due to the way variable <name> is used.")
MatlabMessage(' PFRIN', 1, "The reduction variable <name> might not be set before the PARFOR loop.")
MatlabMessage(' PFRUS', 1, "The reduction variable <name> might not be used after the PARFOR loop.")
MatlabMessage(' PFPIE', 2, "Valid indices for <name> are restricted in PARFOR loops.")
MatlabMessage(' PFBNS', 1, "Variable <name> is indexed, but not sliced, in a PARFOR loop. This might result in unnecessary communication overhead.")
MatlabMessage('PFSAME', 2, "In a PARFOR loop, variable <name> is indexed in different ways, potentially causing dependencies between iterations.")
MatlabMessage(' PFTIN', 2, "The temporary variable <name> uses a value set outside of the PARFOR loop.")
MatlabMessage(' PFBFN', 2, "The function <NAME> inside a PARFOR loop might not access the correct workspace.")
MatlabMessage(' PFIFN', 2, "The function <NAME> might make an invalid workspace access inside the PARFOR loop.")
MatlabMessage('  PFNF', 2, "The nested function <NAME> cannot be called from within a PARFOR loop.")
MatlabMessage(' PFTUS', 2, "The temporary variable <name> is used after the PARFOR loop, but its value is nondeterministic.")
MatlabMessage(' PFRNC', 2, "The variable <name> is used like a PARFOR reduction variable, but it has additional (invalid) uses.")
MatlabMessage(' PFRFH', 2, "The PARFOR reduction function <NAME> must either be a function name or a broadcast variable.")
MatlabMessage('FORFLG', 1, "Problems would result if this FOR keyword were replaced by PARFOR.")
MatlabMessage(' FORPF', 1, "This FOR loop might be a candidate for conversion to a PARFOR loop.")
MatlabMessage(' PFXST', 2, "Changing the loop index <name> is invalid inside a PARFOR loop.")
MatlabMessage('PFCODN', 2, "Because the variable <name> is or contains a distributed or codistributed variable, it is invalid inside a PARFOR loop.")
MatlabMessage('PFCODA', 2, "Because this expression appears to be or contain a distributed or codistributed variable, it is invalid inside a PARFOR loop.")
MatlabMessage('PFCMPN', 2, "Because the variable <name> is or contains a Composite, it is invalid inside a PARFOR loop.")
MatlabMessage('PFCMPA', 2, "Because this expression appears to be or contain a Composite, it is invalid inside a PARFOR loop.")
MatlabMessage(' SPMDS', 0, "========== SPMD and Distributed Array Messages ==========")
MatlabMessage(' SPDEC', 2, "The bounds on the number of workers an SPMD block can use must be a positive integer.")
MatlabMessage('SPDEC3', 2, "An SPMD block can only specify a lower and upper bound for the number of workers to use.")
MatlabMessage(' SPNST', 2, "PARFOR or SPMD cannot be used inside an SPMD block.")
MatlabMessage(' SPRET', 2, "<reserved word> statement cannot be used inside an SPMD block.")
MatlabMessage(' SPBRK', 2, "The loop containing the BREAK or CONTINUE must be completely contained in the SPMD block.")
MatlabMessage('  SPLD', 2, "In an SPMD block, the only valid use of the LOAD function is to assign to an output structure.")
MatlabMessage('  SPSV', 2, "SAVE cannot be called in an SPMD block.")
MatlabMessage('  SPGP', 2, "Setting the GLOBAL or PERSISTENT variable <name> in an SPMD block might fail because the set happens on a worker machine.")
MatlabMessage('  SPGV', 1, "Using the GLOBAL or PERSISTENT variable <name> in an SPMD block might fail because it is accessed on a worker machine.")
MatlabMessage(' SPEVB', 1, "Using EVALIN('base') or ASSIGNIN('base') inside an SPMD block refers to the worker machines' base workspaces.")
MatlabMessage(' SPEVC', 2, "EVALIN('caller') and ASSIGNIN('caller') are invalid inside of an SPMD block.")
MatlabMessage(' SPBFN', 2, "The function <NAME> inside an SPMD block might not access the desired workspace.")
MatlabMessage(' SPIFN', 2, "The function <NAME> might make an invalid workspace access inside the SPMD block.")
MatlabMessage('  SPNF', 2, "The nested function <NAME> cannot be called from within an SPMD block.")
MatlabMessage(' DCMIX', 2, "The operator <operator> appears to combine distributed and codistributed values.")
MatlabMessage('  SPCN', 1, "Container <name> should not be used inside an SPMD block because it is hiding a Composite, distributed, or codistributed variable.")
MatlabMessage(' SPCNC', 1, "This cell array should not be used inside an SPMD block because it is hiding a Composite, distributed, or codistributed variable.")
MatlabMessage(' SPICN', 2, "The variable <name> contains a hidden Composite, distributed, or codistributed variable and therefore should not be used inside an SPMD block.")
MatlabMessage(' SPCCO', 2, "Because the variable <name> contains a hidden codistributed variable, it should not be used outside an SPMD block.")
MatlabMessage('DSPMDN', 1, "The variable <name> appears to be distributed, but is created inside an SPMD block.")
MatlabMessage('DSPMDA', 1, "This expression appears to create a distributed value inside an SPMD block.")
MatlabMessage(' DCUNK', 1, "The codistributed or distributed array static function <name> is unrecognized.")
MatlabMessage('FSPMDN', 1, "The variable <name> appears to be set to a codistributed value outside of an SPMD block.")
MatlabMessage('FSPMDA', 1, "This expression appears to create a codistributed value outside of an SPMD block.")
MatlabMessage('SPWHOS', 2, "The <NAME> function cannot be called from within an SPMD block.")
MatlabMessage(' UNUSD', 0, "========== Unused or Unnecessary Constructions ==========")
MatlabMessage(' NOEFF', 1, "The operation or expression <operator> has no evident effect.")
MatlabMessage(' NUSED', 1, "Global or persistent variable <name> might be unused or unset in this function or script.")
MatlabMessage(' EQEFF', 0, "Possible inappropriate use of == operator. Use = if assignment is intended.")
MatlabMessage(' MNEFF', 0, "Possible inappropriate use of - operator. Use = if assignment is intended.")
MatlabMessage(' NOANS', 0, "Using ANS as a variable is not recommended as ANS is frequently overwritten by MATLAB.")
MatlabMessage('  PUSE', 1, "Persistent variable <name> might be unused.")
MatlabMessage(' USENS', 1, "Variable <name> is used, but might be unset.")
MatlabMessage('SUSENS', 1, "Variable <name> is used, but might be unset (within a script).")
MatlabMessage(' SETNU', 1, "Variable <name> is set, but might be unused.")
MatlabMessage(' ASGLU', 1, "The value assigned here to <name> appears to be unused. Consider replacing it by ~.")
MatlabMessage(' NASGU', 1, "The value assigned to variable <name> might be unused.")
MatlabMessage('SNASGU', 1, "The value assigned to variable <name> might be unused (within the script).")
MatlabMessage(' NODEF', 1, "The variable <name> might be used before it is defined.")
MatlabMessage(' INUSD', 1, "Input argument <name> might be unused. If this is OK, consider replacing it by ~.")
MatlabMessage(' VANUS', 1, "Input argument 'varargin' might be unused.")
MatlabMessage(' INUSL', 1, "Input argument <name> might be unused, although a later one is used. Consider replacing it by ~.")
MatlabMessage(' DEFNU', 1, "The function <name> might be unused.")
MatlabMessage(' VALST', 1, "<name> must be the last argument in the argument list.")
MatlabMessage(' ASGSL', 1, "Assignment to <name> might be unnecessary.")
MatlabMessage(' UNRCH', 1, "This statement (and possibly following ones) cannot be reached.")
MatlabMessage('  PROP', 1, "There is a property named <name>. Did you mean to reference it?")
MatlabMessage(' CPROP', 1, "Confusing function call. Did you mean to reference property <name>?")
MatlabMessage(' USAGE', 0, "========== Unexpected or Suspicious Usage ==========")
MatlabMessage(' COMNL', 1, "Comma before newline might incorrectly suggest row continuation.")
MatlabMessage(' FXSET', 1, "Loop index <name> is changed inside of a FOR loop.")
MatlabMessage('  FXUP', 1, "Outer loop index <name> is set inside a child function.")
MatlabMessage(' STRSZ', 1, "Comparing two strings that might have different sizes. Use STRCMP.")
MatlabMessage(' M3COL', 1, "Using three colons (a:b:c:d) in an expression is probably unintended.")
MatlabMessage(' BDLOG', 1, "Operator <operator> is seldom used in a logical context.")
MatlabMessage(' BDSCA', 1, "Operator <operator> is seldom used in a scalar context.")
MatlabMessage(' BDLGI', 1, "Variable <name> might be set by a nonlogical operator.")
MatlabMessage(' BDSCI', 1, "Variable <name> might be set by a nonscalar operator.")
MatlabMessage(' DUALC', 1, "Command <name> might be prematurely ended by comma.")
MatlabMessage(' RHSFN', 2, "The expression cannot be assigned to multiple values.")
MatlabMessage(' STOUT', 1, "The function return value <name> might be unset.")
MatlabMessage(' LTARG', 1, "Function <NAME> might be called with too few arguments.")
MatlabMessage(' GTARG', 1, "Function <NAME> might be called with too many arguments.")
MatlabMessage(' CTPCT', 1, "The format string might not agree with the argument count.")
MatlabMessage('  FNAN', 2, "Use ISNAN when comparing values to NaN.")
MatlabMessage(' PDEPR', 1, "Function <name>.<name> is deprecated. Use <name> instead.")
MatlabMessage(' FDEPR', 1, "Function <NAME> is deprecated. Use <name> instead.")
MatlabMessage('  FOBS', 1, "The function <NAME> is now or soon will become obsolete.")
MatlabMessage(' MGONE', 2, "The function <NAME> is no longer supported by MATLAB.")
MatlabMessage(' NOSEM', 0, "Extra semicolon is unnecessary.")
MatlabMessage(' NOCOM', 0, "Extra comma is unnecessary.")
MatlabMessage(' TRYNC', 0, "TRY statement should have a CATCH statement to check for unexpected errors.")
MatlabMessage(' NO4LP', 0, "Parentheses are not needed in a FOR statement.")
MatlabMessage(' FNDEF', 0, "Function name <name> is known to MATLAB by its file name: <file>.")
MatlabMessage('  CTCH', 1, "Best practice is for CATCH to be followed by an identifier that gets the error information.")
MatlabMessage('  LERR', 1, "LASTERR and LASTERROR are not recommended. Use an identifier on the CATCH block instead.")
MatlabMessage('  EVLC', 1, "Using EVAL and EVALC with two arguments is deprecated--use TRY/CATCH instead.")
MatlabMessage('  RAND', 1, "RAND and RANDN will not accept 'seed', 'state', or 'twister' in a future release.")
MatlabMessage('  NOV6', 1, "The 'v6' flag is deprecated in <NAME>. It will not be supported in a future release.")
MatlabMessage('  V6ON', 1, "Function USEV6PLOTAPI('on') is deprecated. It will not be supported in a future release.")
MatlabMessage('  FAFD', 2, "FARROW.FD is deprecated. Use DFILT.FARROWFD instead.")
MatlabMessage(' FALFD', 2, "FARROW.LINEARFD is deprecated. Use DFILT.FARROWLINEARFD instead.")
MatlabMessage(' PSTAT', 3, "The 'Static' attribute is invalid on properties. Use 'Constant' instead.")
MatlabMessage(' CTORO', 2, "Class constructors must be declared with at least one output argument.")
MatlabMessage('  NOIN', 1, "Method <name> is not Static, so it must have at least one input argument.")
MatlabMessage('  MANU', 1, "Argument <name> is unused. Should this method be Static?")
MatlabMessage(' SQGPN', 2, "SEQGEN.PN is obsolete. Use comm.PNSequence instead.")
MatlabMessage(' MHERM', 1, "Parenthesize the multiplication of <name> and its transpose to ensure the result is Hermitian.")
MatlabMessage(' MOCUP', 1, "The variable <name> is an uplevel variable, invalid in a function called by onCleanup.")
MatlabMessage(' MDUPC', 1, "The case value <name> is a duplicate of one on line <line #>.")
MatlabMessage(' MNANC', 2, "NaN never compares equal to any value, so this case will never be matched.")
MatlabMessage(' MULCC', 1, "This case cannot be matched due to a call to UPPER or LOWER on the SWITCH value.")
MatlabMessage(' HOUGH', 1, "HOUGH(BW,'ThetaResolution',VAL) is discouraged. Use HOUGH(BW,'Theta',-90:VAL:(90-VAL) ).")
MatlabMessage(' FPARK', 1, "<NAME> is not recommended. Use <name> instead.")
MatlabMessage(' FREMO', 1, "<NAME> will be removed in a future release. Use <name> instead.")
MatlabMessage(' FREMX', 1, "<NAME> will be removed in a future release. There is no simple replacement for this.")
MatlabMessage(' FROPT', 1, "Option <NAME> will be removed in a future release. Use <name> instead.")
MatlabMessage('FROPTX', 1, "Option <NAME> will be removed in a future release. There is no simple replacement for this.")
MatlabMessage(' RMWRN', 1, "The warning with tag <name> has been removed from MATLAB, so this statement has no effect.")
MatlabMessage(' MMRPS', 2, "MMREADER.ISPLATFORMSUPPORTED has been removed. MMREADER is now supported on all platforms.")
MatlabMessage(' VRRPS', 2, "VIDEOREADER.ISPLATFORMSUPPORTED has been removed. VIDEOREADER is now supported on all platforms.")
MatlabMessage('  DMMR', 1, "MMREADER will be removed in a future release. Use VIDEOREADER instead.")
MatlabMessage('  FSTR', 1, "<NAME> is not recommended. Use <name> instead.")
MatlabMessage('MATCH2', 1, "STRMATCH is not recommended. Use STRNCMP or VALIDATESTRING instead.")
MatlabMessage('MATCH3', 1, "STRMATCH is not recommended. Use STRCMP instead.")
MatlabMessage(' DGEO1', 2, "<NAME> has been removed. Use <name> instead.")
MatlabMessage(' DGEO2', 2, "<NAME> has been removed. Use <name> instead.")
MatlabMessage(' DGEO3', 2, "<NAME> has been removed. Use <name> instead.")
MatlabMessage(' DGEO4', 2, "<NAME> has been removed. Use <name> instead.")
MatlabMessage(' GPUAR', 1, "parallel.gpu.GPUArray will be removed in a future release. Use gpuArray instead.")
MatlabMessage('GPUARB', 1, "parallel.gpu.GPUArray.<name> will be removed in a future release. Use gpuArray.<name> instead.")
MatlabMessage('REMFF1', 1, "<NAME> will be removed in a future release. Use <name> instead.")
MatlabMessage('REMFP1', 1, "<name>.<name> will be removed in a future release. Use <name> instead.")
MatlabMessage('REMFX1', 1, "<NAME> will be removed in a future release. There is no simple replacement for this.")
MatlabMessage('REMOO1', 1, "Option <NAME> will be removed in a future release. Use <name> instead.")
MatlabMessage('REMOX1', 1, "Option <NAME> will be removed in a future release. There is no simple replacement for this.")
MatlabMessage('REMFF2', 2, "<NAME> will be removed in a future release. Use <name> instead.")
MatlabMessage('REMFX2', 2, "<NAME> will be removed in a future release. There is no simple replacement for this.")
MatlabMessage('REMOO2', 2, "Option <NAME> will be removed in a future release. Use <name> instead.")
MatlabMessage('REMOX2', 2, "Option <NAME> will be removed in a future release. There is no simple replacement for this.")
MatlabMessage('REMFF3', 2, "<NAME> has been removed. Use <name> instead.")
MatlabMessage('REMFX3', 2, "<NAME> has been removed. There is no simple replacement for this.")
MatlabMessage('REMOO3', 2, "Option <NAME> has been removed. Use <name> instead.")
MatlabMessage('REMOX3', 2, "Option <NAME> has been removed. There is no simple replacement for this.")
MatlabMessage(' CHLNC', 2, "CHOLINC has been removed. Use ICHOL instead.")
MatlabMessage('CHLNCI', 2, "CHOLINC(X,'inf') has been removed. There is no simple replacement for this.")
MatlabMessage(' BTSFT', 1, "BITSHIFT(A,K,N) will be removed in a future release . Use BITSHIFT(A,K,ASSUMEDTYPE) instead.")
MatlabMessage(' BTCMP', 1, "BITCMP(A,N) will be removed in a future release . Use BITCMP(A,ASSUMEDTYPE) instead.")
MatlabMessage('NORALG', 1, "RANDNALG will be removed in a future release. Use NORMALTRANSFORM instead.")
MatlabMessage(' SETRS', 2, "SETDEFAULTSTREAM has been removed. Use SETGLOBALSTREAM instead.")
MatlabMessage(' GETRS', 2, "GETDEFAULTSTREAM has been removed. Use GETGLOBALSTREAM instead.")
MatlabMessage(' UNONC', 1, "Assign the onCleanup output argument to a variable. Do not use the tilde operator (~) in place of a variable.")
MatlabMessage('CRTJOB', 1, "<NAME> using zero inputs will be removed in a future release. Use a cluster object as the first input instead.")
MatlabMessage(' CHAIN', 1, "Use (<name> <name> <name>) && (<name> <name> <name>) instead of (<name> <name> <name> <name> <name>) to test if <name> is between <name> and <name>.")
MatlabMessage('  MCOS', 0, "========== MATLAB Classes ==========")
MatlabMessage('  ATTF', 1, "The attribute value <name> is unexpected. Use 'true' or 'false' instead.")
MatlabMessage(' ATPPP', 1, "The attribute value <name> is unexpected. Use 'public', 'private', 'protected', or a cell array of meta-classes instead.")
MatlabMessage(' ATPPI', 1, "The attribute value <name> is unexpected. Use 'public', 'private', 'protected', 'immutable', or a cell array of meta-classes instead.")
MatlabMessage('  ATCA', 1, "The attribute value <name> is unexpected. Use a cell array of meta-class objects instead.")
MatlabMessage(' ATNPP', 3, "Set attribute <name> to 'public', 'private', 'protected', or a cell array of meta-classes instead.")
MatlabMessage(' ATNPI', 3, "Set attribute <name> to 'public', 'private', 'protected', 'immutable', or a cell array of meta-classes instead.")
MatlabMessage(' ATNCA', 1, "Set attribute <name> to a cell array of meta-class objects.")
MatlabMessage('  ATAS', 1, "The attribute value <name> is unexpected. Use a single meta-class object or a cell array of meta-class objects.")
MatlabMessage(' ATNAS', 1, "Set attribute <name> to a single meta-class object or a cell array of meta-class objects.")
MatlabMessage(' ATUNK', 2, "Unknown attribute name <name>.")
MatlabMessage(' ATVIZ', 3, "Attribute 'Visible' is spelled '~Hidden' in MATLAB, and is the default.")
MatlabMessage(' ATTOF', 1, "Setting the class attribute Abstract to false is not recommended.")
MatlabMessage('  ATTO', 1, "The attribute value <name> is unexpected. Use 'true' or 'false' instead.")
MatlabMessage(' CLTWO', 3, "Only one class definition is allowed per file, and it must come at the head of the file.")
MatlabMessage(' NOPRV', 3, "A class definition cannot be inside a private directory.")
MatlabMessage(' MCHV1', 2, "Conflict between handle and value class usage (lines <line #> and <line #>).")
MatlabMessage(' MCHV2', 1, "Probable conflict between handle and value class usage (lines <line #> and <line #>).")
MatlabMessage(' MCHV3', 1, "Possible conflict between handle and value class usage (lines <line #> and <line #>).")
MatlabMessage('  MCVC', 1, "The class <NAME> has no superclasses, so must be value class (line <line #>).")
MatlabMessage('  MCHC', 1, "The class <name> is derived from a handle class, so must be a handle class (line <line #>).")
MatlabMessage('  MCEB', 1, "The class has an <reserved word> block, so must be a handle class (line <line #>).")
MatlabMessage(' MCDEL', 1, "The class has a <NAME> method, so is likely to be a handle class (line <line #>).")
MatlabMessage('  MCHM', 1, "A property is set in object <NAME>, but the modified object is not used or returned, implying that this class is a handle class (line <line #>).")
MatlabMessage('  MCVM', 1, "Method <NAME> sets a property and returns the modified object, implying that the class is a value class (line <line #>).")
MatlabMessage(' MCSGP', 2, "The method <NAME> does not refer to a valid property name.")
MatlabMessage(' MCSGA', 2, "Set/Get method <NAME> must be defined in a METHODS block with no attributes.")
MatlabMessage(' MCS2I', 2, "Set Methods must have exactly two inputs.")
MatlabMessage(' MCS1O', 2, "Set Methods must have at most one output.")
MatlabMessage(' MCG1I', 2, "Get methods must have exactly one input.")
MatlabMessage(' MCG1O', 2, "Get methods must have exactly one output.")
MatlabMessage('  MCPO', 1, "The property <NAME> is observable, which implies the class is a handle class (line <line #>).")
MatlabMessage(' MCGSA', 2, "Method <NAME> tries to set or get an abstract property.")
MatlabMessage(' MCSCN', 2, "Method <NAME> tries to set a constant property.")
MatlabMessage(' MCANI', 2, "Abstract property <name> cannot be initialized.")
MatlabMessage(' MCASC', 2, "Abstract property <name> cannot be used in a Sealed class.")
MatlabMessage(' MCCPI', 1, "The Constant property <name> needs to be initialized.")
MatlabMessage('  MCSH', 1, "Method <NAME> has a signature consistent with a handle class (line <line #>).")
MatlabMessage('  MCSV', 1, "Method <NAME> has a signature consistent with a value class (line <line #>).")
MatlabMessage(' MCCBD', 2, "The constructor <NAME> must be fully defined in the class definition file.")
MatlabMessage(' MCPSG', 2, "The set/get function <NAME> must be fully defined in the class definition file.")
MatlabMessage(' MCSCT', 2, "A call to a superclass constructor must appear at the top level (not conditional) in a constructor.")
MatlabMessage(' MCSCO', 2, "A superclass constructor must be called using the first constructor output argument.")
MatlabMessage(' MCSCF', 2, "A superclass constructor must be assigned to the first constructor output argument.")
MatlabMessage(' MCCBS', 2, "A superclass constructor is being called, but <NAME> is not a declared superclass name.")
MatlabMessage(' MCCBU', 2, "This superclass constructor is called after a use of the constructed object.")
MatlabMessage(' MCCMC', 2, "The constructor for superclass <NAME> can only be called once.")
MatlabMessage(' MCSCM', 2, "In this call of a superclass method, <NAME> must match the name of the method in which it is used.")
MatlabMessage(' MCNPN', 1, "<name> is referenced but is not a property, method, or event name defined in this class.")
MatlabMessage(' MCNPR', 1, "<name> is not a property, but is the target of an assignment.")
MatlabMessage(' MCCPE', 1, "Attempting to call a property or event <NAME> as a function.")
MatlabMessage(' MCSUP', 1, "A set method for a non-Dependent property should not access another property (<name>).")
MatlabMessage(' MCCSP', 2, "'<name>.<name>' creates a struct named <name> with a field named <name>, matching the names of the class and constant property.")
MatlabMessage(' MTMAT', 2, "The attribute <name> cannot be set more than once.")
MatlabMessage('MTMATG', 2, "The GetAccess attribute cannot be set more than once.")
MatlabMessage('MTMATS', 2, "The SetAccess attribute cannot be set more than once.")
MatlabMessage('MTMTSG', 2, "The GetAccess and SetAccess attributes cannot be set more than once.")
MatlabMessage(' MCSAC', 1, "SetAccess cannot be set on Constant properties.")
MatlabMessage(' MCSNO', 1, "Set method's first argument <name> is not returned, implying a handle class.")
MatlabMessage(' MCAPP', 2, "The private property <name> cannot be Abstract.")
MatlabMessage(' MCMSP', 2, "The private method <name> cannot be Abstract.")
MatlabMessage('MHERIT', 3, "Deriving from the built-in MATLAB <name> class is not supported.")
MatlabMessage(' MCSWA', 2, "A sealed class cannot specify allowed subclasses.")
MatlabMessage(' ERWRN', 0, "========== Errors, Warnings, etc. ==========")
MatlabMessage(' SPERR', 1, "ERROR takes SPRINTF-like arguments directly.")
MatlabMessage(' SPWRN', 1, "WARNING takes SPRINTF-like arguments directly.")
MatlabMessage(' NCHKI', 1, "<NAME> will be removed in a future release. Use NARGINCHK instead.")
MatlabMessage(' NCHKO', 1, "<NAME> will be removed in a future release. Use NARGOUTCHK instead.")
MatlabMessage(' NCHKN', 1, "NARGCHK will be removed in a future release. Use NARGINCHK without ERROR instead.")
MatlabMessage(' NCHKM', 1, "NARGCHK will be removed in a future release. Use NARGOUTCHK without ERROR instead.")
MatlabMessage('NCHKOS', 2, "NARGINCHK does not return any values.")
MatlabMessage('NCHKNO', 1, "NARGOUTCHK using more than two inputs will be removed in a future release. There is no simple replacement for this.")
MatlabMessage(' NCHKE', 1, "Use NARGOUTCHK without ERROR.")
MatlabMessage(' WLAST', 1, "WARNING('') does not reset the warning state. Use LASTWARN('') instead.")
MatlabMessage('  WNON', 1, "WARNING('ON',msgID) is faster than WARNING('ON').")
MatlabMessage(' WNOFF', 1, "WARNING('OFF',msgID) is faster than WARNING('OFF').")
MatlabMessage(' WNTAG', 1, "The first argument of WARNING should be a message identifier. Using a message identifier allows users better control over the message.")
MatlabMessage(' ERTAG', 1, "The first argument of ERROR should be a message identifier.")
MatlabMessage(' ERTXT', 2, "Specify an error message with the message identifier.")
MatlabMessage('  WTXT', 2, "Specify a warning message with the message identifier.")
MatlabMessage('  DSPS', 1, "DISP(SPRINTF(...)) can usually be replaced by FPRINTF(...).")
MatlabMessage(' STRNG', 0, "========== Strings ==========")
MatlabMessage(' STCMP', 1, "Use STRCMP instead of == or ~= to compare strings.")
MatlabMessage(' RGXP1', 1, "Using REGEXP(string, pattern, 'ONCE') is faster in this case.")
MatlabMessage(' TRIM1', 1, "Use STRTRIM(str) instead of nesting FLIPLR and DEBLANK calls.")
MatlabMessage(' STTOK', 1, "Use one call to TEXTSCAN instead of calling STRTOK in a loop.")
MatlabMessage(' TRIM2', 1, "Use STRTRIM(str) instead of DEBLANK(STRJUST(str,'left')).")
MatlabMessage('  STCI', 1, "Use STRCMPI(str1,str2) instead of using UPPER/LOWER in a call to STRCMP.")
MatlabMessage(' STNCI', 1, "Use STRNCMPI(str1,str2) instead of using UPPER/LOWER in a call to STRNCMP.")
MatlabMessage(' STLOW', 1, "There is no need for UPPER/LOWER in this string comparison.")
MatlabMessage(' STCUL', 1, "The string comparison will likely fail due to upper/lower case mismatch.")
MatlabMessage(' STCCS', 1, "It appears that STRCMPI/STRNCMPI can be replaced by a faster, case sensitive compare.")
MatlabMessage(' STISA', 1, "Consider using ISA instead of comparing the class to a string.")
MatlabMessage(' PFCEL', 1, "The function <NAME> is apparently called with a cell array (argument <line #>).")
MatlabMessage(' STRNU', 1, "Variable <name>, apparently a structure, is changed but the value seems to be unused.")
MatlabMessage(' ITERS', 1, "The Code Analyzer type analysis may be incorrect here.")
MatlabMessage('FLUDLR', 1, "It appears that flipud(fliplr(x)) or fliplr(flipud(x)) can be replaced by a faster rot90(x,2).")
MatlabMessage(' RPMT0', 1, "Consider replacing repmat(0,x,y) with zeros(x,y) for better performance.")
MatlabMessage(' RPMT1', 1, "Consider replacing repmat(1,x,y) with ones(x,y) for better performance.")
MatlabMessage(' RPMTN', 1, "Consider replacing repmat(NaN,x,y) with NaN(x,y) for better performance.")
MatlabMessage(' RPMTF', 1, "Consider replacing repmat(false,x,y) with false(x,y) for better performance.")
MatlabMessage(' RPMTT', 1, "Consider replacing repmat(true,x,y) with true(x,y) for better performance.")
MatlabMessage(' RPMTI', 1, "Consider replacing repmat(Inf,x,y) with Inf(x,y) for better performance.")
MatlabMessage(' SPEED', 0, "========== Potential Performance Problems ==========")
MatlabMessage(' PSIZE', 1, "NUMEL(x) is usually faster than PROD(SIZE(x)).")
MatlabMessage(' FNDSB', 1, "To improve performance, use logical indexing instead of FIND.")
MatlabMessage('  SFLD', 1, "Use dynamic fieldnames with structures instead of SETFIELD.")
MatlabMessage('  GFLD', 1, "Use dynamic fieldnames with structures instead of GETFIELD.")
MatlabMessage('  VCAT', 1, "Constructing a cell array is faster than using STRVCAT.")
MatlabMessage('  CCAT', 1, "{ A{:} B } can often be replaced by [ A {B}], which can be much faster.")
MatlabMessage(' AGROW', 1, "The variable <name> appears to change size on every loop iteration. Consider preallocating for speed.")
MatlabMessage('SAGROW', 1, "The variable <name> appears to change size on every loop iteration (within a script). Consider preallocating for speed.")
MatlabMessage('  ISMT', 1, "Using ISEMPTY is usually faster than comparing LENGTH to 0.")
MatlabMessage('  LOGL', 1, "Use TRUE or FALSE instead of LOGICAL(1) or LOGICAL(0).")
MatlabMessage(' ST2NM', 1, "STR2DOUBLE is faster than STR2NUM; however, STR2DOUBLE operates only on scalars. Use the function that best suits your needs.")
MatlabMessage(' FLPST', 1, "For better performance in some cases, use SORT with the 'descend' option.")
MatlabMessage(' MXFND', 1, "Use FIND with the 'first' or 'last' option.")
MatlabMessage(' EFIND', 1, "To improve performance, replace ISEMPTY(FIND(X)) with ISEMPTY(FIND( X, 1 )).")
MatlabMessage(' EXIST', 1, "EXIST with two input arguments is generally faster and clearer than with one input argument.")
MatlabMessage('  UDIM', 1, "Instead of using transpose ('), consider using a different DIMENSION input argument to <NAME>.")
MatlabMessage(' ISCHR', 1, "Use ISCHAR instead of comparing the class to 'char'.")
MatlabMessage(' ISSTR', 1, "Use ISSTRUCT instead of comparing the class to 'struct'.")
MatlabMessage(' ISLOG', 1, "Use ISLOGICAL instead of comparing the class to 'logical'.")
MatlabMessage(' ISCEL', 1, "Use ISCELL instead of comparing the class to 'cell'.")
MatlabMessage(' MIPC1', 1, "On Windows platforms, calling COMPUTER with an argument returns 'win32' or 'win64', but never 'PCWIN'.")
MatlabMessage(' STFLD', 1, "SETFIELD output must be assigned back to the structure.")
MatlabMessage(' RMFLD', 1, "RMFIELD output must be assigned back to the structure.")
MatlabMessage(' FREAD', 1, "FREAD(FID,...,'*char') is more efficient than CHAR(FREAD(...)).")
MatlabMessage(' N2UNI', 1, "FREAD no longer requires NATIVE2UNICODE in R2006A and later releases.")
MatlabMessage(' TNMLP', 1, "Consider moving the toolbox function <NAME> out of the loop for better performance.")
MatlabMessage('  IJCL', 1, "Replace complex i and j by 1i for speed and improved robustness.")
MatlabMessage('  MINV', 1, "INV(A)*b can be slower and less accurate than A\b. Consider using A\b for INV(A)*b or b/A for b*INV(A).")
MatlabMessage(' LAXES', 1, "Calling AXES(h) in a loop can be slow. Consider moving the call to AXES outside the loop.")
MatlabMessage('  MMTC', 1, "This use of MAT2CELL should probably be replaced by a simpler, faster call to NUM2CELL.")
MatlabMessage(' MRPBW', 1, "To use less memory, replace BWLABEL(bw) by LOGICAL(bw) in a call of REGIONPROPS.")
MatlabMessage(' SPRIX', 1, "This sparse indexing expression is likely to be slow.")
MatlabMessage(' SPEIG', 1, "The EIG function is called in an invalid manner with a sparse argument.")
MatlabMessage(' TRSRT', 1, "Transposing the input to <NAME> is often unnecessary.")
MatlabMessage(' CCAT1', 1, "{ A{I} } can usually be replaced by A(I) or A(I)', which can be much faster.")
MatlabMessage(' GRIDD', 1, "Consider replacing GRIDDATA with TRISCATTEREDINTERP for better performance.")
MatlabMessage(' ISMAT', 1, "When checking if a variable is a matrix consider using ISMATRIX.")
MatlabMessage(' ISROW', 1, "When checking if a variable is a row vector consider using ISROW.")
MatlabMessage(' ISCOL', 1, "When checking if a variable is a column vector consider using ISCOLUMN.")
MatlabMessage('   EML', 0, "========== MATLAB for Code Generation Messages ==========")
MatlabMessage('  EMAO', 2, "Code generation does not support & and | in conditionals. Use && and ||.")
MatlabMessage('  EMCA', 2, "Code generation only supports cell operations for varargin and varargout.")
MatlabMessage('  EMTC', 2, "Code generation does not support TRY/CATCH constructions.")
MatlabMessage(' EMSCR', 2, "Code generation does not support scripts.")
MatlabMessage(' EMNST', 2, "Code generation does not support nested functions.")
MatlabMessage('  EMFH', 2, "Code generation does not support anonymous functions.")
MatlabMessage(' EMVDF', 2, "Code generation requires variable <name> to be fully defined before subscripting it.")
MatlabMessage(' EMGRO', 2, "Code generation does not support variable <name> size growth through indexing.")
MatlabMessage(' EMNSI', 2, "Code generation requires IF and WHILE conditions to be scalar.")
MatlabMessage(' EMTAG', 1, "The compilation directive (or pragma) EML is not recommended. Use CODEGEN instead.")
MatlabMessage(' EMXTR', 1, "The EML package is not recommended. Use CODER instead.")
MatlabMessage('   MCC', 0, "========== MATLAB Compiler (Deployment) Messages ==========")
MatlabMessage('  MCAP', 2, "MCC does not permit the ADDPATH function.")
MatlabMessage('  MCCD', 1, "MCC use of the CD function is problematic.")
MatlabMessage(' MCPRD', 2, "MCC allows only one argument in the PRINTDLG function.")
MatlabMessage(' MCPRT', 1, "MCC prefers Windows applications to call DEPLOYPRINT instead of PRINT, but use PRINT when printing to a file.")
MatlabMessage(' MCHLP', 2, "MCC does not permit the HELP function.")
MatlabMessage(' MCKBD', 2, "MCC does not permit the KEYBOARD function.")
MatlabMessage(' MCSVP', 2, "MCC does not permit the SAVEPATH function.")
MatlabMessage(' MCMLR', 1, "MCC use of the MATLABROOT function is problematic.")
MatlabMessage('  MCDP', 1, "MCC use of the DEPLOYPRINT function is problematic.")
MatlabMessage(' MCABF', 1, "MCC use of absolute file names is likely to fail.")
MatlabMessage(' MCMFL', 1, "MCC allows writing .m files, but they cannot be executed by the deployed application.")
MatlabMessage(' MCTBX', 1, "MCC use of toolbox folder file names is likely to fail.")
MatlabMessage(' MCUOA', 2, "MCC requires the program to assign a value to output argument <name>.")
MatlabMessage('  MCLL', 1, "MCC does not allow C++ files to be read directly using LOADLIBRARY.")
MatlabMessage(' MCWBF', 1, "MCC requires that the first argument of WEBFIGURE not come from FIGURE(n).")
MatlabMessage(' MCWFL', 1, "MCC requires that the first argument of WEBFIGURE not come from FIGURE(n) (line <line #>).")
MatlabMessage('  NITS', 0, "========== Aesthetics and Readability ==========")
MatlabMessage(' SEPEX', 0, "For better readability, use newline, semicolon, or comma before this statement.")
MatlabMessage(' NBRAK', 0, "Use of brackets [] is unnecessary. Use parentheses to group, if needed.")
MatlabMessage(' ALIGN', 0, "<reserved word> might not be aligned with its matching END (line <line #>).")
MatlabMessage('  AND2', 0, "Use && instead of & as the AND operator in (scalar) conditional statements.")
MatlabMessage('   OR2', 0, "Use || instead of | as the OR operator in (scalar) conditional statements.")
MatlabMessage(' NOPTS', 0, "Terminate statement with semicolon to suppress output (within a script).")
MatlabMessage(' NOPRT', 0, "Terminate statement with semicolon to suppress output (in functions).")
MatlabMessage(' VUNUS', 0, "<operator> produces a value that might be unused.")
MatlabMessage(' LNGNM', 0, "The name <name> has been truncated to 63 characters.")
MatlabMessage(' MFAMB', 0, "Code Analyzer cannot determine whether <name> is a variable or a function, and assumes it is a function.")
MatlabMessage('  MSNU', 0, "A Code Analyzer message was once suppressed here, but the message is no longer generated.")
MatlabMessage('  DNNW', 0, "DATENUM(NOW) can be replaced by NOW.")
MatlabMessage('  LIC3', 2, "In test files, use 'qeLicense' instead of LICENSE.")
MatlabMessage('  APWT', 2, "In test files, use 'qePoll' instead of APWAIT.")
MatlabMessage('PRTCAL', 1, "This call of <NAME> will produce output that will be printed.")
MatlabMessage('NCOMMA', 1, "Best practice is to separate output variables with commas.")
MatlabMessage(' MYLNT', 0, "========== Autofix and My-Lint Messages ==========")
MatlabMessage(' MYBUG', 4, "A problem has been detected with My-Lint patterns, messages, or autofixes. Please report to the MathWorks.")
MatlabMessage(' MYBAD', 2, "A My-Lint pattern was applied to a node <operator> that does not support it.")
MatlabMessage(' MYVER', 2, "A My-Lint extension file is ignored because its version is too new.")
MatlabMessage(' MYFIL', 2, "A My-Lint extension file is missing, unreadable, or corrupt.")
MatlabMessage('MSGPTH', 2, "A message was generated using a null node, and was ignored.")
MatlabMessage('FIXPTH', 2, "An autofix operation was attempted on an inappropriate node, <name>, and was ignored.")
MatlabMessage('FIXNUL', 2, "An autofix operation was attempted on a null node, and was ignored.")
MatlabMessage('MYNYET', 1, "This My-Lint operation is plausible, but not yet implemented.")
MatlabMessage(' MINFO', 0, "========== Information and Metrics ==========")
MatlabMessage(' NSTMT', 5, "The function <name> has <line #> statements.")
MatlabMessage(' NSSMT', 5, "This script has <line #> statements.")
MatlabMessage('  CABE', 5, "The McCabe complexity of <name> is <line #>.")
MatlabMessage(' SCABE', 5, "The McCabe complexity is <line #>.")


def checkMessage( msgid, minSeverity = 1 ):
    """
       Check if the given 'id' Matlab message should be report against the
       'minSeverity' level

       Return True of False if the given id message should be reported against
       the 'minSeverity' level
    """
    retVal = False
    if is_valid( msgid ):
        retVal = True if MESSAGES[ msgid ].severity >= minSeverity else False
    else:
        logging.warning( "Matlab MessageId '%i' not present in MESSAGES", msgid )

    return retVal


def is_valid( msgid ):
    """
        Return True if the matlab message id is valid, False otherwise
    """
    return msgid in MESSAGES


def get( msgid ):
    """
        Return the MatlabMessage object associated to the give Matlab id
        message if present
        None otherwise
    """
    return MESSAGES[ msgid ] if is_valid( msgid ) else None


def codeCheck( filename, minseverity = 1, filtermsg = None ):
    """
        Execute Matlab code checked against the specified filename which must
        be given as an absolute pathname. Returns a list of tuples in the
        form:  (lineNumber, msgId, description)

        Optional severity specified the minimum severity level to report.

        Some matlab msgId might be filtered specifying a list or tuple of
        msgid strings.
    """
    Any.requireIsFileNonEmpty( filename )

    ProcessEnv.source( ToolBOSConf.getConfigOption( 'package_matlab' ) )

    cmd = "matlab -nodisplay -nosplash -nodesktop -r " + \
          "\"checkcode('{0}', '-id', '-fullpath'); quit;\"".format( filename )

    stdout = StringIO()
    stderr = StringIO() if Any.getDebugLevel() <= 3 else None

    try:
        FastScript.execProgram( cmd, stdout=stdout, stderr=stderr )

        # TODO: stderr contains a lot of D-Bus errors, check if contain sth. useful

    except OSError:
        raise RuntimeError( "Matlab is not in PATH, please source it first." )


    if filtermsg is None:
        filtermsg = []

    result = []
    regexp = re.compile( r'^L\s(\d+)\s\(.+?\):\s([A-Z]+):\s(.+)$' )

    for line in stdout.getvalue().split( '\n' ):
        tmp = regexp.match( line )

        if tmp:
            lineNumber = tmp.group(1)
            msgId      = tmp.group(2).rjust(6)      # e.g. " INTER"
            msg        = tmp.group(3)

            if is_valid( msgId ) and msgId not in filtermsg:
                if checkMessage( msgId, minseverity ):
                    result.append( ( lineNumber, msg ) )

    return result


# EOF
