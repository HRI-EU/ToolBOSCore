#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  lists the dependencies of a package
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


import logging
import os

from ToolBOSCore.BuildSystem.BuildSystemTools import requireTopLevelDir
from ToolBOSCore.Packages.AbstractPackage     import AbstractPackage
from ToolBOSCore.Packages                     import BSTPackage
from ToolBOSCore.Packages                     import ProjectProperties
from ToolBOSCore.Util                         import Any
from ToolBOSCore.Util                         import FastScript


def listDependencies( canonicalPath, reverse=False, recursive=True,
                      missingOnly=False, asList=False, showDuplicates=False ):

    if missingOnly:
        asList  = True
        reverse = False


    # if '.' provided as package, read dependencies from ./pkgInfo.py,
    # otherwise work on SIT level

    if canonicalPath == '.' and not reverse:
        try:
            requireTopLevelDir()
        except RuntimeError as details:
            raise SystemExit( details )

        package = BSTPackage.BSTSourcePackage()
        package.open( os.getcwd() )

    else:
        if canonicalPath == '.':               # implies reverse == True
            requireTopLevelDir()

            package = BSTPackage.BSTSourcePackage()
            package.open( os.getcwd() )
            canonicalPath = package.detector.canonicalPath


        # strip-off the SIT part if provided, and convert to URL-style
        ProjectProperties.requireIsCanonicalPath( canonicalPath )
        packageURL = 'sit://' + canonicalPath
        package    = BSTPackage.BSTProxyInstalledPackage( packageURL )

        try:
            package.open()
        except AssertionError as details:
            logging.error( details )
            logging.error( '%s: No such package in SIT', canonicalPath )
            raise SystemExit()


    if reverse:
        package.retrieveReverseDependencies( recursive )
    else:
        package.retrieveDependencies( recursive, normalDeps=True, buildDeps=False )


    if asList:
        _showAsList( package, reverse, missingOnly )
    else:
        _showAsTree( package, reverse, recursive, showDuplicates )


#----------------------------------------------------------------------------
# Private functions
#----------------------------------------------------------------------------


def _showAsList( package, reverse, missingOnly ):
    """
        Direcyly print list of [reverse] dependencies onto console.
    """
    Any.requireIsInstance( package, BSTPackage.BSTPackage )
    Any.requireIsBool( reverse )

    data = package.revDepSet if reverse else package.depSet
    Any.requireIsSet( data )

    packageURLs = list( data )
    packageURLs.sort()

    for packageURL in packageURLs:
        Any.requireIsTextNonEmpty( packageURL )

        if missingOnly:
            try:
                if not ProjectProperties.isInstalled( packageURL ):
                    print( packageURL )

            except EnvironmentError:
                # unknown, treat as "not installed"
                print( packageURL )

        else:
            print( packageURL )


def _showAsTree( package, reverse, recursive, showDuplicates ):
    """
        Convert BSTPackage-tree representation to traditional
        FastScript-tree format, to re-use existing code.
    """
    Any.requireIsInstance( package, AbstractPackage )
    Any.requireIsBool( reverse )
    Any.requireIsBool( recursive )
    Any.requireIsBool( showDuplicates )

    treeData = _convertToTree( package, reverse, recursive,
                               showDuplicates, set() )
    Any.requireIsList( treeData )

    treeText = FastScript.getTreeView( treeData )
    Any.requireIsText( treeText)

    print( treeText.strip() )


def _convertToTree( package, reverse, recursive, showDuplicates, duplicateData ):
    Any.requireIsInstance( package, AbstractPackage )
    Any.requireIsBool( reverse )
    Any.requireIsBool( recursive )
    Any.requireIsBool( showDuplicates )

    treeData = []
    origData = package.revDepTree if reverse else package.depTree
    Any.requireIsList( origData )

    for depPackage in origData:
        Any.requireIsInstance( depPackage, AbstractPackage )

        if showDuplicates or depPackage.url not in duplicateData:
            treeData.append( depPackage.url )
            duplicateData.add( depPackage.url )

            if recursive:
                tmp = _convertToTree( depPackage, reverse, recursive,
                                      showDuplicates, duplicateData )

                if tmp:
                    treeData.append( tmp )

    return treeData


# EOF
