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

version          = '4.0'

section          = 'DevelopmentTools'

category         = 'DevelopmentTools'

patchlevel       = 0

maintainer       = ( 'mstein', 'Marijke Stein' )

gitBranch        = 'TBCORE-2231-GitLabCI'

gitCommitID      = '020950dfc0913a1a18b80335f25dd7b1335b0d48'

gitOrigin        = 'https://github.com/HRI-EU/ToolBOSCore.git'

gitRelPath       = ''

gitOriginForCIA  = 'git@dmz-gitlab.honda-ri.de:ToolBOS/ToolBOSCore.git'

recommends       = [ 'deb://git',
                     'sit://External/CMake/3.4',
                     'sit://External/git/2.18',
                     'sit://External/wine/3.5' ]


# EOF
