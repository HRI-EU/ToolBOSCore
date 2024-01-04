#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Configures the user's shell environment to work with ToolBOS
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
import os.path
import re
import sys

# ATTENTION: Do imports from ToolBOSCore-package below after PYTHONPATH
#            got extended!


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


# auto-detect where the ToolBOSCore package is located
tcRootDir   = os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..' ) )
realRootDir = os.path.realpath( tcRootDir )

sys.path.append( os.path.join( tcRootDir, 'include' ) )
sys.path.append( os.path.join( tcRootDir, 'src'     ) )


# check if ToolBOSCore/4.3/BashSrc was sourced (so PYTHONPATH was set),
# otherwise we will not be able to import any ToolBOSCore Python package
#
sourced = False

# Attention: In this expression the part '4.3' would actually need to
#            be '4\.2' as we mean the literal dot and not any chracter!
#            It is only done so that our bumpVersion.sh script replaces it!
versionInclude = re.compile( 'ToolBOSCore/4.3.*/include' )

for directory in sys.path:
    if versionInclude.match( directory ) or \
       directory.endswith( 'ToolBOSCore/include' ):
        sourced = True

if not sourced:
    print( "\nPlease run the following command first:" )
    print( "source /hri/sit/latest/DevelopmentTools/ToolBOSCore/4.3/BashSrc\n" )
    sys.exit( -1 )


from ToolBOSCore.Settings import ToolBOSConf
from ToolBOSCore.Settings import UserSetup
from ToolBOSCore.Storage  import SIT
from ToolBOSCore.Util     import ArgsManagerV2
from ToolBOSCore.Util     import FastScript


#----------------------------------------------------------------------------
# Default settings
#----------------------------------------------------------------------------


sitRootPath  = SIT.getDefaultRootPath()
sitProxyPath = SIT.getDefaultProxyPath()
shell        = FastScript.getEnv( 'SHELL' )
version      = ToolBOSConf.packageVersion
subtitle     = '~ Welcome to ToolBOS SDK %s ~' % version


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


# Replace the username in the sitProxyPath by a generic placeholder so that
# the unittests relying on the consistent output will pass, see TBCORE-1378.

userName         = FastScript.getCurrentUserName()
sitProxyPathHelp = sitProxyPath.replace( userName, '<user>' )


desc = 'Configures your shell for using the ToolBOS SDK.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-r', '--rootDir', metavar='PATH', default=sitRootPath,
                    help='path to global SIT (default: %s)' % sitRootPath )

argman.addArgument( '-p', '--proxyDir', metavar='PATH', default=sitProxyPath,
                    help='path to proxy SIT (default: %s)' % sitProxyPathHelp )

argman.addArgument( '-a', '--advanced', action='store_true',
                    help='advanced config with SIT proxy directory' )

argman.addExample( '%(prog)s' )
argman.addExample( '%(prog)s -a' )

args         = vars( argman.run() )
sitRootPath  = args['rootDir']
sitProxyPath = args['proxyDir']
advanced     = args['advanced']


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


print( '' )
print( '########                 ###   #######     ####     #####' )
print( '   ##     #####   #####   ##   ##    ##  ##    ##  ##   ##' )
print( '   ##    ##   ## ##   ##  ##   ######## ##      ##  ##' )
print( '   ##    ##   ## ##   ##  ##   ##    ## ##      ##    ##' )
print( '   ##    ##   ## ##   ##  ##   ##    ##  ##    ##  ##   ##' )
print( '   ##     #####   #####  ##### #######     ####     #####' )
print( '' )
print( subtitle.center( 58 ) )    # 58 == logo width
print( '' )
print( '' )


FastScript.setEnv( 'SIT_VERSION', 'latest' )


dirName = os.path.expanduser( '~/.HRI' )

if os.path.exists( dirName ):
    logging.warning( '%s: directory already exists', dirName )
    answer = input( 'Overwrite (y/N)? ' )

    if answer != 'y' and answer != 'Y':
        raise SystemExit( 'Aborted.' )

try:
    UserSetup.setupShell()

    if advanced:
        UserSetup.setupProxy( sitRootPath, sitProxyPath )

except AssertionError as details:
    raise SystemExit( details )


shellfile            = 'BashSrc'
shellFilePath        = os.path.join( tcRootDir, shellfile )
shellFilePathDefault = os.path.join( SIT.getDefaultRootPath(),
                                     ToolBOSConf.canonicalPath,
                                     shellfile )


# in case we are using the default SIT, suggest to put "latest" into the
# ~/.bashrc, otherwise suggest to put the particular SIT build

if os.path.realpath( shellFilePath ) == os.path.realpath( shellFilePathDefault ):
    shellFilePath = shellFilePathDefault


bashFile = os.path.expanduser( '~/.bashrc' )
line1    = 'Please add this line to file "%s":' % bashFile
line2    = 'source %s' % shellFilePath
line3    = 'Then login again.'
length   = max( len(line1), len(line2) )


# The following is not performance-critical and would become
# too complex if written in a lazy way...
# pylint: disable=logging-not-lazy
logging.info( '' )
logging.info( '' )
logging.info( '   ' + '_' * (length+2) )
logging.info( '  |' + ' ' * (length+2) + '|' )
logging.info( '  | %s ' % line1 + ' ' * (length-len(line1)) + '|' )
logging.info( '  | %s ' % line2 + ' ' * (length-len(line2)) + '|' )
logging.info( '  |' + ' ' * (length+2) + '|' )
logging.info( '  | %s ' % line3 + ' ' * (length-len(line3)) + '|' )
logging.info( '  |' + '_' * (length+2) + '|' )
logging.info( '' )
logging.info( '' )
logging.info( 'Have a lot of fun with ToolBOS %s :-)' % version )
logging.info( '' )


# EOF
