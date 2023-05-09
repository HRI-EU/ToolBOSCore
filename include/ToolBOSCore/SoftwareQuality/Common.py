# -*- coding: utf-8 -*-
#
#  Common constants for Software Quality Guideline
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


from ToolBOSCore.Settings import ToolBOSConf
from ToolBOSCore.Util     import FastScript


OK                = 'OK'
FAILED            = 'failed'
DISABLED          = 'disabled'
NOT_APPLICABLE    = 'not applicable'
NOT_EXECUTED      = 'not executed'
NOT_IMPLEMENTED   = 'not implemented'
NOT_REQUIRED      = 'not required'

# do not use (frozen)set for sqLevelNames, to preserve a kind of "order"
# even though the levels are independent and not based upon each other
sqLevelNames      = [ 'cleanLab', 'basic', 'advanced', 'safety' ]

sqLevels          = { 'cleanLab': 'clean-lab standard (essentials only)',
                      'basic'   : 'basic set (HRI-EU standard)',
                      'advanced': 'advanced set',
                      'safety'  : 'safety-critical applications' }

sqLevelDefault    = 'basic'

sectionKeys       = [ 'GEN', 'C', 'PY', 'MAT', 'DOC', 'SAFE', 'SPEC', 'BASH' ]

sectionNames      = { 'GEN' : 'General',
                      'C'   : 'C and C++',
                      'PY'  : 'Python',
                      'MAT' : 'Matlab',
                      'DOC' : 'Documentation',
                      'SAFE': 'Safety-critical applications',
                      'SPEC': 'Specific requirements',
                      'BASH': 'Bash-Scripts' }

sectionObjectives = { 'GEN' : 'Maintainability, compatibility',
                      'C'   : 'Maintainability, compatibility',
                      'PY'  : 'Maintainability, compatibility',
                      'MAT' : 'Maintainability',
                      'DOC' : 'User experience',
                      'SAFE': 'Safety',
                      'SPEC': 'Safety, portability',
                      'BASH': 'Maintainability, safety' }

tempPylintConf    = ToolBOSConf.getConfigOption( 'pylintConf' )
pylintConf        = FastScript.expandVars( tempPylintConf )


# EOF
