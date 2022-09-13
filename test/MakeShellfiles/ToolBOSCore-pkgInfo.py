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


name             = 'ToolBOSCore'

package          = 'ToolBOSCore'

version          = '4.1'

section          = 'DevelopmentTools'

category         = 'DevelopmentTools'

patchlevel       = 0

maintainer       = ( 'mstein', 'Marijke Stein' )

gitBranch        = 'develop'

gitCommitID      = '420a264e48c6ccb41b5ba67f0c5f4ca52df6e8b0'

gitOrigin        = 'git@dmz-gitlab.honda-ri.de:TECH_Team/ToolBOSCore.git'

gitRelPath       = ''

gitOriginForCIA  = 'git@dmz-gitlab.honda-ri.de:ToolBOS/ToolBOSCore.git'

recommends       = [ 'deb://git',
                     'sit://External/CMake/3.4',
                     'sit://External/git/2.18',
                     'sit://External/wine/3.5' ]


# EOF
