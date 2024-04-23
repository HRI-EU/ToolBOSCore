# -*- coding: utf-8 -*-
#
#  example package settings for running quality checker on your package
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