##  Installation

![](BST-small.png)


### Usage

The build system distinguishes between installing into a proxy and into the main SIT. 
It also supports creating a tarball only (no installation).

**See also**
* [Software Installation Tree (SIT)](../../Concepts/SIT.md) 
* [Proxy Directory](../../Concepts/ProxyDirectory.md)


| command   | description
|-----------|------------------
| BST.py -x | installing into the user's SIT sandbox ("proxy directory") without altering the global installation, should be used while testing/debugging
| BST.py -i | installing into the global SIT (official release) SIT
| BST.py -r | create a tarball only (no installation)
| BST.py -U | uninstall, see Uninstalling


###  Install custom files/directories

If you need to install more files than would automatically be detected, you can specify them in the pkgInfo.py file.


####  Install files/directories [recursively]

This recursively installs the 3 directories "external, "etc" and "include" from your source tree into the
installation tree of your package.

    # -*- coding: utf-8 -*-
    #
    #  Custom package settings
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
    install          = [ 'external',
                         'etc',
                         'include' ]
    # EOF
    
    
#####  Install files/directories [recursively], with different destination

If the destination shall be different, turn such a string-element into a tuple of (source dir.,destination dir.).

Same as above, except that 'external' will get installed as '3rdParty':

    install          = [ ( 'external', '3rdParty' ),           # tuple of (src,dst)
                         'etc',                                # src == dst
                         'include' ]                           # src == dst
                         

####  Install files/directories matching regular expression

To install only those files matching a certain regexp, use the copyMatching() function instead. Each element in the
list must be a tuple of (source dir.,regular expression).

This installs all Java examples:

    installMatching  = [ ( 'examples', '\.java' ) ]            # (srcDir,regexp)
    
    
#### Install files/directories matching regular expression, with different destination
     
Tuples might contain three elements in case the destination directory shall be different.
If Java examples were to be installed into a destination directory 'HowTo' instead, the code would look like:

    installMatching  = [ ( 'examples', '\.java', 'HowTo' ) ]   # (srcDir,regexp,dstDir)
    
#### Installing symlinks
     
To create a symlink during installation, put the following list of tuples in your pkgInfo.py.
Each tuple contains two elements (target, symlink).

    installSymlinks  = [ ( 'windows-amd64-vs2020',             # target
                           'windows-amd64-vs2017' ) ]          # symlink

This creates a symlink within the installation directory. The symlink is named "windows-amd64-vs2017" (2nd element) 
pointing to "windows-amd64-vs2020" (1st element).

Both elements may contain subdirectory pathnames.


####  Setting ownership of files
      
You can specify a particular group to whom the installed files shall belong:

    installGroup     = 'users'                                 # group name
    
and also the umask-settings (permission modes), e.g.:

    installUmask     = '0002'                                  # group-writeable, world-readable
    

###  Toggle incremental / clean-install mode
     
BST.py defaults to performing incremental installations, this means existing files won't be deleted prior to installing
the new files. This allows sequential installation for multiple platforms.
     
The drawback is that files that in the meanwhile have been deleted from the codebase, persist in the installation 
and eventually disturb.

Please select an appropriate way and put either of the following settings in your pkgInfo.py.

####  Solution A: use patchlevel-installations (3-digit versions)

       usePatchlevels   = True
    
       patchlevel       = 123                                     # default: SVN revision
    
####  Solution B: clean existing installation

    installMode      = 'clean'                                 # default: 'incremental'
    
    
###  For the experts: Install hooks (Python)

You may implement any of the following Python functions in your pkgInfo.py in order to manually extend the installation procedure.
     
* Install_onStartupStage1
* Install_onExitStage1
* Install_onStartupStage2
* Install_onExitStage2
* Install_onStartupStage3
* Install_onExitStage3
* Install_onStartupStage4
* Install_onExitStage4
* Install_onStartupStage5
* Install_onExitStage5


    from ToolBOSCore.Util import FastScript
    def Install_onStartupStage2( self ):
        """
            Custom extension of install procedure.
        """
        logging.info( "Hello, World!" )
        logging.info( "packageName=%s", self.details.packageName )
        FastScript.execProgram( "myHelperProgram" )
        
This hook function will be executed by the installation procedure at the beginning of stage 2, f.i.:

       [...]
       STAGE 2 # AUTO-GENERATING FILES
    
       [<string>:126 INFO] Hello, World!
       [<string>:127 INFO] packageName=MyPackage
       [...output of myHelperProgram...]
       [PackageCreator.py:966 INFO] cp BashSrc ./install/
       [PackageCreator.py:978 INFO] cp CmdSrc.bat ./install/
       [...]
       
#### For the experts: Install hooks (Bash)

As alternative to implementing Pythonic install hooks (see above) you can write small shellscripts that will be executed 
during the install procedure. They have to be located in the top-level directory of your package and must be named:

**most relevant:**

* preInstallHook.sh (executed just before copying)
* installHook.sh (this is the file you most probably look for)
* postInstallHook.sh (executed after copying all files)

for special cases, symmetric to the Python functions above:

*  Install_onStartupStage1.sh
*  Install_onExitStage1.sh
*  Install_onStartupStage2.sh
*  Install_onExitStage2.sh
*  Install_onStartupStage3.sh
*  Install_onExitStage3.sh
*  Install_onStartupStage4.sh
*  Install_onExitStage4.sh
*  Install_onStartupStage5.sh
*  Install_onExitStage5.sh

Most common use case is to call the install routine of a 3rd party software from our install procedure. To achieve this
you would create a shellscript installHook.sh looking similar to this:

    #!/bin/bash
    #
    #  additional steps for the installation procedure
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
    
    
    cd build/${MAKEFILE_PLATFORM}
    make install
    
    
    # EOF
