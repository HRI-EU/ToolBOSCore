##  Environment variables

![](BST-small.png)


 <table>
 <tr>
   <th>environment variable</th>
   <th>description</th>
 </tr>
 <tr>
   <td colspan="2" bgcolor="#CCCCFF"><b>User settings
       (e.g. in scripts or interactive shells)</b></td>
 </tr>
 <tr>
   <td>export BST_BUILD_JOBS=NUM</td>
   <td>number of parallel jobs, can also be specified using
       BST.py -j NUM</td>
 </tr>
 <tr>
   <td>export BST_CMAKE_OPTIONS="..."</td>
   <td>additional parameters to pass to CMake, e.g. --trace</td>
 </tr>
 <tr>
   <td>export BST_INSTALL_PREFIX=/path/to/SIT</td>
   <td>install package to different path (e.g. /tmp), mostly useful for
       testing external software</td>
 </tr>
 <tr>
   <td>export BST_SKIP_SCRIPTS=TRUE</td>
   <td>do not execute custom build scripts such as \c compile.sh (used to
       avoid recursion when called from within \c compile.sh)</td>
 </tr>
 <tr>
   <td>export BST_USE_ICECC=TRUE</td>
   <td>explicitly force usage of IceCC distributing compiler on Linux
       (TRUE or FALSE)</td>
 </tr>

 <tr>
   <td>export DRY_RUN=TRUE</td>
   <td>don't actually do anything (considered by install procedure and
       cleaning routine only)</td>
 </tr>
 <tr>
   <td>export MAKEFILE_DOC=FALSE</td>
   <td>skip documentation creation (doxygen/matdoc)</td>
 </tr>
 <tr>
   <td>export MAKEFILE_GLOBALINSTALLREASON="NEW: fixed XY"</td>
   <td>Non-Interactive global installation (e.g. for shell scripts)</td>
 </tr>
 <tr>
   <td>export MAKEFILE_GLOBALINSTALLUSER=username</td>
   <td>override auto-detected global install username, maybe useful if
       LDAP server is busy and not responsive</td>
 </tr>
 <tr>
   <td>export MAKEFILE_INSTALL_GROUPNAME=hriasc</td>
   <td>force groupname when installing packages</td>
 </tr>
 <tr>
   <td>export MAKEFILE_INSTALL_UMASK=0002</td>
   <td>force umask (file permissions) when installing packages</td>
 </tr>
 <tr>
   <td>export VERBOSE=TRUE</td>
   <td>show all compiler output and debug messages</td>
 </tr>
 <tr>
   <td colspan="2" bgcolor="#CCCCFF"><b>Variables to use in
       packageVar.cmake for platform-dependent settings</b></td>
 </tr>
 <tr>
   <td>COMPILER</td>
   <td>compiler dependent build settings (e.g. gcc/msvc)</td>
 </tr>
 <tr>
   <td>MAKEFILE_PLATFORM</td>
   <td>attempt to build for specified target platform, or check if current
       build is about this platform</td>
 </tr>
 <tr>
   <td>HOSTARCH / TARGETARCH</td>
   <td>CPU architecture dependent build settings (e.g. 32/64 bit)</td>
 </tr>
 <tr>
   <td>HOSTOS / TARGETOS</td>
   <td>O.S. dependent build settings (e.g. Linux/Windows/MacOS)</td>
 </tr>
 <tr>
   <td colspan="2" bgcolor="#CCCCFF"><b>Legacy
       variables</b></td>
 </tr>
 <tr>
   <td>MAKEFILE_CC</td>
   <td>use COMPILER instead</td>
 </tr>
 <tr>
   <td>MAKEFILE_CPU</td>
   <td>use TARGETARCH instead</td>
 </tr>
 <tr>
   <td>MAKEFILE_OS</td>
   <td>use TARGETOS instead</td>
 </tr>
 <tr>
   <td>MAKEFILE_SKIPSVNCHECK</td>
   <td>use [ToolBOS.conf](../../Concepts/ToolBOSConf.md)instead</td>
 </tr>

 </table>
