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

gitBranch        = 'develop-4.1'

gitCommitID      = '2b0d260ea459a4495a404577eed6a44a09e9113a'

gitOrigin        = 'git@dmz-gitlab.honda-ri.de:TECH_Team/ToolBOSCore.git'

gitRelPath       = ''

gitOriginForCIA  = 'git@dmz-gitlab.honda-ri.de:ToolBOS/ToolBOSCore.git'

recommends       = [ 'deb://git',
                     'sit://External/CMake/3.4',
                     'sit://External/git/2.18',
                     'sit://External/wine/3.5' ]


# EOF
