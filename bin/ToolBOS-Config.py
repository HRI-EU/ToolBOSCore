#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Show ToolBOS config options
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


from __future__ import print_function

import logging

from ToolBOSCore.Settings import ToolBOSConf
from ToolBOSCore.Util     import Any, ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Configure ToolBOS SDK preferences.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-p', '--print', type=str, metavar='VAR',
                    help='show value of specified config option' )

argman.addArgument( '-s', '--set', type=str, metavar='EXPR',
                    help='set config option in user conf in Python syntax ("key=value")' )

argman.addArgument( '-r', '--remove', type=str, metavar='VAR',
                    help='remove config option from user conf' )

argman.addArgument( '-z', '--zen', action='store_true',
                    help='open configuration GUI' )


argman.addExample( '%(prog)s' )
argman.addExample( '%(prog)s -p defaultPlatform' )
argman.addExample( '%(prog)s -s "defaultPlatform = \'qnx\'"' )
argman.addExample( '%(prog)s -s "foo=bar"' )
argman.addExample( '%(prog)s -r "foo"' )
argman.addExample( '%(prog)s -z                   # opens GUI' )

args     = vars( argman.run() )

printVar  = args['print']
removeVar = args['remove']
setVar    = args['set']
zen       = args['zen']


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


tconf = ToolBOSConf.ToolBOSConf()


if printVar:
    try:
        value = tconf.getConfigOption( printVar )
    except KeyError:
        value = '<not set>'

    print( value )

elif setVar:
    # Note: Setting non-string options does not work, yet because everything
    # is stored as string so far.
    #
    # Example:
    # $ ./bin/ToolBOS-Config.py -s 'foo2 = [ 1, 2, 3, 4]'
    # [ToolBOSSettings.py:196 DEBUG] setting config option: foo2=[ 1, 2, 3, 4]
    #
    # results in:
    # foo2 = '[ 1, 2, 3, 4]'
    #
    # because the function to store the option checks the datatype and in
    # case of strings put quotes around it.
    # To be reviewed (if necessary at all).

    key, value = setVar.split( '=' )
    key        = key.strip()
    value      = value.strip()

    Any.setDebugLevel( logging.DEBUG )
    tconf.setUserConfigOption( key, value )

elif removeVar:

    Any.setDebugLevel( logging.DEBUG )
    tconf.delUserConfigOption( removeVar  )

elif removeVar:

    Any.setDebugLevel( logging.DEBUG )
    tconf.delUserConfigOption( removeVar  )

elif zen:

    from ToolBOSCore.Settings import PreferencesDialog

    PreferencesDialog.run()

else:
    # read ground-truth of available config options
    config = tconf.getConfigOptions()

    # show sorted by key
    keys = list( config.keys() )
    keys.sort()

    for key in keys:
        value = config[ key ]
        print( '%30s | %s' % ( key.ljust(30), value ) )


# EOF
