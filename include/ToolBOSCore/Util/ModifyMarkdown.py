#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


import logging
import os
import shutil

from ToolBOSCore.Util import Any, FastScript


def _getAllMdAndImgFilesList( src ):
    """
    returns two lists containing all the markdown files and images within specified path
    """
    Any.requireIsText( src )

    mdFiles = []
    imgFiles = []

    for root, dirs, files in os.walk( src ):
        for file in files:
            if '.md' in file:
                mdFiles.append( os.path.join( root, file ) )
            if '.png' in file:
                imgFiles.append( os.path.join( root, file ) )

    return mdFiles, imgFiles


def _copyAllFilesInList( fileList, dst ):
    """
    Copies all files in the list into the specified destination folder
    """
    Any.requireIsList( fileList )
    Any.requireIsText( dst )

    for file in fileList:
        FastScript.mkdir( dst )
        try:
            FastScript.copy( file, dst )
        except shutil.SameFileError as e:
            logging.debug( e )


def _getFilesToModify( src ):
    """
    Loops over all the markdown files and looks for files which need to be modified before running doxygen
    This function returns 2 lists:
    filesToModifyLinks: This contains list of files where the subpage link syntax need modifications
    filesToModifyImgs: This contains list of files where the image syntax needs modifications
    """
    Any.requireIsDir( src )

    filesToModifyLinks = []
    filesToModifyImgs = []

    # Loop through all md files and find filenames hyperlinked by @subpage and image syntax '!['
    for root, dirs, files in os.walk( src ):
        for file in files:
            if '.md' in file:
                fileRead = open( os.path.join( root, file ), 'r' )
                fileLines = fileRead.readlines()

                for line in fileLines:
                    if '@subpage' in line:
                        fileNameToBeModified = line.split(' ')[-1]
                        filesToModifyLinks.append( fileNameToBeModified.rstrip("\n") + '.md' )

                    if '![' in line:
                        filesToModifyImgs.append( file )

                fileRead.close()

    return  filesToModifyLinks, filesToModifyImgs


def _modifySubpageLinkSyntax( file ):
    """
    Opens given file which needs subpage link modifications and appends {#linkTopage}
    to the first line of the file
    """
    Any.requireIsText( file )

    logging.info( "modifying file: %s", file )

    original = os.path.join( root, file )
    Any.requireIsFile( original )

    tempFile = os.path.join( root, 'temp' + file )

    shutil.copyfile( original, tempFile )

    fromFile = open( tempFile )

    line = fromFile.readline().rstrip("\n")
    line = line + ' {#' + file[:-3] + '}'

    toFile = open( original, 'w' )
    toFile.write( line )
    shutil.copyfileobj( fromFile, toFile )

    # TODO: remove the temp file here
    for filename in os.listdir( root ):
        if filename.startswith( "temp" ):
            logging.debug( "removing: %s", filename )
            os.remove( os.path.join( root, filename ) )

    fromFile.close()
    toFile.close()


def _modifyImgLinkSyntax( file ):
    """
    Opens given file which needs image link syntax modifications and replaces '![title][imgPath]'
    with html image tag '<img src = imgpath>'
    """
    Any.requireIsText( file )

    original = os.path.join( root, file )
    tempFile = os.path.join( root, 'temp' + file )

    shutil.copyfile( original, tempFile )

    fromFile = open( tempFile )
    lines = fromFile.readlines()

    toFile = open( original, 'w' )

    for line in lines:
        if '![' in line:
            imgpath = doxySourceFilesPath + '/' + line[line.find("(") + 1:line.find(")")]
            line = "<img src=\"" + imgpath + "\">"

            toFile.write(line)
        else:
            toFile.write(line)

    # remove the temp file here
    for filename in os.listdir( root ):
        if filename.startswith("temp"):
            logging.debug( "removing: %s", filename )
            os.remove(os.path.join( root, filename ) )

    fromFile.close()
    toFile.close()


if __name__ == "__main__":

    projectRootPath     = os.getcwd()
    doxySourceFilesPath = os.path.join( projectRootPath, 'doc/ModifiedMdFiles' )
    
    # Returns lists of md files and Img files from the given path recursively
    mdFiles, imgFiles = _getAllMdAndImgFilesList( projectRootPath )

    # Copy all markdown files from source recursively to the common markdown file directory
    _copyAllFilesInList( mdFiles, doxySourceFilesPath )

    filesToModifyLinks, filesToModifyImgs = _getFilesToModify( doxySourceFilesPath )

    # Copy all Img files in all directories to the common md files directory for doxygen
    _copyAllFilesInList( imgFiles, doxySourceFilesPath )

    # Replace markdown syntax for github with doxygen
    for root, dirs, files in os.walk( doxySourceFilesPath ):
        for file in files:
            if file in filesToModifyLinks:
                _modifySubpageLinkSyntax( file )

            if file in set(filesToModifyImgs):
                _modifyImgLinkSyntax( file )

