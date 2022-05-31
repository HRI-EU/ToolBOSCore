# -*- coding: utf-8 -*-
#
#  example package settings for running quality checker on your package
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



"""
   This is an example pkgInfo.py file. Here you can find different
   configurations which can be set in order to configure your checker.
   These settings are only specific to quality checker
"""

# name of the package
name          = 'ExamplePackage'

# version number of the package
version       = '1.0'

# category of the package (eg. Development tools, Application or External etc.)
category      = 'Applications'

# targeted SQ level: 'clean-lab', 'basic', 'advanced', 'safety-critical'
sqLevel       = 'basic'

# list of SQ rules to be explicitly enabled
sqOptInRules  = [ 'SAFE04', 'C16' ]

# list of SQ rules to be explicitly disabled
# please leave comment on why this rule is disabled by specifying 'sqComments'
# key shown in this example file
sqOptOutRules = [ 'GEN06', 'C10' ]

# list of directories (relative paths) to be explicitly included in the check
sqOptInDirs   = [ 'src', 'foo' ]

# list of directories (relative paths) to be explicitly excluded from the check
sqOptOutDirs  = [ 'external', '3rdParty' ]

# list of files (relative paths) to be explicitly included in the check
sqOptInFiles  = [ 'external/example.py' ]

# list of files (relative paths) to be explicitly excluded from the check
sqOptOutFiles = [ 'src/helper.cpp', 'include/io.py' ]

# comments + annotations to SQ rules, e.g. why opt-in/out or justification
# why a rule cannot be fulfilled
sqComments    = { 'GEN03': 'confirmed, to be fixed',
                  'C10'  : 'do not invoke Klocwork on example files' }

# paths to the executables, including arguments (if any),
# that shall be analyzed by the valgrind check routine
sqCheckExe    = [ 'bin/focal64/parseTester',
                  'bin/focal64/parseTester exampledata/FastLobby' ]

# specify this key if your project has different copyright header/license
# information than HRI-EU license
copyright     = [ 'Copyright (c) Honda Research Institute Europe GmbH',
                  'Redistribution and use in source and binary forms,',
                  'with or without modification, are permitted provided that',
                  'the following conditions are met:',
                  [...]
                ]

# specify path to the `pyproject.toml` file to configure pylint check
pylintConf    = 'config/pylint/conf'