#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  launches the unit testing
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
import subprocess
import tempfile
import unittest

from six import StringIO

from ToolBOSCore.Tools import SVN
from ToolBOSCore.Util  import Any, FastScript


origDir = os.getcwd()
svnRepo = os.path.join( origDir, 'TestRepo' )


class TestSubversion( unittest.TestCase ):

    def setUp( self ):
        if not FastScript.getEnv( 'VERBOSE' ) == 'TRUE':
            Any.setDebugLevel( 1 )

        # always start from defined location
        FastScript.changeDirectory( origDir )


    def test_svn_create( self ):
        tmpDir = tempfile.mkdtemp( prefix='test-' )
        logging.info( 'creating repository in %s' % tmpDir )

        repo   = SVN.SVNRepository( 'file://' + tmpDir + '/Example/Foo' )
        self.assertFalse( repo.exists() )

        repo.create()
        self.assertTrue( repo.exists() )

        FastScript.remove( tmpDir )


    def test_svn_checkout( self ):
        url    = 'file://' + svnRepo
        tmpDir = tempfile.mkdtemp( prefix='test-' )
        output = StringIO()

        FastScript.changeDirectory( tmpDir )
        repo = SVN.SVNRepository( url )
        repo.checkout( output=output )

        self.assertTrue( output.getvalue().find( 'Checked out revision' ) != -1 )

        self.assertTrue( os.path.isdir(  'TestRepo'            ) )
        self.assertTrue( os.path.isdir(  'TestRepo/.svn'       ) )
        self.assertTrue( os.path.isfile( 'TestRepo/README.txt' ) )

        FastScript.changeDirectory( origDir )
        FastScript.remove( tmpDir )


    def test_svn_exists( self ):
        repo   = SVN.SVNRepository( 'file://' + svnRepo )
        result = repo.exists()

        self.assertTrue( result )


    def test_svn_status( self ):
        url    = 'file://' + svnRepo
        tmpDir = tempfile.mkdtemp( prefix='test-' )
        output = StringIO()

        FastScript.changeDirectory( tmpDir )

        repo = SVN.SVNRepository( url )
        repo.checkout( revision=1, output=output )

        self.assertTrue( os.path.isdir(  'TestRepo' ) )

        FastScript.changeDirectory( 'TestRepo' )
        output.truncate( 0 )

        vcs = SVN.WorkingCopy()
        vcs.status( True, output )

        returned = output.getvalue()

        # since we did not modify or commit anything, output should be empty
        self.assertEqual( returned, 'Status against revision:      1\n' )

        # create some file
        FastScript.setFileContent( 'NewFile.txt', "Hello, World!\n" )

        output.truncate( 0 )

        vcs = SVN.WorkingCopy()
        vcs.status( True, output )

        returned = output.getvalue()

        # now the new / unknown file must be listed
        expected = '''?                    NewFile.txt
Status against revision:      1
'''
        self.assertEqual( returned, expected )

        FastScript.changeDirectory( origDir )
        FastScript.remove( tmpDir )


    def test_svn_commit( self ):
        # copy repository to temporary location
        tmpSVN = tempfile.mkdtemp( prefix='test-' )
        FastScript.remove( tmpSVN)   # shutil.copytree() will complain if exists
        Any.requireIsDirNonEmpty( svnRepo )
        shutil.copytree( svnRepo, tmpSVN + "/TestRepo" )

        # when using Git the test repo may lack some required empty
        # directories, thus ensure that they exists after copying
        FastScript.mkdir( os.path.join( tmpSVN + "/TestRepo/db/transactions" ) )
        FastScript.mkdir( os.path.join( tmpSVN + "/TestRepo/db/txn-protorevs" ) )

        # checkout from temporary location
        tmpWC  = tempfile.mkdtemp( prefix='test-' )
        url    = 'file://' + tmpSVN + '/' + 'TestRepo'
        output = StringIO()
        FastScript.changeDirectory( tmpWC )

        repo = SVN.SVNRepository( url )
        repo.checkout( revision=1, output=output )

        output.truncate( 0 )

        # create a file within working copy and commit it to repository
        FastScript.changeDirectory( 'TestRepo' )
        FastScript.setFileContent( 'NewFile.txt', 'File created by unittest.\n' )


        vcs = SVN.WorkingCopy()
        vcs.add( [ 'NewFile.txt' ], output=output )

        try:
            vcs.commitUpstream( "committed by unittest", output=output )
        except subprocess.CalledProcessError:
            logging.error( output.getvalue() )
            self.fail( 'problem in comitting files' )

        self.assertTrue( output.getvalue().find( 'Committed revision' ) > 0 )

        FastScript.changeDirectory( origDir )
        FastScript.remove( tmpSVN )
        FastScript.remove( tmpWC )


    def test_svn_update( self ):
        url    = 'file://' + svnRepo
        tmpDir = tempfile.mkdtemp( prefix='test-' )
        output = StringIO()

        FastScript.changeDirectory( tmpDir )

        repo = SVN.SVNRepository( url )
        repo.checkout( revision=1, output=output )

        self.assertTrue( os.path.isdir(  'TestRepo' ) )

        FastScript.changeDirectory( 'TestRepo' )
        output.truncate( 0 )

        vcs = SVN.WorkingCopy()
        vcs.setDryRun( True )
        vcs.update()

        FastScript.changeDirectory( origDir )
        FastScript.remove( tmpDir )


    def test_svn_diff( self ):
        url    = 'file://' + svnRepo
        tmpDir = tempfile.mkdtemp( prefix='test-' )
        output = StringIO()

        FastScript.changeDirectory( tmpDir )

        repo = SVN.SVNRepository( url )
        repo.checkout( revision=1, output=output )

        self.assertTrue( os.path.isdir(  'TestRepo' ) )

        FastScript.changeDirectory( 'TestRepo' )
        output.truncate( 0 )

        FastScript.setFileContent( 'README.txt', 'Hello, Earth!\n' )

        vcs = SVN.WorkingCopy()
        vcs.diff( output=output )

        self.assertTrue( output.getvalue().find( '-Hello, World!' ) > 0 )
        self.assertTrue( output.getvalue().find( '+Hello, Earth!' ) > 0 )

        FastScript.changeDirectory( origDir )
        FastScript.remove( tmpDir )


if __name__ == '__main__':
    unittest.main()


# EOF
