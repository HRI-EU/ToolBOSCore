#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  lists the dependencies of a package
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


from ToolBOSCore.Packages import ListDependencies, ProjectProperties
from ToolBOSCore.Util     import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


desc = 'Lists the dependencies of a package, taken from the pkgInfo.py ' \
       'files in the Software Installation Tree (SIT). By default each ' \
       'package appears only once for better readability.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-d', '--direct', action='store_true',
                    help='direct dependencies only, exclude transitive ones' )

argman.addArgument( '-f', '--full', action='store_true',
                    help='show full tree (default: suppress duplicates)' )

argman.addArgument( '-l', '--list', action='store_true',
                    help='show as list (default: show as tree)' )

argman.addArgument( '-m', '--missing-only', action='store_true',
                    help='only list missing (implies "--list" and "--direct")' )

argman.addArgument( '-r', '--reverse', action='store_true',
                    help='find out who is depending on package' )

argman.addArgument( 'package', help='absolute or canonical package path' )

argman.addExample( '%(prog)s .' )
argman.addExample( '%(prog)s Libraries/MasterClock/1.6' )
argman.addExample( '%(prog)s ${SIT}/Libraries/MasterClock/1.6' )
argman.addExample( '%(prog)s -f /hri/sit/latest/Libraries/MasterClock/1.6' )
argman.addExample( '%(prog)s -r sit://Libraries/MasterClock/1.6' )

args          = vars( argman.run() )

asList        = args['list']
canonicalPath = ProjectProperties.toCanonicalPath( args['package'] )
direct        = args['direct']
full          = args['full']
missingOnly   = args['missing_only']
reverse       = args['reverse']

recursive     = not direct

if missingOnly:
    asList    = True
    reverse   = False


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


ListDependencies.listDependencies( canonicalPath, reverse, recursive,
                                   missingOnly, asList, full )


# EOF
