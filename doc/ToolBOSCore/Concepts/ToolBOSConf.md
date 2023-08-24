## ToolBOS.conf


If ToolBOS does not detect desired values, you may override or customize certain settings via configfiles.  
They are Python files typically with simple key-value pair assignments only but might contain script logic as well.  
The content is being evaluated when loading such files.  

If a setting is not found in the current ToolBOS.conf file, it will look-up the lower priority paths/files until it was 
found otherwise fallback to the default value shipped with the ToolBOS SDK itself.


**The paths/files are searched in the following order:**

* ./ToolBOS.conf (current working directory)
* entries from additional search-paths if provided
* ${HOME}/.HRI/ToolBOS/ToolBOS.conf (user-settings)
* /etc/ToolBOS.conf (machine-wide settings by sysadmin)
* ${TOOLBOSCORE_ROOT}/etc/ToolBOS.conf (fallback / defaults)

### Example

In order to tell the SVNCheckout.py script to always use a different username when connecting to the SVN server 'svnext',
create a file ${HOME}/.HRI/ToolBOS/ToolBOS.conf with the following content:

    serverAccounts = { 'svnext': 'marijke' }
    
 
### Commandline usage
 
You may configure your settings using ToolBOS-Config.py:

    $ ToolBOS-Config.py                                 # list all settings
    
    $ ToolBOS-Config.py -p hostPlatform                 # print host platform
    
    $ ToolBOS-Config.py -s "foo=bar"                    # add custom setting
    
    
### List of possible settings

| key 	                   | description|
|:------                   |:-----------|
| askGlobalInstallReason   | enable / disable the need to provide global install-reason (log message, default: True)  |
| BST_compileHosts 	       | BST.py: mapping of platform names to names of native compile hosts in this network |
| BST_confirmInstall 	   | interactively confirm global installation? (default: False)
| BST_crossCompileBSPs 	   | BST.py: mapping of platform names to the canonical path of the extension package necessary to source prior to cross-compiling
| BST_crossCompileHosts    | BST.py: mapping of platform names to names of cross-compile hosts in this network 
| BST_modulePath 	       | location of BuildSystemTools.cmake
| BST_svnCheck 	           | perform SVN consistency check at global installation (default: True)
| BST_useClang 	           | enable / disable the usage of Clang/LLVM for compiling C/C++ code (default: False)
| BST_useDoxypy            | enable / disable the usage of Doxypy when creating doxygen-documentation for Python code (default: True)
| bugtrackURL 	           | location of the issue tracker system, e.g. JIRA (http://hostname/path)
| CIA_account 	           | CIA buildbot account name
| CIA_startKey 	           | path to the SSH keyfile which shall be used for connecting to the Nightly Build servers in order to trigger the build
| CIA_checkoutKey 	       | path to the SSH keyfile which shall be used by the Nightly Build process for connecting to the SVN server (read only access to SVN repositories)
| CIA_commitKey 	       | path to the SSH keyfile which shall be used by the Nightly Build process for connecting to the SVN server (read/write access to SVN repositories)
| CIA_compileHosts 	       | dict containing a mapping of platform names to the compile hosts to use
| CIA_targetPlatforms 	   | set of platforms CIA shall compile for 
| clang_lib 	           | dict containing a mapping of platform names to the path to libclang.so, used by the SQ checkers
| defaultPlatform 	       | mainstream platform used by the majority of users
| defaultSVNServer 	       | server where to create new SVN repositories by default
| defaultSVNRepositoryPath | path to repository root on 'defaultSVNServer' (root path where all the SVN repositories are located), e.g. /data/subversion/HRIREPOS
| documentationServer 	   | URL to documentation server (https://...) 
| documentationURL 	       | location of the doxygen documentation of ToolBOSCore itself
| documentationURL_sit 	   | location of the SIT on the documentation server (http://.../sit/latest/)
| documentationURL_dir 	   | location of the doxygen documentation of ToolBOSCore itself (http://.../doc/html/)
| documentationURL 	       | URL to the doxygen documentation of ToolBOSCore itself (composed of documentationURL_dir + 'index.html'
| Git_allowedHosts 	       | whitelist of hosts allowed to clone from during Nightly Build, aka servers considered to contain the official versions
| hostArch 	               | value of MAKEFILE_CPU to use inside Python scripts 
| hostOS 	               | value of MAKEFILE_OS to use inside Python scripts
| hostPlatform 	           | value of MAKEFILE_PLATFORM to use inside Python scripts
| installGroup 	           | set group of installed files to specified group name
| installUmask 	           | override user's umask-setting when installing packages (can be specified as decimal integer, octal integer, or string)
| kwLicenseServerHost 	   | Klocwork license server hostname (e.g. "hri-licenses")
| kwLicenseServerPort 	   | Klocwork license server port (integer)
| package_clion 	       | canonical path of CLion SIT package (e.g. "External/CLion/1.0")
| package_klocwork 	       | canonical path of Klocwork SIT package (e.g. "External/klocwork/10.2") 
| package_libxml 	       | canonical path of libxml SIT package (e.g. "External/libxml2/2.6")
| package_matlab 	       | canonical path of Matlab package (e.g. "External/Matlab/8.4")
| package_nanomsg 	       | canonical path of the NanoMsg library to use (e.g. "External/nanomsg/1.0")
| package_pycharm 	       | canonical path of PyCharm SIT package (e.g. "External/PyCharmPro/4.5")
| package_rtmaps           | canonical path of RTMaps SIT package (e.g. "External/RTMaps/4.7")
| serverAccounts 	       | username to use for SSH when connecting to certain hosts (a Python dictionary mapping hostname => username)
| SVN_allowedHosts 	       | whitelist of hosts allowed to checkout from during Nightly Build, aka servers considered to contain the official versions 
| sonarToken               | SonarQube user auth token for static code analysis