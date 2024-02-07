##  pkgInfo.py

A pkgInfo.py file might be present in a package, both in VCS and/or in the SIT.

* If such file exists within a source package (f.i. in VCS) it is used to
  configure the behavior of BST.py. Thus, it typically is handcrafted.

* Each package installed in the SIT should have a pkgInfo.py file containing
  meta-information, such as location of VCS repository or current maintainer.
  These information are used e.g. by the CIA (aka Nightly Build) system.
  Such files are typically auto-generated at install time.

> **Note:**
> A pkgInfo.py file may contain arbitrary Python code.
> If necessary you could even import packages to calculate some values.

###  Recognized keywords

The file is organized as key-value-pair assignments. However, you may use any
code to do such assignments. At loading time the Python code gets evaluated
and the following variables are searched:


<table>
<tr>
    <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
        colspan="3">package meta info</td>
</tr>
<tr>
    <td>name</td>
    <td>string</td>
    <td>name of the package</td>
</tr>
<tr>
    <td>version</td>
    <td>string</td>
    <td>version number of the package</td>
</tr>
<tr>
    <td>category</td>
    <td>string</td>
    <td>category of the package (eg.: Development tools,
        Application or External etc.)</td>
</tr>
<tr>
    <td>scripts</td>
    <td>dict { string: string }</td>
    <td>customize scripts invoked by BST.py, e.g.:
<pre>
scripts = { 'compile' : 'compile-all.sh',
            'unittest': 'scripts/myTest.sh' }
</pre>
</td>
</tr>
<tr>
    <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
        colspan="3">package interrelationship</td>
</tr>
<tr>
    <td>depends</td>
    <td>list of strings</td>
    <td>direct dependencies required by this package (for both building
        and execution), in canonical package notation</td>
</tr>
<tr>
    <td>dependsArch</td>
    <td>dict { string: list of strings }</td>
    <td>platform-specific dependencies can be stored in this dictionary
        e.g.:
<pre>
dependsArch = { 'focal64': [ 'deb://openjdk-11-jdk' ] }
</pre>
</td>
</tr>
<tr>
    <td>buildDepends</td>
    <td>list of strings</td>
    <td>direct dependencies required for building this package, in
        canonical package notation</td>
</tr>
<tr>
    <td>buildDependsArch</td>
    <td>dict { string: list of strings }</td>
    <td>platform-specific build-dependencies can be stored in this
        dictionary, e.g.:
<pre>
buildDependsArch = { 'focal64': [ 'deb://gcc-9.3' ] }
</pre>
</td>
</tr>
<tr>
    <td>recommended</td>
    <td>list of strings</td>
    <td>packages often found / used together with this one, without
        a hard dependency on it, in canonical package notation</td>
</tr>
<tr>
    <td>suggests</td>
    <td>list of strings</td>
    <td>packages which might be of interest to users of this one</td>
</tr>

<tr>
    <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
        colspan="3">compilation</td>
</tr>
<tr>
    <td>BST_useClang</td>
    <td>bool</td>
    <td>enable / disable the usage of Clang/LLVM for compiling C/C++ code</td>
</tr>

<tr>
    <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
        colspan="3">distclean</td>
</tr>
<tr>
    <td>delete</td>
    <td>list of strings</td>
    <td>additional file patterns to be deleted (apart from default patterns),
        see <a href="Cleaning.md">Cleaning</a></td>
</tr>
<tr>
    <td>doNotDelete</td>
    <td>list of strings</td>
    <td>file patterns from the default set of patterns which shall be kept
        see <a href="Cleaning.md">Cleaning</a></td>
</tr>
<tr>
    <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
        colspan="3">Software Quality settings</td>
</tr>
<tr>
    <td>sqLevel</td>
    <td>string</td>
    <td>targeted SQ level, see
        <a href="../../../../include/ToolBOSCore/SoftwareQuality/Common.py?plain=1#L51">Quality
        levels</a>, e.g.:
<pre>
sqLevel = 'advanced'
</pre>
</td>
</tr>
<tr>
    <td>sqOptInRules</td>
    <td>list of strings</td>
    <td>list of SQ rules to be explicitly enabled, e.g.:
<pre>
sqOptInRules = [ 'C15', 'C16' ]
</pre>
</td>
</tr>
<tr>
    <td>sqOptOutRules</td>
    <td>list of strings</td>
    <td>list of SQ to be explicitly disabled (please leave comment why), e.g.:
<pre>
sqOptOutRules = [ 'C04', 'C05' ]
</pre>
</td>
</tr>
<tr>
    <td>sqOptInDirs</td>
    <td>list of strings</td>
    <td>list of directories (relative paths) to be explicitly included
        in check, e.g.:
<pre>
sqOptInDirs = [ 'src' ]
</pre>
</td>
</tr>
<tr>
    <td>sqOptOutDirs</td>
    <td>list of strings</td>
    <td>list of directories (relative paths) to be explicitly excluded
        from check, e.g.:
<pre>
sqOptOutDirs = [ 'external', '3rdParty' ]
</pre>
</td>
</tr>
<tr>
    <td>sqOptInFiles</td>
    <td>list of strings</td>
    <td>list of files (relative paths) to be explicitly included
        in check, e.g.:
<pre>
sqOptInFiles = [ 'helper.cpp' ]
</pre>
</td>
</tr>
<tr>
    <td>sqOptOutFiles</td>
    <td>list of strings</td>
    <td>list of files (relative paths) to be explicitly excluded
        from check, e.g.:
<pre>
sqOptOutFiles = [ 'src/autoGeneratedWrapper.cpp' ]
</pre>
</td>
</tr>
<tr>
    <td>sqComments</td>
    <td>dict { string: list of strings }</td>
    <td>comments + annotations to SQ rules, e.g. why opt-in/out or
        justification why a rule cannot be fulfilled</td>
</tr>
<tr>
    <td>sqCheckExe</td>
    <td>list of strings</td>
    <td>paths to the executables, including arguments (if any), that
        shall be analyzed by the valgrind check routine</td>
</tr>
<tr>
    <td>pylintConf</td>
    <td>string</td>
    <td>path to the user pylint configuration file</td>
</tr>
<tr>
    <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
        colspan="3">documentation</td>
</tr>
<tr>
    <td>docFiles</td>
    <td>list of strings</td>
    <td>make SQ DOC01 search for specified documentation files, e.g.:
<pre>
docFiles = [ 'README.md',
             'doc/documentation.h',
             'doc/ReleaseNotes.txt' ]
</pre>
    </td>
</tr>
<tr>
    <td>docTool</td>
    <td>string</td>
    <td>force particular documentation tool ("doxygen", "matdoc"), or
         disable documentation creation using an empty string ("")</td>
</tr>
<tr>
    <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
        colspan="3">installation procedure</td>
</tr>
<tr>
    <td>install</td>
    <td>list of tuples</td>
    <td>additional files/directories to install,
         see <a href="Installation.md?plain=1#L29">Installation</a></td>
</tr>
<tr>
    <td>installMatching</td>
    <td>list of tuples</td>
    <td>additional files/directories to install,
         see <a href="Installation.md?plain=1#L65">Installation</a></td>
</tr>
<tr>
    <td>installSymlinks</td>
    <td>list of tuples</td>
    <td>symlinks to be created at install time,
         see <a href="Installation.md?plain=1#L82">Installation</a></td>
</tr>
<tr>
    <td>installMode</td>
    <td>string</td>
    <td>"incremental": add files to previous installation (= default),
         "clean": wipe previous installation before installing</td>
</tr>
<tr>
    <td>installExclude</td>
    <td>list of strings</td>
    <td>do not install files/directories whose relative paths start
        with given strings, e.g.:
<pre>
installExclude = [ 'bin/secret.py',
                   'etc/passwords',
                   'include/skipMe' ]
</pre>
</td>
</tr>
<tr>
    <td>installGroup</td>
    <td>string</td>
    <td>set group of installed files to specified group name, e.g.
         "users"</td>
</tr>
<tr>
    <td>installUmask</td>
    <td>integer</td>
    <td>override user's umask-setting when installing packages, can be
         specified as decimal integer, octal integer, or string), e.g.:
<pre>
installUmask = "0022"      # for permissions rwxr-xr-x
</pre>
</td>
</tr>
<tr>
    <td>usePatchlevels</td>
    <td>True or False</td>
    <td>use 3-digit version scheme for installation such as "1.0.123"</td>
</tr>
<tr>
    <td>patchlevel</td>
    <td>integer</td>
    <td>number to use for last field in 3-digit version scheme,
         e.g. 123 to yield full version string "1.0.123"</td>
</tr>
<tr>
    <td>linkAllLibraries</td>
    <td>bool</td>
    <td>flag if CreateLibIndex for RTBOS shall consider all.so files
         in the install directory, or only the main one named after the
         package</td>
</tr>
<tr>
    <td>Install_on{Startup,Exit}Stage{1..5}</td>
    <td>callable</td>
    <td>Python function to be executed at startup/exit of the
         corresponding stage 1..5</td>
</tr>
<tr>
    <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
        colspan="3">shellfiles customization</td>
</tr>
<tr>
    <td>envVars</td>
    <td>list of tuples</td>
    <td>environment variable assignments to put into auto-generated
         \c BashSrc and \c CmdSrc.bat files
         each tuple (of two elements) contains a varName-value assignment
         Note: this was not implemented as \c dict in order to preserve
         the list of appearance in the file</td>
</tr>
<tr>
    <td>aliases</td>
    <td>list of tuples</td>
    <td>command aliases to put into auto-generated
         \c BashSrc and \c CmdSrc.bat files
         each tuple (of two elements) contains an alias-command assignment
         Note: this was not implemented as \c dict in order to preserve
         the list of appearance in the file</td>
</tr>
<tr>
    <td>bashCode</td>
    <td>list of strings</td>
    <td>Bash code to be injected into auto-generated \c BashSrc files,
         line-wise</td>
</tr>
<tr>
    <td>cmdCode</td>
    <td>list of strings</td>
    <td>Windows \c cmd.exe code to be injected into auto-generated
         \c CmdSrc.bat files, line-wise</td>
</tr>
<tr>
    <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
        colspan="3">version control system</td>
</tr>
<tr>
    <td>gitBranch</td>
    <td>string</td>
    <td>Git branch name used for installation</td>
</tr>
<tr>
    <td>gitCommitID</td>
    <td>string</td>
    <td>Git commit ID</td>
</tr>
<tr>
    <td>gitOrigin</td>
    <td>string</td>
    <td>URL of Git blessed repository</td>
</tr>
<tr>
    <td>gitRepoRelPath</td>
    <td>string</td>
    <td>path of the files relative within the Git repository root</td>
</tr>
<tr>
    <td>revision</td>
    <td>string</td>
    <td>SVN revision number</td>
</tr>
<tr>
    <td>revisionforCIA</td>
    <td>string</td>
    <td>SVN revision which shall be build by CIA</td>
</tr>
<tr>
    <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
        colspan="3">legacy settings</td>
</tr>
<tr>
    <td>package</td>
    <td>string</td>
    <td>name of the package (replaced by "name")</td>
</tr>
</table>


## Example

```
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


name             = 'Foo'

version          = '1.0'

category         = 'Applications'

sqLevel          = 'advanced'

linkAllLibraries = True

envVars          = [ ( 'PATH', '${INSTALL_ROOT}/bin/${MAKEFILE_PLATFORM}:${PATH}' ),
                     ( 'LD_LIBRARY_PATH', '${INSTALL_ROOT}/lib/${MAKEFILE_PLATFORM}:${LD_LIBRARY_PATH}' ) ]

bashCode         = [ 'echo "Hello, World!"' ]

usePatchlevels   = True

import numpy
patchlevel       = int( numpy.pi )               # just for demonstration purposes ;-)


# EOF
```
