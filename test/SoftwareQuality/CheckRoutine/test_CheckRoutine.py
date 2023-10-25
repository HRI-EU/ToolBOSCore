#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Unittests for Rules.py module
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


import os
import pytest
import sys

from ToolBOSCore.Packages                 import PackageCreator
from ToolBOSCore.Packages.PackageDetector import PackageDetector
from ToolBOSCore.SoftwareQuality          import Common, Rules
from ToolBOSCore.Util                     import FastScript


_refDir = 'test/SoftwareQuality/CheckRoutine/ReferenceData'


@pytest.fixture
def toolBOSCoreDetector():
    """
        create an instance of packageDetector for ToolBOSCore package,
        this will be passed to individual tests if required
    """
    toolBOSCoreRoot = FastScript.getEnv( 'TOOLBOSCORE_ROOT' )

    # always switch to ToolBOSCore root before running tests
    FastScript.changeDirectory( toolBOSCoreRoot )

    details = PackageDetector( toolBOSCoreRoot )
    details.retrieveMakefileInfo()

    return details


@pytest.fixture
def testPackageForC():
    """
        create an instance of packageDetector for test package for C,
        this package instance will be used for testing of C/C++ specific rules
    """

    toolBOSCoreRoot = FastScript.getEnv( 'TOOLBOSCORE_ROOT' )

    testPackageRoot = os.path.join( toolBOSCoreRoot, 'test/SoftwareQuality/'
                        'CheckRoutine/ReferenceData/TestPackageForC' )

    # always switch to test package root before running tests
    FastScript.changeDirectory( testPackageRoot )

    details = PackageDetector( testPackageRoot )
    details.retrieveMakefileInfo()

    return details


def test_runGen01_filename_in_english( toolBOSCoreDetector ):
    """
        test rule GEN01 that filenames must be English, by providing files
        with ascii filenames
    """
    rule    = Rules.Rule_GEN01()
    details = toolBOSCoreDetector
    files   = { 'all': [ 'include/ToolBOSCore/Util/Any.py',
                         'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                         'include/ToolBOSCore/Util/FastScript.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runGen01_filename_in_other_languages( toolBOSCoreDetector ):
    """
        test rule GEN01 that filenames must be English, by providing files
        with non-ascii filenames
    """
    rule    = Rules.Rule_GEN01()
    details = toolBOSCoreDetector
    files   = { 'all': [ 'include/ToolBOSCore/Util/Any.py',
                         'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                         'include/ToolBOSCore/Util/FastScript.py',
                         f'{_refDir}/TestFileGen01äÄß.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runGen02_file_with_utf8_encoding( toolBOSCoreDetector ):
    """
        test rule GEN02 that Source code should be in ASCII or UTF-8 files,
        by providing files with valid encoding formats
    """
    rule    = Rules.Rule_GEN02()
    details = toolBOSCoreDetector
    files   = { 'all': [ 'include/ToolBOSCore/Util/Any.py',
                         'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                         'include/ToolBOSCore/Util/FastScript.py',
                         f'{_refDir}/TestFileGen01äÄß.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runGen02_file_with_wrong_encoding( toolBOSCoreDetector ):
    """
        test rule GEN02 that Source code should be in ASCII or UTF-8 files,
        by providing files with wrong encoding formats
    """
    rule    = Rules.Rule_GEN02()
    details = toolBOSCoreDetector
    files   = { 'all': [ f'{_refDir}/TestFileGen02-ISO-8859-1.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runGen03_files_with_width_limit_of_80( toolBOSCoreDetector ):
    """
        test rule GEN03 that max. line length of each source file is ideally < 80,
        by providing files with max. line width < 80
    """
    rule    = Rules.Rule_GEN03()
    details = toolBOSCoreDetector
    files   = { 'all': [ 'include/ToolBOSCore/Util/Any.py',
                              'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                              'include/ToolBOSCore/Util/FastScript.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runGen03_files_exceeding_width_limit_of_80( toolBOSCoreDetector ):
    """
        test rule GEN03 that max. line length of each source file is ideally < 80,
        by providing files with max. line width > 80
    """
    rule    = Rules.Rule_GEN03()
    details = toolBOSCoreDetector
    files   = { 'all': [ 'include/ToolBOSCore/Util/Any.py',
                         'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                         'include/ToolBOSCore/Util/FastScript.py',
                         'include/ToolBOSCore/Platforms/CrossCompilation.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runGen06_files_without_tabs( toolBOSCoreDetector ):
    """
        test rule GEN06 that there are no tabs in the code by providing files
        without any tabs
    """
    rule    = Rules.Rule_GEN06()
    details = toolBOSCoreDetector
    files   = { 'all': [ 'include/ToolBOSCore/Util/Any.py',
                         'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                         'include/ToolBOSCore/Util/FastScript.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runGen07_package_with_unittest( toolBOSCoreDetector ):
    """
        test rule GEN07 for existence of unittests by providing package
        with unittest
    """
    rule    = Rules.Rule_GEN07()
    details = toolBOSCoreDetector
    files   = {}

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runGen07_package_without_unittest(  tmp_path ):
    """
        test rule GEN07 for existence of unittests by providing package
        without unittest
    """
    rule  = Rules.Rule_GEN07()
    files = {}

    # using 'tmp_path' fixture to create a temporary directory unique to this test invocation
    FastScript.changeDirectory( tmp_path )

    # create a new python package
    creator = PackageCreator.PackageCreator_Python( 'MyPackage', '1.0', flatStyle=True )
    creator.run()

    MyPackageRoot = os.path.join( tmp_path, 'MyPackage' )
    FastScript.changeDirectory( MyPackageRoot )

    # to test this we need a package without unittest.sh. thus, removing unittest.sh
    FastScript.remove( 'unittest.sh' )

    # create an instance of this packageDetector instance for this package
    details = PackageDetector( MyPackageRoot )
    details.retrieveMakefileInfo()

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runGen10_package_managed_via_vcs( toolBOSCoreDetector ):
    """
        test rule GEN10 for VCS usage by providing a package which is
        managed by Git or SVN
    """
    rule    = Rules.Rule_GEN10()
    files   = {}
    details = toolBOSCoreDetector
    details.retrieveVCSInfo()

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runGen10_package_not_managed_via_vcs( tmp_path ):
    """
        test rule GEN10 for VCS usage by providing a package which is
        not managed by Git or SVN
    """
    rule  = Rules.Rule_GEN10()
    files = {}

    # using 'tmp_path' fixture to create a temporary directory unique to this test invocation,
    FastScript.changeDirectory( tmp_path )

    # create a new python package, which is not managed under any VCS
    creator = PackageCreator.PackageCreator_Python( 'MyPackage', '1.0', flatStyle=True )
    creator.run()

    MyPackageRoot = os.path.join( tmp_path, 'MyPackage' )
    details       = PackageDetector( MyPackageRoot )
    details.retrieveMakefileInfo()
    details.retrieveVCSInfo()

    result = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runPy02_files_without_private_members_access( toolBOSCoreDetector ):
    """
        test rule PY02 for private member access by providing files
        without access to private members
    """
    rule    = Rules.Rule_PY02()
    details = toolBOSCoreDetector

    files   = { 'python': [ 'include/ToolBOSCore/Util/Any.py',
                            'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                            'include/ToolBOSCore/Util/FastScript.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runPy02_files_with_private_members_access( toolBOSCoreDetector ):
    """
        test rule PY02 for private member access by providing files
        with access to private members
    """
    rule    = Rules.Rule_PY02()
    details = toolBOSCoreDetector
    files   = { 'python': [ 'include/ToolBOSCore/Util/Any.py',
                            'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                            'include/ToolBOSCore/Util/FastScript.py',
                            'include/ToolBOSCore/Packages/BSTPackage.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runPy04_files_without_exit_call( toolBOSCoreDetector ):
    """
        test rule PY04 for usage of exit() calls by providing files
        without any exit() calls
    """
    rule    = Rules.Rule_PY04()
    details = toolBOSCoreDetector

    files   = { 'python': [ 'include/ToolBOSCore/Util/Any.py',
                            'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                            'include/ToolBOSCore/Util/FastScript.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runPy04_files_with_exit_call( toolBOSCoreDetector ):
    """
        test rule PY04 for usage of exit() calls by providing files with exit() calls
    """
    rule    = Rules.Rule_PY04()
    details = toolBOSCoreDetector
    files   = { 'python': [ 'include/ToolBOSCore/Util/Any.py',
                            'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                            'include/ToolBOSCore/Util/FastScript.py',
                            'bin/UpdateProxyDir.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runPy05_files_without_lint_issues( toolBOSCoreDetector ):
    """
        test rule PY05 for files without any pylint issues
    """
    rule    = Rules.Rule_PY05()
    details = toolBOSCoreDetector
    files   = { 'python': [ 'test/SoftwareQuality/CheckRoutine/ReferenceData/TestPy05_Calculator.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runPy05_files_with_lint_issues( toolBOSCoreDetector ):
    """
        test rule PY05 for files with pylint issues
    """
    rule    = Rules.Rule_PY05()
    details = toolBOSCoreDetector
    files   = { 'python': [ 'include/ToolBOSCore/Util/Any.py',
                            'include/ToolBOSCore/BuildSystem/InstallProcedure.py',
                            'include/ToolBOSCore/Util/FastScript.py' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runDoc01_package_with_documentation( toolBOSCoreDetector ):
    """
        test rule DOC01 for presence of documentation within the package by
        providing a package with some documentation
    """
    rule    = Rules.Rule_DOC01()
    details = toolBOSCoreDetector
    files   = {}

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runDoc01_package_without_documentation( tmp_path ):
    """
        test rule DOC01 for presence of documentation within the package by
        providing a package without any documentation
    """
    rule  = Rules.Rule_DOC01()
    files = {}

    # using 'tmp_path' fixture to create a temporary directory unique to this test invocation
    # without any documentation
    FastScript.changeDirectory( tmp_path )

    # create a new python package
    creator = PackageCreator.PackageCreator_Python( 'MyPackage', '1.0', flatStyle=True )
    creator.run()

    MyPackageRoot = os.path.join( tmp_path, 'MyPackage' )
    details     = PackageDetector( MyPackageRoot )
    details.retrieveMakefileInfo()

    result = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runDoc01_package_with_empty_README( tmp_path ):
    """
        test rule DOC01 for presence of documentation within the package by
        providing a package with empty README.md file
    """
    from pathlib import Path

    rule  = Rules.Rule_DOC01()
    files = {}

    # using 'tmp_path' fixture to create a temporary directory unique to this test invocation
    # without any documentation
    FastScript.changeDirectory( tmp_path )

    # create a new python package
    creator = PackageCreator.PackageCreator_Python( 'MyPackage', '1.0', flatStyle=True )
    creator.run()

    MyPackageRoot = os.path.join( tmp_path, 'MyPackage' )
    FastScript.changeDirectory( MyPackageRoot )

    # add an empty README.md file
    Path('README.md').touch()

    details = PackageDetector( MyPackageRoot )
    details.retrieveMakefileInfo()

    result = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runDoc03_package_with_examples( toolBOSCoreDetector ):
    """
        test rule DOC03 for presence of examples within the package by providing
        a package with an examples directory
    """
    rule    = Rules.Rule_DOC03()
    details = toolBOSCoreDetector
    files   = {}

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runDoc03_package_without_examples( tmp_path ):
    """
        test rule DOC03 for presence of examples within the package by providing
        a package without any examples directory
    """
    rule  = Rules.Rule_DOC03()
    files = {}

    # using 'tmp_path' fixture to create a temporary directory unique to this test invocation
    # without any documentation
    FastScript.changeDirectory( tmp_path )

    # create a new python package
    creator = PackageCreator.PackageCreator_Python( 'MyPackage', '1.0', flatStyle=True )
    creator.run()

    MyPackageRoot = os.path.join( tmp_path, 'MyPackage' )
    details       = PackageDetector( MyPackageRoot )

    result = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runC01_package_with_exit_calls( testPackageForC ):
    """
        test rule C01 for usage of exit() calls within the package by providing
        files with exit() calls
    """
    rule    = Rules.Rule_C01()
    details = testPackageForC
    files   = { 'cpp'      : [],
                'c'        : [ 'src/AnyExit.c' ],
                'cppHeaders': [] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runC01_package_without_exit_calls( testPackageForC ):
    """
        test rule C01 for usage of exit() calls within the package by providing
        files without any exit() calls
    """
    rule    = Rules.Rule_C01()
    details = testPackageForC
    files   = { 'cpp'        : [],
                'c'          : [ 'src/TestPackageForC.c' ] ,
                'cppHeaders' : [ 'src/TestPackageForC.h' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runC05_with_multi_inclusion_safeguards( testPackageForC ):
    """
        test rule C05 that C/C++ header files contain inclusion guards by providing
        header files with inclusion guards
    """
    rule    = Rules.Rule_C05()
    details = testPackageForC
    files   = { 'cppHeaders' : [ 'src/TestPackageForC.h' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runC05_missing_multi_inclusion_safeguards( testPackageForC ):
    """
        test rule C05 that C/C++ header files contain inclusion guards by providing
        header files without inclusion guards
    """
    rule    = Rules.Rule_C05()
    details = testPackageForC
    files   = { 'cppHeaders' : [ 'src/ArrayList.h', 'src/BaseTypes.h' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runC09_BST_compliant_package( testPackageForC ):
    """
        test rule C09 that package can be built using BST.py by providing
        a BST-compliant package
    """
    rule    = Rules.Rule_C09()
    details = testPackageForC
    files   = {}

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runC09_non_BST_compliant_package( tmp_path ):
    """
        test rule C09 that package can be built using BST.py by providing
        a non BST-compliant package
    """
    rule  = Rules.Rule_C09()
    files = {}

    # using 'tmp_path' fixture to create a temporary directory
    # unique to this test invocation
    FastScript.changeDirectory( tmp_path )

    # create a new C library
    creator = PackageCreator.PackageCreator_C_Library( 'MyPackage', '1.0', flatStyle=True )
    creator.run()

    MyPackageRoot = os.path.join( tmp_path, 'MyPackage' )

    FastScript.changeDirectory( MyPackageRoot )
    FastScript.remove( 'pkgInfo.py' )    # to get non BST-compliant package

    details = PackageDetector( MyPackageRoot )
    details.retrieveMakefileInfo()

    result = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runC10_package_with_Klocwork_issues( testPackageForC ):
    """
        test rule C10 that executes the Klocwork source code analyzer in CLI mode,
        by providing a package with code issues
    """
    rule    = Rules.Rule_C10()
    details = testPackageForC
    files   = {}

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runBASH01_script_without_quotes( toolBOSCoreDetector ):
    """
        test rule BASH01 with scripts that have variables without quotes
    """
    rule    = Rules.Rule_BASH01()
    details = toolBOSCoreDetector

    files   = { 'bash' : [ f'{_refDir}/withoutQuotes.bash' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runBASH01_script_with_quotes( toolBOSCoreDetector ):
    """
        test rule BASH01 with scripts that have no unquoted variables
    """
    rule    = Rules.Rule_BASH01()
    details = toolBOSCoreDetector

    files   = { 'bash' : [ f'{_refDir}/withQuotes.bash' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runBASH03_script_with_backticks( toolBOSCoreDetector ):
    """
        test rule BASH03 with scripts that use backticks for
        command-substitution
    """
    rule    = Rules.Rule_BASH03()
    details = toolBOSCoreDetector

    files   = { 'bash' : [ f'{_refDir}/withBackticks.bash' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runBASH03_script_without_backticks( toolBOSCoreDetector ):
    """
        test rule BASH03 with scripts that do not use backticks for
        command-substitution
    """
    rule    = Rules.Rule_BASH03()
    details = toolBOSCoreDetector

    files   = { 'bash' : [ f'{_refDir}/withoutBackticks.bash' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runBASH04_script_args_in_string( toolBOSCoreDetector ):
    """
        test rule BASH04 with scripts that pass args in a string
    """
    rule    = Rules.Rule_BASH04()
    details = toolBOSCoreDetector

    files   = { 'bash' : [ f'{_refDir}/argsInString.bash' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runBASH04_script_args_in_array( toolBOSCoreDetector ):
    """
        test rule BASH04 with scripts that pass args in an array
    """
    rule    = Rules.Rule_BASH04()
    details = toolBOSCoreDetector

    files   = { 'bash' : [ f'{_refDir}/argsInArray.bash' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runBASH06_script_without_braces( toolBOSCoreDetector ):
    """
        test rule BASH06 with scripts that have references to
        variables without braces'
    """
    rule    = Rules.Rule_BASH06()
    details = toolBOSCoreDetector

    files   = { 'bash' : [ f'{_refDir}/withoutBraces.bash' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runBASH06_script_with_braces( toolBOSCoreDetector ):
    """
        test rule BASH06 with scripts that only have references to
        variables with braces'
    """
    rule    = Rules.Rule_BASH06()
    details = toolBOSCoreDetector

    files   = { 'bash' : [ f'{_refDir}/withBraces.bash' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


def test_runBASH07_script_without_set( toolBOSCoreDetector ):
    """
        test rule BASH07 for 'set -euo pipefail' by providing files
        without 'set -euo pipefail'
    """
    rule    = Rules.Rule_BASH07()
    details = toolBOSCoreDetector

    files   = { 'bash' : [ f'{_refDir}/setTestWithout.bash',
                           f'{_refDir}/setTest1Fail.bash',
                           f'{_refDir}/setTest2Fail.bash',
                           f'{_refDir}/setTest3Fail.bash',
                           f'{_refDir}/setTest4Fail.bash' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.FAILED


def test_runBASH07_script_with_set_or_ignored( toolBOSCoreDetector ):
    """
        test rule BASH07 for 'set -euo pipefail' by providing files
        with 'set -euxo pipefail' or files that are ignored
    """
    rule    = Rules.Rule_BASH07()
    details = toolBOSCoreDetector

    files   = { 'bash' : [ f'{_refDir}/setTest1.bash',
                           f'{_refDir}/setTest2.bash',
                           f'{_refDir}/setTest3.bash',
                           f'{_refDir}/setTest4.bash' ] }

    result  = rule.run( details, files )

    assert result[0] == Common.OK


if __name__ == "__main__":
    # The SQ checks operate on the rootdir. of the package.
    # We therefore have to navigate there.
    cwd = os.getcwd()
    FastScript.changeDirectory( '../../..' )

    sys.exit( pytest.main( [ '-vv', cwd ] ) )


# EOF
