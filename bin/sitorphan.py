#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  List packages which have no dependee (inspired by "deborphan")
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


from ToolBOSCore.Packages import BSTPackage
from ToolBOSCore.Packages import ProjectProperties
from ToolBOSCore.Storage  import SIT
from ToolBOSCore.Util     import Any
from ToolBOSCore.Util     import ArgsManagerV2


#----------------------------------------------------------------------------
# Commandline parsing
#----------------------------------------------------------------------------


blacklist = ( 'Applications', 'Modules/BBCM', 'Modules/Index',
              'Modules/RTMaps', 'Scripts', 'Temporary' )


# It could be possible to add a parameter for the desired SIT path.
# However later we are using the BSTPackage module, which operates
# on the current Proxy-/Global SIT paths only.
#
# If we would support fetching the packages from another SIT,
# e.g.  "/hri/sit/unstable", we would need to touch the BSTPackage
# module first.

desc   = 'List packages which have no dependee (inspired by "deborphan"). ' \
         'Note that some SIT categories (such as "Applications" or ' \
         '"Modules/BBCM") contain packages which typically have no ' \
         'dependee by design. They are excluded by default, pass "--all" ' \
         'to also show them.'

argman = ArgsManagerV2.ArgsManager( desc )

argman.addArgument( '-a', '--all', action='store_true',
                    help='show all SIT packages without dependee' )

argman.addExample( '%(prog)s' )

args    = vars( argman.run() )
showAll = args['all']

if not args['verbose']:
    # disable typical progress logging
    Any.setDebugLevel( 0 )


#----------------------------------------------------------------------------
# Main program
#----------------------------------------------------------------------------


sitPath = SIT.getPath()

fullPkgList = SIT.getCanonicalPaths( sitPath )
Any.requireIsListNonEmpty( fullPkgList )


if showAll:
    # "-a|--all": check all packages
    pkgList = fullPkgList
else:
    # default: filter-out packages which typically have no dependees
    filterFunc = lambda canonicalPath: not canonicalPath.startswith( blacklist )
    pkgList    = filter( filterFunc, fullPkgList )


for canonicalPath in pkgList:
    package = BSTPackage.BSTInstalledPackage( 'sit://' + canonicalPath )
    package.retrieveReverseDependencies( recursive=False )

    if not package.revDepSet:
        maintainer = ProjectProperties.getMaintainerFromFilesystem( canonicalPath )
        print( "%s (%s)" % ( canonicalPath, maintainer ) )


# EOF
