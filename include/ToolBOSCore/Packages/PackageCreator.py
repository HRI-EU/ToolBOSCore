# -*- coding: utf-8 -*-
#
#  Functions to create a new package
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
import random
import shutil

from ToolBOSCore.Packages.PackageDetector   import PackageDetector
from ToolBOSCore.Packages.ProjectProperties import requireIsCanonicalPath
from ToolBOSCore.Settings                   import ToolBOSConf
from ToolBOSCore.Storage                    import SIT
from ToolBOSCore.Storage.BashSrc            import BashSrcWriter
from ToolBOSCore.Storage.CmdSrc             import CmdSrcWriter
from ToolBOSCore.Storage.PackageVar         import PackageVarCmakeWriter
from ToolBOSCore.Storage.PkgInfoWriter      import PkgInfoWriter
from ToolBOSCore.Util                       import Any, FastScript, TemplateEngine


# location of core templates such as Master, C_Library etc.
templateDir_core = TemplateEngine.templateDir

# location of higher-level templates such as BBCMs etc.
templateDir      = os.path.join( SIT.getPath(),
                                 ToolBOSConf.getConfigOption( 'package_pkgCreator' ),
                                 'etc/mako-templates' )


class PackageCreator( object ):

    # some templates should not be directly visible to the users,
    # e.g. the Software Quality Guideline, if False they will be hidden
    # in the Package Creator GUI (TBCORE-1201)

    show = True


    def __init__( self, packageName, packageVersion, values=None,
                  outputDir='', flatStyle=False ):
        Any.requireIsTextNonEmpty( packageName )
        Any.requireIsTextNonEmpty( packageVersion )
        Any.requireIsText( outputDir )
        Any.requireIsBool( flatStyle )

        self.packageName      = packageName
        self.packageVersion   = packageVersion
        self.templateDir      = templateDir
        self.templateDir_core = templateDir_core
        self.outputDir        = outputDir
        self.flatStyle        = flatStyle

        if flatStyle:
            # modern directory structure, e.g. src/ directly in project root
            self.dstDir = os.path.join( outputDir, packageName )
        else:
            # legacy directory structure with version-directory
            self.dstDir = os.path.join( outputDir, packageName, packageVersion )


        # replacement map etc. passed to templating engine
        self.values         = { 'flatStyle'      : flatStyle,
                                'packageCategory': 'Libraries',
                                'packageName'    : packageName,
                                'PACKAGENAME'    : packageName.upper(),
                                'packageVersion' : packageVersion }

        try:
            if values is None:
                self.force  = False
            else:
                Any.requireIsDict( values )
                Any.requireIsBool( values['force'] )
                self.force      = values['force']
        except KeyError:                         # not defined
            self.force      = False

        if os.path.exists( self.dstDir ) and not self.force:
            raise ValueError( '%s: directory already exists' % self.dstDir )

        if values:
            Any.requireIsDict( values )
            self.values.update( values )


    def createMainPackage( self ):
        """
            Creates a new package with the provided name and version.
            A set of default directories and files will be placed inside.
        """
        tmp = PackageCreator_Master( self.packageName,
                                     self.packageVersion,
                                     self.values,
                                     self.outputDir,
                                     self.flatStyle )

        tmp.run()


    def run( self ):
        """
            Abstract function to be implemented by derived classes.
        """
        msg = 'The template you are using did not implement run()  :-/'
        raise NotImplementedError( msg )


    def setValidFlags( self ):
        """
            Unless provided by the user the valid-flags will be randomized
            and put into self.values .
        """
        if not 'validFlags' in self.values:
            self.values[ 'validFlags' ] = randomizeValidityFlags()

        Any.requireIsTuple( self.values[ 'validFlags' ] )
        self.values[ 'validFlag'   ] = self.values[ 'validFlags' ][0]
        self.values[ 'invalidFlag' ] = self.values[ 'validFlags' ][1]

        logging.debug( 'valid flag:   %s', self.values[ 'validFlag'   ] )
        logging.debug( 'invalid flag: %s', self.values[ 'invalidFlag' ] )


    def templatize( self, srcFile, dstFile ):
        """
            Runs the templating engine, applying values from self.values
            onto the template file 'srcFile', writing results into 'dstFile'.
        """
        TemplateEngine.run( srcFile, dstFile, self.values )


    def copyVerbatim( self, srcFile, dstFile ):
        """
            Copies a file, with standardized info log.
        """
        Any.requireIsFile( srcFile )

        FastScript.mkdir( os.path.dirname( dstFile ) )  # ensure dstDir exists

        logging.info( 'processing %s', dstFile )

        # unlike shutil.copyfile() the shutil.copy2() function also copies
        # attributes such as executable flag (e.g. needed for unittest.sh etc.)
        shutil.copy2( srcFile, dstFile )


class PackageCreator_Master( PackageCreator ):
    """
        Master package template, all other templates internally use this
        for creating the skeleton directory structure.

        Creates a new package with the provided name and version.
        A set of default directories and files will be placed inside.
    """
    def run( self ):
        if not 'category' in self.values:
            logging.info( 'please check SIT category in pkgInfo.py!' )
            self.values.update( { 'category': 'Libraries' } )

        if not 'customPkgInfo' in self.values:
            self.values.update( { 'customPkgInfo': '' } )

        srcDir = os.path.join( self.templateDir_core, 'master' )
        dstDir = self.dstDir

        Any.requireIsDir( srcDir )

        self.templatize( os.path.join( srcDir, 'pkgInfo.py.mako' ),
                         os.path.join( dstDir, 'pkgInfo.py' ) )

        self.copyVerbatim( os.path.join( srcDir, 'unittest.sh' ),
                           os.path.join( dstDir, 'unittest.sh' ) )


class PackageCreator_CMakeProject( PackageCreator ):
    """
        Creates an empty package with a boilerplate CMakeLists.txt.
    """
    def run( self ):
        package_cutest     = ToolBOSConf.getConfigOption( 'package_cutest' )
        package_toolboslib = ToolBOSConf.getConfigOption( 'package_toolboslib' )

        if not 'buildRules' in self.values:

            # When using default build rules, allow customization of
            # file search patterns (TBCORE-971)

            if not 'srcFilesPattern' in self.values:
                self.values[ 'srcFilesPattern' ] = 'src/*.c src/*.cpp'

            if not 'exeFilesPattern' in self.values:
                self.values[ 'exeFilesPattern' ] = '''bin/*.c bin/*.cpp examples/*.c examples/*.cpp
                    test/*.c test/*.cpp'''

            Any.requireIsTextNonEmpty( self.values[ 'srcFilesPattern' ] )
            Any.requireIsTextNonEmpty( self.values[ 'exeFilesPattern' ] )

            buildRules = '''file(GLOB SRC_FILES %(srcFilesPattern)s)

bst_build_libraries("${SRC_FILES}" "${PROJECT_NAME}" "${BST_LIBRARIES_SHARED}")


file(GLOB EXE_FILES %(exeFilesPattern)s)

bst_build_executables("${EXE_FILES}" "${BST_LIBRARIES_SHARED}")''' % \
                         { 'srcFilesPattern': self.values[ 'srcFilesPattern' ],
                           'exeFilesPattern': self.values[ 'exeFilesPattern' ] }


            # Add custom pre-/post-build rules if specified (TBCORE-971)

            if 'preBuildRules' in self.values:
                Any.requireIsTextNonEmpty( self.values[ 'preBuildRules'] )
                buildRules = self.values[ 'preBuildRules'] + '\n\n' + buildRules

            if 'postBuildRules' in self.values:
                Any.requireIsTextNonEmpty( self.values[ 'postBuildRules'] )
                buildRules = buildRules + '\n\n' + self.values[ 'postBuildRules']

            self.values.update( { 'buildRules': buildRules } )


        if not 'dependencies' in self.values:
            self.values[ 'dependencies' ] = [ package_toolboslib,
                                              package_cutest ]

        self.createMainPackage()

        srcDir = os.path.join( self.templateDir_core, 'CMakeProject' )
        dstDir = self.dstDir

        self.templatize( os.path.join( srcDir, 'CMakeLists.txt.mako' ),
                         os.path.join( dstDir, 'CMakeLists.txt' ) )


    def createCMakePackage( self ):
        """
            Creates a new package with the provided name and version.
            A set of default directories and files will be placed inside.
        """
        tmp = PackageCreator_CMakeProject( self.packageName,
                                           self.packageVersion,
                                           self.values,
                                           self.outputDir,
                                           self.flatStyle )

        tmp.run()


class PackageCreator_C_BBCM( PackageCreator_CMakeProject ):
    """
        Creates a BBCM component for wrapping code in RTBOS.
    """
    def run( self ):
        package_cutest     = ToolBOSConf.getConfigOption( 'package_cutest' )
        package_libxml     = ToolBOSConf.getConfigOption( 'package_libxml' )
        package_toolboslib = ToolBOSConf.getConfigOption( 'package_toolboslib' )

        if not 'category' in self.values:
            self.values[ 'category' ] = 'Modules/BBCM/Testing'

        if not 'dependencies' in self.values:
            self.values[ 'dependencies' ] = [ package_toolboslib,
                                              package_cutest,
                                              package_libxml ]

        Any.requireMsg( self.packageName[0].isupper() == True,
                        'BBCM template requires package name to start uppercase' )

        self.setValidFlags()

        self.createCMakePackage()

        srcDir = os.path.join( self.templateDir, 'C_BBCM' )
        dstDir = self.dstDir

        self.templatize( os.path.join( srcDir, 'packageName.c.mako' ),
                         os.path.join( dstDir, 'src', '%s.c' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'packageName.h.mako' ),
                         os.path.join( dstDir, 'src', '%s.h' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'packageName_ext.c.mako' ),
                         os.path.join( dstDir, 'src', '%s_ext.c' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'packageName_ext.h.mako' ),
                         os.path.join( dstDir, 'src', '%s_ext.h' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'packageName_info.c.mako' ),
                         os.path.join( dstDir, 'src', '%s_info.c' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'packageName_init.c.mako' ),
                         os.path.join( dstDir, 'src', '%s_init.c' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'unittest.c.mako' ),
                         os.path.join( dstDir, 'test', 'unittest.c' ) )


class PackageCreator_C_BBDM( PackageCreator_CMakeProject ):
    """
        Creates a BBDM component for wrapping data in RTBOS.
    """
    def run( self ):
        Any.requireMsg( len(self.packageName) > 4, "package name is too short" )
        Any.requireMsg( self.packageName.startswith( 'BBDM' ), "package name must start with 'BBDM'" )

        package_cutest     = ToolBOSConf.getConfigOption( 'package_cutest' )
        package_libxml     = ToolBOSConf.getConfigOption( 'package_libxml' )
        package_toolboslib = ToolBOSConf.getConfigOption( 'package_toolboslib' )

        if not 'category' in self.values:
            self.values[ 'category' ] = 'Modules/BBDM'

        if not 'dependencies' in self.values:
            self.values[ 'dependencies' ] = [ package_toolboslib,
                                              package_cutest,
                                              package_libxml ]

        self.values[ 'DataType' ] = self.packageName[4:]
        self.values[ 'DATATYPE' ] = self.packageName[4:].upper()

        self.setValidFlags()

        self.createCMakePackage()

        srcDir = os.path.join( self.templateDir, 'C_BBDM' )
        dstDir = self.dstDir

        self.templatize( os.path.join( srcDir, 'packageName.c.mako' ),
                         os.path.join( dstDir, 'src', '%s.c' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'packageName.h.mako' ),
                         os.path.join( dstDir, 'src', '%s.h' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'packageName_ext.c.mako' ),
                         os.path.join( dstDir, 'src', '%s_ext.c' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'packageName_ext.h.mako' ),
                         os.path.join( dstDir, 'src', '%s_ext.h' % self.packageName ) )

        # overwrite the file from master template
        self.copyVerbatim( os.path.join( srcDir, 'unittest.sh' ),
                           os.path.join( dstDir, 'unittest.sh' ) )

        self.templatize( os.path.join( srcDir, 'TestCopy.c.mako' ),
                         os.path.join( dstDir, 'test', 'TestCopy.c' ) )

        self.templatize( os.path.join( srcDir, 'TestInstanceName.c.mako' ),
                         os.path.join( dstDir, 'test', 'TestInstanceName.c' ) )

        self.templatize( os.path.join( srcDir, 'TestSuite.c.mako' ),
                         os.path.join( dstDir, 'test', 'TestSuite.c' ) )

        self.templatize( os.path.join( srcDir, 'TestTimestep.c.mako' ),
                         os.path.join( dstDir, 'test', 'TestTimestep.c' ) )


class PackageCreator_C_Library( PackageCreator_CMakeProject ):
    """
        Creates a simple C library package.
    """
    def run( self ):
        package_cutest     = ToolBOSConf.getConfigOption( 'package_cutest' )
        package_toolboslib = ToolBOSConf.getConfigOption( 'package_toolboslib' )

        if not 'category' in self.values:
            self.values[ 'category' ] = 'Libraries'

        if not 'dependencies' in self.values:
            self.values[ 'dependencies' ] = [ package_toolboslib,
                                              package_cutest ]

        self.setValidFlags()

        self.createCMakePackage()

        srcDir = os.path.join( self.templateDir_core, 'C_Library' )
        dstDir = self.dstDir

        self.templatize( os.path.join( srcDir, 'packageName.c.mako' ),
                         os.path.join( dstDir, 'src', '%s.c' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'packageName.h.mako' ),
                         os.path.join( dstDir, 'src', '%s.h' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'unittest.c.mako' ),
                         os.path.join( dstDir, 'test', 'unittest.c' ) )


class PackageCreator_C_MainProgram( PackageCreator_CMakeProject ):
    """
        Creates a simple C main program package.
    """
    def run( self ):
        package_toolboslib = ToolBOSConf.getConfigOption( 'package_toolboslib' )
        if not 'category' in self.values:
            self.values[ 'category' ] = 'Applications'

        if not 'dependencies' in self.values:
            self.values[ 'dependencies' ] = [ package_toolboslib ]

        self.createCMakePackage()

        srcDir = os.path.join( self.templateDir_core, 'C_MainProgram' )
        dstDir = self.dstDir

        self.templatize( os.path.join( srcDir, 'main.c.mako' ),
                         os.path.join( dstDir, 'bin', 'main.c' ) )

        FastScript.remove( os.path.join( dstDir, 'lib' ) )
        FastScript.remove( os.path.join( dstDir, 'src' ) )
        FastScript.remove( os.path.join( dstDir, 'unittest.sh' ) )


class PackageCreator_Cpp_Class( PackageCreator_CMakeProject ):
    """
        Creates a simple C++ class package.
    """
    def run( self ):
        package_toolboslib = ToolBOSConf.getConfigOption( 'package_toolboslib' )

        if not 'category' in self.values:
            self.values[ 'category' ] = 'Libraries'

        if not 'dependencies' in self.values:
            self.values[ 'dependencies' ] = [ package_toolboslib ]

        self.createCMakePackage()

        srcDir = os.path.join( self.templateDir_core, 'Cpp_Class' )
        dstDir = self.dstDir

        self.templatize( os.path.join( srcDir, 'packageName.cpp.mako' ),
                         os.path.join( dstDir, 'src', '%s.cpp' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'packageName.h.mako' ),
                         os.path.join( dstDir, 'src', '%s.h' % self.packageName ) )

        FastScript.remove( os.path.join( dstDir, 'unittest.sh' ) )


class PackageCreator_Cpp_MainProgram( PackageCreator_CMakeProject ):
    """
        Creates a simple C main program package.
    """
    def run( self ):
        package_toolboslib = ToolBOSConf.getConfigOption( 'package_toolboslib' )

        if not 'category' in self.values:
            self.values[ 'category' ] = 'Applications'

        if not 'dependencies' in self.values:
            self.values[ 'dependencies' ] = [ package_toolboslib ]


        self.createCMakePackage()

        srcDir = os.path.join( self.templateDir_core, 'Cpp_MainProgram' )
        dstDir = self.dstDir

        self.templatize( os.path.join( srcDir, 'main.cpp.mako' ),
                         os.path.join( dstDir, 'bin', 'main.cpp' ) )

        FastScript.remove( os.path.join( dstDir, 'lib' ) )
        FastScript.remove( os.path.join( dstDir, 'src' ) )
        FastScript.remove( os.path.join( dstDir, 'unittest.sh' ) )


class PackageCreator_External_GNU_Autotools( PackageCreator ):
    """
        Creates a skeleton package for wrapping an external (3rd party)
        software, which needs to be compiled first (e.g. OSS).
    """
    def run( self ):
        if not 'category' in self.values:
            self.values[ 'category' ] = 'External'

        if not 'customPkgInfo' in self.values:
            self.values[ 'customPkgInfo' ] = '''
# envVars        = [ ( 'PATH', '${INSTALL_ROOT}/bin:${PATH}' ),
#                    ( 'LD_LIBRARY_PATH', '${INSTALL_ROOT}/lib/${MAKEFILE_PLATFORM}:${LD_LIBRARY_PATH}' ) ]

linkAllLibraries = True

install          = [ ( 'precompiled/package', '.' ) ]
'''

        self.createMainPackage()

        srcDir    = os.path.join( self.templateDir, 'External_GNU_Autotools' )
        dstDir    = self.dstDir

        for fileName in FastScript.getFilesInDir( srcDir, ):
            srcFile = os.path.join( srcDir, fileName )
            dstFile = os.path.join( dstDir, fileName )
            self.copyVerbatim( srcFile, dstFile )

        FastScript.remove( os.path.join( dstDir, 'unittest.sh' ) )

        # create exemplarily (fake-)tarball file, and interface-symlink to it
        tarball  = os.path.join( dstDir, 'src', 'Example-1.0-src.tar.bz2' )
        symlink  = os.path.join( dstDir, 'src', 'sources.tar.bz2' )

        logging.info( 'processing %s', tarball )
        FastScript.setFileContent( tarball, '' )

        logging.info( 'processing %s', symlink )
        os.symlink( 'Example-1.0-src.tar.bz2', symlink )


        # create basic packageVar.cmake
        #
        # Note: for some reason calling FastScript.changeDir() with rel. path failed,
        # continuing with absolute path as workaround
        dstDir  = os.path.abspath( dstDir )
        Any.requireIsDir( dstDir )

        details = PackageDetector( dstDir )
        details.retrieveMakefileInfo()

        fileName = os.path.join( dstDir, 'packageVar.cmake' )
        PackageVarCmakeWriter( details ).write( fileName )


class PackageCreator_External_CMake_in_tree_build( PackageCreator ):
    """
        Creates a skeleton package for wrapping an external (3rd party)
        software, which needs to be compiled first (e.g. OSS).
    """

    def run(self):
        if not 'category' in self.values:
            self.values['category'] = 'External'

        if not 'customPkgInfo' in self.values:
            self.values[ 'customPkgInfo' ] = '''
# envVars        = [ ( 'PATH', '${INSTALL_ROOT}/bin:${PATH}' ),
#                    ( 'LD_LIBRARY_PATH', '${INSTALL_ROOT}/lib/${MAKEFILE_PLATFORM}:${LD_LIBRARY_PATH}' ) ]

linkAllLibraries = True

usePatchlevels   = True

patchlevel       = 0
'''

        self.createMainPackage()

        srcDir = os.path.join(self.templateDir, 'External_CMake_in_tree_build' )
        dstDir = self.dstDir

        for fileName in FastScript.getFilesInDir( srcDir ):
            srcFile = os.path.join( srcDir, fileName )
            dstFile = os.path.join( dstDir, fileName )
            self.copyVerbatim( srcFile, dstFile )

        FastScript.remove(os.path.join(dstDir, 'unittest.sh'))

        # create exemplarily (fake-)tarball file, and interface-symlink to it
        tarball = os.path.join(dstDir, 'src', 'Example-1.0-src.tar.bz2')
        symlink = os.path.join(dstDir, 'src', 'sources.tar.bz2')

        logging.info('processing %s', tarball)
        FastScript.setFileContent(tarball, '')

        logging.info('processing %s', symlink)
        os.symlink('Example-1.0-src.tar.bz2', symlink)

        # create basic packageVar.cmake
        #
        # Note: for some reason calling FastScript.changeDirectory() with rel. path failed,
        # continuing with absolute path as workaround
        dstDir = os.path.abspath(dstDir)
        Any.requireIsDir(dstDir)

        details = PackageDetector(dstDir)
        details.retrieveMakefileInfo()

        fileName = os.path.join(dstDir, 'packageVar.cmake')
        PackageVarCmakeWriter(details).write(fileName)


class PackageCreator_External_CMake_out_of_tree_build( PackageCreator ):
    """
        Creates a skeleton package for wrapping an external (3rd party)
        software, which needs to be compiled first (e.g. OSS).
    """
    def run( self ):
        if not 'category' in self.values:
            self.values[ 'category' ] = 'External'

        if not 'customPkgInfo' in self.values:
            self.values[ 'customPkgInfo' ] = '''
# envVars        = [ ( 'PATH', '${INSTALL_ROOT}/bin:${PATH}' ),
#                    ( 'LD_LIBRARY_PATH', '${INSTALL_ROOT}/lib/${MAKEFILE_PLATFORM}:${LD_LIBRARY_PATH}' ) ]

linkAllLibraries = True

usePatchlevels   = True

patchlevel       = 0
'''

        self.createMainPackage()

        srcDir    = os.path.join( self.templateDir, 'External_CMake_out_of_tree_build' )
        dstDir    = self.dstDir

        for fileName in FastScript.getFilesInDir( srcDir ):
            srcFile = os.path.join( srcDir, fileName )
            dstFile = os.path.join( dstDir, fileName )
            self.copyVerbatim( srcFile, dstFile )

        FastScript.remove( os.path.join( dstDir, 'unittest.sh' ) )

        # create exemplarily (fake-)tarball file, and interface-symlink to it
        tarball  = os.path.join( dstDir, 'src', 'Example-1.0-src.tar.bz2' )
        symlink  = os.path.join( dstDir, 'src', 'sources.tar.bz2' )

        logging.info( 'processing %s', tarball )
        FastScript.setFileContent( tarball, '' )

        logging.info( 'processing %s', symlink )
        os.symlink( 'Example-1.0-src.tar.bz2', symlink )


        # create basic packageVar.cmake
        #
        # Note: for some reason calling FastScript.changeDirectory() with rel. path failed,
        # continuing with absolute path as workaround
        dstDir  = os.path.abspath( dstDir )
        Any.requireIsDir( dstDir )

        details = PackageDetector( dstDir )
        details.retrieveMakefileInfo()

        fileName = os.path.join( dstDir, 'packageVar.cmake' )
        PackageVarCmakeWriter( details ).write( fileName )


class PackageCreator_External_without_compilation( PackageCreator ):
    """
        Creates a skeleton package for wrapping an external (3rd party)
        software, which does not need to be compiled (e.g. closed-source).
    """
    def run( self ):
        if not 'category' in self.values:
            self.values[ 'category' ] = 'External'

        if not 'buildRules' in self.values:
            self.values[ 'buildRules' ] = '''# This is a dummy file needed by various aux. scripts.
#
# The actual build instructions can be found in the compile.sh.
'''

        if not 'customPkgInfo' in self.values:
            self.values[ 'customPkgInfo' ] = '''
# envVars        = [ ( 'PATH', '${INSTALL_ROOT}/bin:${PATH}' ),
#                    ( 'LD_LIBRARY_PATH', '${INSTALL_ROOT}/lib/${MAKEFILE_PLATFORM}:${LD_LIBRARY_PATH}' ) ]

linkAllLibraries = True

install          = [ ( 'precompiled/package', '.' ) ]
'''

        self.createMainPackage()

        srcDir    = os.path.join( self.templateDir, 'External_without_compilation' )
        dstDir    = self.dstDir

        self.copyVerbatim( os.path.join( srcDir, 'HowTo.txt' ),
                           os.path.join( dstDir, 'HowTo.txt' ) )

        self.copyVerbatim( os.path.join( srcDir, 'pre-configure.sh' ),
                           os.path.join( dstDir, 'pre-configure.sh' ) )

        FastScript.remove( os.path.join( dstDir, 'unittest.sh' ) )

        # create exemplarily (fake-)tarball file, and interface-symlink to it
        tarball  = os.path.join( dstDir, 'src', 'Example-1.0-precompiled.tar.bz2' )
        symlink  = os.path.join( dstDir, 'src', 'package.tar.bz2' )

        logging.info( 'processing %s', tarball )
        FastScript.setFileContent( tarball, '' )

        logging.info( 'processing %s', symlink )
        os.symlink( 'Example-1.0-precompiled.tar.bz2', symlink )


        # create basic packageVar.cmake
        #
        # Note: for some reason calling FastScript.changeDirectory() with rel. path failed,
        # continuing with absolute path as workaround
        dstDir  = os.path.abspath( dstDir )
        Any.requireIsDir( dstDir )

        details = PackageDetector( dstDir )
        details.retrieveMakefileInfo()

        fileName = os.path.join( dstDir, 'packageVar.cmake' )
        PackageVarCmakeWriter( details ).write( fileName )


class PackageCreator_JetBrains_Common_Config( PackageCreator ):
    """
        Creates an IDE config directory within the current working directory.
    """
    show = False                                 # hide in GUI (it's special)


    def run( self ):
        logging.info( 'This abstract template alone is not useful,' )
        logging.info( 'please choose a derived one instead.' )


    def runCommon( self, templateName, verbatim, templatize ):
        import subprocess

        from ToolBOSCore.Platforms.Platforms import getHostPlatform
        from ToolBOSCore.Tools               import SVN

        Any.requireIsTextNonEmpty( templateName )
        Any.requireIsSet( verbatim )
        Any.requireIsDict( templatize )


        hostPlatform = getHostPlatform()

        if not 'buildDir' in self.values:
            self.values[ 'buildDir' ] = os.path.join( 'build', hostPlatform )

        if not 'MAKEFILE_PLATFORM' in self.values:
            self.values[ 'MAKEFILE_PLATFORM' ] = hostPlatform


        srcDir = os.path.join( self.templateDir, templateName )
        dstDir = self.outputDir

        for item in verbatim:
            srcFile  = os.path.join( srcDir, item )
            dstFile  = os.path.join( dstDir, item )
            self.copyVerbatim( srcFile, dstFile )

        for key, value in templatize.items():
            srcFile  = os.path.join( srcDir, key )
            dstFile  = os.path.join( dstDir, value )
            self.templatize( srcFile, dstFile )


        # enable VCS integration if SVN information found
        try:
            wc  = SVN.WorkingCopy()
            url = wc.getRepositoryURL()

        except ( FileNotFoundError, subprocess.CalledProcessError ) as details:
            # most likely is no working copy --> ignore
            url = None
            logging.debug( details )


        srcFile = os.path.join( srcDir, 'misc.xml.mako' )
        dstFile = os.path.join( dstDir, 'misc.xml' )

        if url:
            logging.info( 'VCS integration enabled' )
            self.values[ 'repositoryUrl' ] = url
        else:
            self.values[ 'repositoryUrl' ] = ''
            logging.info( 'VCS integration disabled (not an SVN working copy)' )

        self.templatize( srcFile, dstFile )


class PackageCreator_JetBrains_CLion_Config( PackageCreator_JetBrains_Common_Config ):
    """
        Creates an IDE config directory within the current working directory.
    """
    def run( self ):

        verbatim = frozenset( [ '1.0.iml',
                                'codeStyleSettings.xml',
                                'modules.xml',
                                'vcs.xml' ] )

        templatize = { 'dot.name.mako'      : '.name',
                       'workspace.xml.mako' : 'workspace.xml' }

        self.runCommon( 'JetBrains_CLion_Config', verbatim, templatize )


class PackageCreator_JetBrains_IntelliJ_Config( PackageCreator_JetBrains_Common_Config ):
    """
        Creates an IDE config directory within the current working directory.
    """
    def run( self ):

        verbatim = frozenset( [ '1.0.iml',
                                'codeStyleSettings.xml',
                                'inspectionProfiles/HRI.xml',
                                'inspectionProfiles/profiles_settings.xml',
                                'modules.xml',
                                'vcs.xml',
                                'workspace.xml' ] )

        templatize = { 'dot.name.mako' : '.name' }

        self.runCommon( 'JetBrains_IntelliJ_Config', verbatim, templatize )


class PackageCreator_JetBrains_PyCharm_Config( PackageCreator_JetBrains_Common_Config ):
    """
        Creates an IDE config directory within the current working directory.
    """
    def run( self ):

        verbatim = frozenset( [ '1.0.iml',
                                'encodings.xml',
                                'inspectionProfiles/Project_Default.xml',
                                'modules.xml',
                                'vcs.xml',
                                'workspace.xml' ] )

        templatize = {}

        self.runCommon( 'JetBrains_PyCharm_Config', verbatim, templatize )


class PackageCreator_Linux_Kernel_Module( PackageCreator ):
    """
        Creates a Linux char-driver kernel module.
    """
    def run( self ):
        if not 'category' in self.values:
            self.values[ 'category' ] = 'DeviceIO'

        if not 'dependencies' in self.values:
            self.values[ 'dependencies' ] = []

        if not 'buildRules' in self.values:
            self.values[ 'buildRules' ] = '''# invoke kbuild for the actual building
add_custom_target(${PACKAGE_NAME} ALL make
                  WORKING_DIRECTORY ${CMAKE_HOME_DIRECTORY})'''


        self.createMainPackage()

        srcDir = os.path.join( self.templateDir, 'Linux_Kernel_Module' )
        dstDir = self.dstDir

        self.templatize( os.path.join( srcDir, 'packageName.c.mako' ),
                         os.path.join( dstDir, 'src', '%s.c' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'Makefile' ),
                           os.path.join( dstDir, 'Makefile' ) )

        FastScript.remove( os.path.join( dstDir, 'unittest.sh' ) )


class PackageCreator_Python( PackageCreator ):
    """
        Creates a simple Python package.
    """
    def run( self ):
        if not 'category' in self.values:
            self.values[ 'category' ] = 'Libraries'

        if not 'dependencies' in self.values:
            self.values[ 'dependencies' ] = [ 'External/AllPython/2.7' ]

        if not 'customPkgInfo' in self.values:
            self.values[ 'customPkgInfo' ] = '''
envVars          = [ ( 'PYTHONPATH', '${INSTALL_ROOT}/include:${PYTHONPATH}' ) ]

install          = [ ( 'src', 'include' ) ]
'''

        self.createMainPackage()

        srcDir = os.path.join( self.templateDir, 'Python' )
        dstDir = self.dstDir

        FastScript.remove( os.path.join( dstDir, 'include' ) )

        self.copyVerbatim( os.path.join( srcDir, '__init__.py' ),
                           os.path.join( dstDir, 'include', self.packageName,
                                         '__init__.py' ) )

        self.copyVerbatim( os.path.join( srcDir, 'HelloWorld.py' ),
                           os.path.join( dstDir, 'include', self.packageName,
                                         'HelloWorld.py' ) )

        self.copyVerbatim( os.path.join( srcDir, 'unittest.sh' ),
                           os.path.join( dstDir, 'unittest.sh' ) )

        self.templatize(   os.path.join( srcDir, 'Unittest_HelloWorld.py.mako' ),
                           os.path.join( dstDir, 'test', 'Unittest_HelloWorld.py' ) )


class PackageCreator_Quality_Guideline( PackageCreator ):
    """
        Exports the HRI-EU Software Quality Guideline 2.0 to HTML format.
    """
    show = False                                 # hide in GUI (it's special)


    def run( self ):
        from ToolBOSCore.SoftwareQuality import Common, Rules

        if not 'category' in self.values:
            self.values[ 'category' ] = 'Intranet'

        if not 'dependencies' in self.values:
            self.values[ 'dependencies' ] = []

        srcDir = os.path.join( self.templateDir, 'QualityGuideline' )
        dstDir = self.outputDir

        self.templateDir = srcDir


        # fill 'values' with content from actual SQ rules

        rules = Rules.getRules()

        ruleIDs        = []
        level_cleanLab = []
        level_basic    = []
        level_advanced = []
        level_safety   = []

        for ( ruleID, rule ) in rules:

            ruleIDs.append( ruleID )

            if rule.sqLevel is None:
                # rule is optional, do not put into level categories
                continue

            if 'cleanLab' in rule.sqLevel:
                level_cleanLab.append( ruleID )

            if 'basic' in rule.sqLevel:
                level_basic.append( ruleID )

            if 'advanced' in rule.sqLevel:
                level_advanced.append( ruleID )

            if 'safety' in rule.sqLevel:
                level_safety.append( ruleID )


        self.values[ 'level_cleanLab'    ] = level_cleanLab
        self.values[ 'level_basic'       ] = level_basic
        self.values[ 'level_advanced'    ] = level_advanced
        self.values[ 'level_safety'      ] = level_safety

        self.values[ 'sectionKeys'       ] = Common.sectionKeys
        self.values[ 'sectionNames'      ] = Common.sectionNames
        self.values[ 'sectionObjectives' ] = Common.sectionObjectives
        self.values[ 'sqLevelDefault'    ] = Common.sqLevelDefault
        self.values[ 'sqLevelNames'      ] = Common.sqLevelNames
        self.values[ 'sqLevels'          ] = Common.sqLevels
        self.values[ 'rules'             ] = Rules.getRules()
        self.values[ 'ruleIDs'           ] = ruleIDs

        self.values[ 'documentationURL_dir' ] = ToolBOSConf.getConfigOption( 'documentationURL_dir' )

        self.templatize( os.path.join( srcDir, 'online.html.mako' ),
                         os.path.join( dstDir, 'QualityGuideline.html' ) )

        self.templatize( os.path.join( srcDir, 'printable.html.mako' ),
                         os.path.join( dstDir, 'QualityGuideline-printable.html' ) )


class PackageCreator_RTMaps_Package( PackageCreator_CMakeProject ):
    """
        Creates an empty RTMaps package structure (without any components
        inside).
    """
    def run( self ):
        if not 'category' in self.values:
            self.values[ 'category' ] = 'Modules/RTMaps'

        if not 'dependencies' in self.values:
            package_rtmaps = ToolBOSConf.getConfigOption( 'package_rtmaps' )
            Any.requireIsTextNonEmpty( package_rtmaps )
            self.values[ 'dependencies' ] = [ package_rtmaps ]

        if not 'buildRules' in self.values:
            self.values[ 'buildRules' ] = '''file(GLOB SRC_FILES src/*.c src/*.cpp)

bst_build_rtmaps_package("${SRC_FILES}" "${PROJECT_NAME}" "${BST_LIBRARIES_SHARED}")'''


        self.createCMakePackage()

        srcDir = os.path.join( self.templateDir, 'RTMaps_Package' )
        dstDir = self.dstDir

        self.copyVerbatim( os.path.join( srcDir, 'packageName.pckinfo' ),
                           os.path.join( dstDir, '%s.pckinfo' % self.packageName ) )

        FastScript.remove( os.path.join( dstDir, 'unittest.sh' ) )


        # TBCORE-1837 Create empty 'src' directory
        FastScript.mkdir( os.path.join( dstDir, 'src' ) )


class PackageCreator_RTMaps_Component( PackageCreator ):
    """
        Creates a simple RTMaps component (in C++).

        This should be invoked from within an RTMaps package's "src"
        subdirectory, e.g.:

           $ BST.py --new RTMaps_Package MyPackage 1.0
           $ cd MyPackage/1.0/src
           $ BST.py --new RTMaps_Component MyComponent 1.0
           $ cd ..
           $ BST.py --build
    """
    def run( self ):
        srcDir = os.path.join( self.templateDir, 'RTMaps_Component' )
        dstDir = '.'

        self.templatize( os.path.join( srcDir, 'maps_packageName.cpp.mako' ),
                         os.path.join( dstDir, 'maps_%s.cpp' % self.packageName ) )

        self.templatize( os.path.join( srcDir, 'maps_packageName.h.mako' ),
                         os.path.join( dstDir, 'maps_%s.h' % self.packageName ) )


def getTemplatesAvailable():
    """
        Returns a list of strings with the names of the available
        (= registered) templates.
    """
    result = []

    for symbol in globals():
        if symbol.startswith( 'PackageCreator_' ):
            result.append( symbol.replace( 'PackageCreator_', '' ) )

    result.sort()

    return result


def packageCreatorFactory( templateName, packageName, packageVersion,
                           values=None, outputDir='', flatStyle=False ):
    """
        Returns an instance of package creator for the desired template.
    """
    try:
        constructor = globals()[ 'PackageCreator_' + templateName ]
    except KeyError:
        raise ValueError( templateName + ': No such template' )

    return constructor( packageName, packageVersion, values, outputDir,
                        flatStyle )


def runTemplate( templateName, packageName, packageVersion, values=None,
                 outputDir='', flatStyle=False ):
    """
        Decorator for packageCreatorFactory() which can be used to create
        a new package. It does all the typical logging and error handling.
    """
    Any.requireIsTextNonEmpty( templateName )
    Any.requireIsTextNonEmpty( packageName )
    Any.requireIsTextNonEmpty( packageVersion )
    Any.requireIsBool( flatStyle )

    logging.debug( 'templateName=%s'  , templateName   )
    logging.debug( 'packageName=%s'   , packageName    )
    logging.debug( 'packageVersion=%s', packageVersion )
    logging.debug( 'flatStyle=%s',      flatStyle      )

    try:
        creator = packageCreatorFactory( templateName, packageName,
                                         packageVersion, values, outputDir,
                                         flatStyle )
    except KeyError:
        logging.error( '%s: No such template' % templateName )
        return False

    except ValueError as details:
        logging.error( details )
        return False


    if creator:
        try:
            creator.run()
            return True

        except ( AssertionError, ValueError ) as details:
            logging.error( details )
            return False


def makeShellfiles( projectRoot ):
    """
        Creates all the various BashSrc, pkgInfo.py etc. files.

        If <topLevelDir>/<fileName> exists it will be copied instead of
        auto-generated. This allows writing fully handcrafted files if
        necessary.

        'topLevelDir' is assumed to be a source code working copy
        (including the version, e.g. "/home/foo/mycode/Spam/42.0")

    """
    Any.requireIsDir( projectRoot )

    oldcwd = os.getcwd()
    FastScript.changeDirectory( projectRoot )


    # collect package details once (this function is internally multi-threaded)

    try:
        details = PackageDetector( projectRoot )
        details.retrieveMakefileInfo()
        details.retrieveVCSInfo()
    except AttributeError:
        raise ValueError( 'Unable to create shellfiles in path="%s", is this '
                          'a package directory?' % projectRoot )
    except ValueError as details:
        raise ValueError( details )

    FastScript.mkdir( './install' )

    if os.path.exists( 'BashSrc' ):
        logging.info( 'cp BashSrc ./install/' )
        shutil.copy2( 'BashSrc', './install/BashSrc' )
    else:
        BashSrcWriter( details ).write( './install/BashSrc'    )

    if os.path.exists( 'CmdSrc.bat' ):
        logging.info( 'cp CmdSrc.bat ./install/' )
        shutil.copy2( 'CmdSrc.bat', './install/CmdSrc.bat' )
    else:
        CmdSrcWriter(  details ).write( './install/CmdSrc.bat' )

    # Note: pkgInfo.py is always generated (merged)
    PkgInfoWriter( details ).write( './install/pkgInfo.py' )

    if os.path.exists( 'packageVar.cmake' ):
        logging.info( 'cp packageVar.cmake ./install/' )
        shutil.copy2( 'packageVar.cmake', './install/packageVar.cmake' )
    else:
        # try to generate a reasonable file (put explicitly under ./install/
        # to indicate it's a installation-temporary file
        #
        # if the user wants to handcraft it, he could move this
        # auto-generated file to ./packageVar.cmake and add it to VCS
        PackageVarCmakeWriter( details ).write( './install/packageVar.cmake' )

    FastScript.changeDirectory( oldcwd )


def uninstall( canonicalPath, cleanGlobalInstallation, dryRun=False ):
    """
         Delete a package from SIT, this includes:

            * Proxy SIT directory
            * Global SIT installation
            * BBCM *.def file
            * RTMaps index entry

        If 'cleanGlobalInstallation=True' the package will also be
        uninstalled from global SIT (if applicable). If False it
        will only be uninstalled from the proxy SIT.
    """
    from ToolBOSCore.Platforms  import Platforms
    from ToolBOSCore.Tools      import RTMaps

    requireIsCanonicalPath( canonicalPath )

    Any.requireIsBool( dryRun )

    sitProxyPath       = SIT.getPath()
    sitRootPath        = SIT.getRootPath()
    Any.requireIsTextNonEmpty( sitProxyPath )
    Any.requireIsTextNonEmpty( sitRootPath )

    installRoot_proxy  = os.path.join( sitProxyPath, canonicalPath )
    installRoot_root   = os.path.join( sitRootPath, canonicalPath )

    rtmapsVersion      = FastScript.getEnv( 'RTMAPS_VERSION' )

    logging.info( 'uninstalling %s', canonicalPath )


    logging.info( 'cleaning proxy-installation' )
    FastScript.remove( installRoot_proxy, dryRun )

    if cleanGlobalInstallation:
        logging.info( 'cleaning global-installation' )
        FastScript.remove( installRoot_root, dryRun )

    if rtmapsVersion:
        Any.requireIsTextNonEmpty( rtmapsVersion )

        hostPlatform   = Platforms.getHostPlatform()
        symlink_relSIT = RTMaps.getIndexFilePath_relSIT( canonicalPath,
                                                         rtmapsVersion,
                                                         hostPlatform )
        Any.requireIsTextNonEmpty( symlink_relSIT )

        symlinkPath    = os.path.join( sitProxyPath, symlink_relSIT )
        Any.requireIsTextNonEmpty( symlinkPath )

        FastScript.remove( symlinkPath, dryRun )
    else:
        logging.debug( 'skipped searching for RTMaps index symlink (RTMaps not sourced)' )


def randomizeValidityFlags():
    """
        Randomizes valid-/invalid-flags to be used as C-defines, e.g.:

        #define FOO_VALID    ( 0x998877 )
        #define FOO_INVALID  ( 0x112233 )

        Returns a tuple of two strings containing the hexvalues.
    """
    valid      = random.randint( 0x00000000, 0xFFFFFFFF )
    invalid    = random.randint( 0x00000000, 0xFFFFFFFF )

    if valid == invalid:
        valid, invalid = randomizeValidityFlags()


    # format int as hex-string with padding
    # (e.g. 0x00000000 so ten chars in total)
    #
    # {   # Format identifier
    # 0:  # first parameter
    # #   # use "0x" prefix
    # 0   # fill with zeroes
    # {1} # to a length of n characters (including 0x), defined by the second parameter
    # x   # hexadecimal number, using lowercase letters for a-f
    # }   # End of format identifier
    #
    validStr   = "{0:#0{1}x}UL".format( valid,   10 )
    invalidStr = "{0:#0{1}x}UL".format( invalid, 10 )

    Any.requireIsTextNonEmpty( validStr )
    Any.requireIsTextNonEmpty( invalidStr )

    return validStr, invalidStr


# EOF
