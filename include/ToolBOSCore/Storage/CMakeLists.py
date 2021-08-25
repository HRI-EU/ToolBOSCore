# -*- coding: utf-8 -*-
#
#  Query information from CMakeLists.txt files
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


import re
import os
import logging

from ToolBOSCore.Packages import ProjectProperties
from ToolBOSCore.Util import Any


def getCategory( fileContent ):
    """
        Extracts the value of the variable BST_INSTALL_CATEGORY
        from the file content provided as input string, e.g.:

        content  = getFileContent( 'CMakeLists.txt' ):
        packageCategory = getProjectCategoryFromCMakeLists( content )

        Returns 'None' if assignment was not found.
    """
    Any.requireIsTextNonEmpty( fileContent )

    pattern = r'BST_INSTALL_CATEGORY\s*?(\S+)\)'

    try:
        return re.search( pattern, fileContent ).group(1).strip()
    except ( AssertionError, AttributeError ):
        return None


def getDependencies( fileContent ):
    """
        Extracts the list of direct dependencies/inclusions from the
        provided string (= CMakeLists.txt file content).
    """
    Any.requireIsTextNonEmpty( fileContent )

    depList = []
    regexp  = re.compile( r"^\s*bst_find_package\s*\((.*)\)\s*$" )

    for line in fileContent.splitlines():
        tmp = regexp.search( line )

        if tmp:
            # remove trailing slashes if present, e.g.:
            # bst_find_package(Libraries/Data/C-common/RoadPoints/1.0/)
            # because it violates the regexp for canonical paths
            data = tmp.group(1)
            data = data[:-1] if data[-1] == '/' else data

            depList.append( 'sit://' + data )

    return depList


def ensureHasDependency( content, package ):
    """
        Ensures if the direct dependencies/inclusions are present
        or not in the provided string (= CMakeLists.txt file content).
    """
    Any.requireIsTextNonEmpty( content )
    ProjectProperties.requireIsCanonicalPath( package )

    logging.debug( 'Validating CMakeLists.txt' )

    category, name, version = ProjectProperties.splitPath( package )
    pkgNoVersion            = os.path.join( category, name )
    found                   = False

    for dep in getDependencies( content ):
        if dep.find( pkgNoVersion ) > 0:
            found = True
            logging.debug( '%s dependency already present', pkgNoVersion )

    if found:
        return content

    else:
        logging.debug( 'inserting dependency to: %s', package )

        return insertDependency( content, package )


def insertDependency( content, package ):
    """
        Inserts the direct dependencies/inclusions if not found
        in the provided string (= CMakeLists.txt file content).
    """
    Any.requireIsTextNonEmpty( content )
    ProjectProperties.requireIsCanonicalPath( package )

    # insert after last occurrence of bst_find_package

    modified = content.splitlines()
    index    = 0

    for line in modified:
        if line.startswith( 'bst_find_package' ):
            index = modified.index( line ) + 1

    if index == 0:
        # if there was no bst_find_package() yet then append at the end
        index = len(modified)

    modified.insert( index, 'bst_find_package(%s)' % package )

    return '\n'.join( modified )


# EOF
