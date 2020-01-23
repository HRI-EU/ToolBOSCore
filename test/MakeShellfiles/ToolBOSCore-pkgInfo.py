# -*- coding: utf-8 -*-
#
#  Custom package settings
#
#  Copyright (C)
#  Honda Research Institute Europe GmbH
#  Carl-Legien-Str. 30
#  63073 Offenbach/Main
#  Germany
#
#  UNPUBLISHED PROPRIETARY MATERIAL.
#  ALL RIGHTS RESERVED.
#
#


section          = 'DevelopmentTools'

version          = '3.3'

name             = 'ToolBOSCore'

package          = 'ToolBOSCore'

maintainer       = ( 'mstein', 'Marcus Stein' )

gitBranch        = 'develop'

gitRelPath       = ''

recommends       = [ 'deb://git-core',
                     'deb://git-svn',
                     'deb://graphviz',
                     'sit://External/CMake/3.3',
                     'sit://External/git/2.18',
                     'sit://External/subversion/2.18',
                     'sit://External/wine/3.5' ]


# EOF
