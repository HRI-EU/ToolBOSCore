<%text>#
#  CMake build settings
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


#----------------------------------------------------------------------------
# Standard header + common routines
#----------------------------------------------------------------------------


cmake_minimum_required(VERSION 2.8.8)

find_package(BuildSystemTools)

</%text>\
set(BST_INSTALL_CATEGORY ${category})
<%text>

#----------------------------------------------------------------------------
# Dependencies
#----------------------------------------------------------------------------


# please include here the packages this one depends on
# (one bst_find_package() per dependency), e.g:
# bst_find_package(DevelopmentTools/ToolBOSCore/3.0)

</%text>\
% for dep in dependencies:
bst_find_package(${dep})
% endfor
<%text>

#----------------------------------------------------------------------------
# Build specification
#----------------------------------------------------------------------------


</%text>\
${buildRules}
<%text>

# EOF</%text>
