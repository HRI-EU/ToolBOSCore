# -*- coding: utf-8 -*-
#
#  Custom package settings
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


name             = 'ToolBOSCore'

version          = '3.3'

category         = 'DevelopmentTools'

recommends       = [ 'deb://git-core',
                     'deb://git-svn',
                     'deb://graphviz',
                     'sit://External/CMake/3.3',
                     'sit://External/git/2.18',
                     'sit://External/subversion/2.18',
                     'sit://External/wine/3.5' ]

delete           = [ '*py.class' ]

usePatchlevels   = True

patchlevel       = 0

install          = [ 'external',
                     'share' ]

installMatching  = [ ('', '^useFromHere.+'),
                     ('bin', '\\.bat'),
                     ('doc', '\\.(png|jpg|txt)$'),
                     ('doc/BuildSystemTools', '\\.png$'),
                     ('doc/Concepts', '\\.png$'),
                     ('doc/HowTo', '\\.png$'),
                     ('doc/Logos', '\\.(jpg|png|svg)$'),
                     ('examples', '\\.(py|c|conf)$') ]

gitOriginForCIA  = 'git@dmz-gitlab.honda-ri.de:ToolBOS/ToolBOSCore-Mirror.git'

sqLevel          = 'advanced'


# ToolBOSCore does not get compiled, hence no executable exists for the
# unittest.c examples or unittests that solely work on file level.
# By suppressing the following directories the C12 checker (Valgrind) will
# not attempt to run them. Also Klocwork (C10) shall not be invoked.
#
# HRI-EU copyright header has been replaced by typical BSD 3-clause license preamble

sqOptOutRules    = [ 'GEN04', 'C10', 'C12' ]

sqComments       = { 'GEN03': 'confirmed, to be fixed',
                     'GEN04': 'package is published under BSD License',
                     'C10'  : 'do not invoke Klocwork on example files',
                     'C12'  : 'do not invoke Valgrind on example files' }


# EOF
