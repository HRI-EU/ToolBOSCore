# -*- coding: utf-8 -*-
#
#  run clang-tidy on project
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


import io
import time
import re

from ToolBOSCore.Util import FastScript


def stripAnsi(line):
    return re.sub(r'\x1b\[[\d;]+m', '', line)


def checkScript(buildDir):
    command = 'run-clang-tidy'

    stdout = io.StringIO()
    stderr = io.StringIO()
    failed = False
    reportedIssues = []

    cmd = f'{command} -p {buildDir}'

    FastScript.execProgram(cmd, stdout=stdout, stderr=stderr)
    reportedIssues = stdout.getvalue().splitlines(keepends=True)

    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
    logFileName = buildDir + '/clang-tidy-' + timestamp + '.log'
    with open(logFileName, 'w') as logFile:
        logFile.writelines(reportedIssues)

    warnings = [stripAnsi(i) for i in reportedIssues if 'warning' in i]
    warningFileName = buildDir + '/clang-tidy-warnings-' + timestamp + '.log'
    with open(warningFileName, 'w') as logFile:
        logFile.writelines(warnings)

    if len(warnings) > 0:
        failed = True
    else:
        failed = False

    stdout.close()
    stderr.close()

    return failed, warnings


# EOF
