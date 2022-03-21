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


name             = 'Middleware'

version          = '4.1'

category         = 'Applications/ToolBOS'

BST_useClang     = True

delete           = [ 'examples/IntegrationTestLoop/runIntegrationTestLoop',
                     'examples/MostSimple/runSimple',
                     'examples/PythonicReferences/runPythonicReferences' ]

usePatchlevels   = True

envVars          = [ ( 'PATH', '${INSTALL_ROOT}/bin:${INSTALL_ROOT}/bin/${MAKEFILE_PLATFORM}:${PATH}' ),
                     ( 'PYTHONPATH', '${INSTALL_ROOT}/include:${PYTHONPATH}' ),
                     ( 'TOOLBOSMIDDLEWARE_ROOT', '${INSTALL_ROOT}' ) ]

install          = [ 'doc/CMBOS',
                     'doc/Logos',
                     'examples',
                     'external',
                     'share' ]

installMatching  = [ ( 'include', '\\.(sh|py)$', 'include' ),
                     ( 'src/ElkLayouter/libs', '\\.jar', 'lib' ),
                     ( 'src/RTBOS', '\\.h$', 'include') ]

sqLevel          = 'advanced'

sqOptOutRules    = [ 'C10' ]

sqComments       = { 'GEN01': 'few UTF8-characters (e.g. arrows) used in documentation',
                     'GEN03': 'confirmed, to be fixed',
                     'GEN04': '3rd-party-files should somehow be excluded from SQ check, e.g. by leaving it under "External" and opt-out/blacklist such directory',
                     'C10':   'just disabled because takes too long in daily runs, could be enabled' }


# EOF
