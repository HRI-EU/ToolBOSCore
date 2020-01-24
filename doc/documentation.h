/*
 *  main documentation
 *
 *  Copyright (c) Honda Research Institute Europe GmbH
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions are
 *  met:
 *
 *  1. Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *
 *  2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *  3. Neither the name of the copyright holder nor the names of its
 *     contributors may be used to endorse or promote products derived from
 *     this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 *  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 *  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 *  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 *  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 *  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 *  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 *  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 *  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 *  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 *  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */


/*!
 * \mainpage

  <table border="0" width="100%">
    <tr>
        <td colspan="4" style="background: #1498d5; color: white; padding-left: 1em;">
            <h2>About</h2>
        </td>
    </tr>

    <tr>
        <td colspan="2" style="border: none; padding: 1em;">
            The <span style="color: #3d578c; font-weight: bold;">ToolBOS Core
            package</span> contains:
            <ul>
            <li>multi-platform build system based upon CMake (CLI + GUI)</li>
            <li>package templates / skeletons</li>
            <li>Software Installation Tree (SIT) management tools</li>
            <li>helpers for VCS access</li>
            <li>tools for distributing and deploying SIT-packages</li>
            <li>software quality guidelines and check routines</li>
            </ul>
        </td>

        <td colspan="2" align="center">
            <img src="../Logos/ToolBOS-Logo.png">
        </td>
    </tr>

    <tr>
        <td colspan="4" style="background: #1498d5; color: white; padding-left: 1em;">
            <h2>Documentation</h2>
        </td>
    </tr>

    <tr>
        <td width="25%" valign="top" style="border: none; padding: 1em;">
            <h2>Setup</h2>
            <ul>
            <li><a href="ToolBOS_Setup_Admin.html">Installing ToolBOS on disk</a></li>
            <li><a href="ToolBOS_Setup_User.html">Shell configuration</a></li>
            <li><a href="ToolBOS_Setup_AddOns.html">Sourcing additional packages</a></li>
            <li><a href="ToolBOS_Setup_Platforms.html">Supported platforms</a></li>
            </ul>
        </td>

        <td width="25%" valign="top" style="border: none; padding: 1em;">
            <h2>Concepts</h2>
            <ul>
            <li><a href="ToolBOS_Concept_SIT.html">Software Installation Tree (SIT)</a></li>
            <li><a href="ToolBOS_Concept_ProxyDir.html">Proxy Directory</a></li>
            <li><a href="ToolBOS_Concept_SoftwareQuality.html">Quality Guideline</a></li>
            <li><a href="ToolBOS_Concept_SourceTreeConventions.html">Source tree conventions</a></li>
            <li><a href="ToolBOS_Concept_InstallationConventions.html">Installation conventions</a></li>
            <li><a href="ToolBOS_Concept_ToolBOSconf.html">ToolBOS.conf</a></li>
            <li><a href="ToolBOS_HowTo_SITSwitch.html">SIT builds</a></li>
            </ul>
        </td>

        <td width="25%" valign="top" style="border: none; padding: 1em;">
            <h2>Tools</h2>
            <ul>
            <li><a href="ToolBOS_Util_PackageCreator.html">Package Creator</a></li>
            <li><a href="ToolBOS_Util_BuildSystemTools.html">Build System Tools</a></li>
            <li><a href="ToolBOS_UseCases_ExecInAllProjects.html">ExecInAllProjects.py</a></li>
            </ul>
        </td>

        <td width="25%" valign="top" style="border: none; padding: 1em;">
            <h2>HowTo's</h2>
            <ul>
            <li><a href="ToolBOS_HowTo_Debugging.html">Debugging</a></li>
            <li><a href="ToolBOS_HowTo_Libraries.html">Writing C/C++ libraries</a></li>
            <li><a href="ToolBOS_HowTo_External_Packages.html">External packages</a></li>
            <li><a href="ToolBOS_HowTo_UserDoxyfile.html">userDoxyfile</a></li>
            <li><a href="ToolBOS_HowTo_ParticularRelease.html">ToolBOS beta-test</a></li>
            <li><a href="ToolBOS_HowTo_Deprecated.html">Deprecated packages</a></li>
            </ul>
        </td>
    </tr>
   </table>
 * \endhtmlonly
 */


/*!
 * \page ToolBOS_Setup_Platforms Supported platforms
 *
 * <table>
 * <tr>
 *   <th>Target</th>
 *   <th>Architecture</th>
 *   <th>Platform identifier</th>
 * </tr>
 * <tr>
 *   <td>Ubuntu Linux 14.04 LTS ("Trusty Tahr")</td>
 *   <td>amd64 (64 bit)</td>
 *   <td><tt>trusty64</tt></td>
 * </tr>
 * <tr>
 *   <td>Ubuntu Linux 18.04 LTS ("Bionic Beaver")</td>
 *   <td>amd64 (64 bit)</td>
 *   <td><tt>bionic64</tt></td>
 * </tr>
 * <tr>
 *   <th colspan="4"> </th>
 * </tr>
 * <tr>
 *   <td>Microsoft Windows 7</td>
 *   <td>amd64 (64 bit)</td>
 *   <td><tt>windows-amd64-vs2017</tt></td>
 * </tr>
 * <tr>
 *   <th colspan="4"> </th>
 * </tr>
 * <tr>
 *   <td><a href="http://www.phytec.de/produkt/single-board-computer/phyboard-wega/">phyBOARD-WEGA</a></td>
 *   <td>ARMv8 (32 bit)</td>
 *   <td><tt>phyboardwega</tt></td>
 * </tr>
 * <tr>
 *   <td><a href="http://www.peak-system.com/PCAN-Router.228.0.html">PCAN-Router</a>
 *      (bare-metal)</td>
 *   <td>ARMv7 (32 bit)</td>
 *   <td><tt>peakcan</tt></td>
 * </tr>
 * </table>
 */


/*!
 * \page ToolBOS_Setup Setup
 *
 * \image html ToolBOS-Logo.png
 *
 * \li \subpage ToolBOS_Setup_Admin
 * \li \subpage ToolBOS_Setup_User
 * \li \subpage ToolBOS_Setup_AddOns
 * \li \subpage ToolBOS_Setup_Platforms
 */


/*! \page ToolBOS_Setup_Admin Installing ToolBOS on disk
 *
 * \note For sites running multiple ToolBOS machines it is common to put the
 *       data on a network share and mount the content appropriately on
 *       clients, rather than copying to each local disk individually.
 *
 * <hr>
 * <h2>Linux</h2>
 *
 * \li Create the following directory:
 *
 * \verbatim
   $ mkdir -p /hri/sit
   \endverbatim
 *
 * \li Copy the Software Installation Tree (SIT) that you have received
 * into the \c /hri/sit directory. Example:
 *
 * \verbatim
   $ cp -R /media/dvd/* /hri/sit
   \endverbatim
 *
 * \li Now the following directories should exist:
 *
 * \li \c /hri/sit/builds
 * \li \c /hri/sit/LTS
 * \li \c /hri/sit/latest (symlink to \c builds/latest)
 *
 * <hr>
 * <h2>Windows</h2>
 *
 * \li Copy the Software Installation Tree (SIT) that you have received
 * to some local directory (e.g. c:\\SIT)
 *
 * \li Map the drive letter \c S: to this directory. Open a terminal using
 * "Start → Run → cmd.exe" and enter the following command (replace
 * c:\\SIT accordingly).
 *
 * \verbatim
   subst s: c:\SIT
   \endverbatim
 *
 * \image html Windows-DriveLetterToPath.png
 *
 * \li Now you should be able to browse the new "drive" \c s: within Windows
 * explorer:
 *
 * \image html Windows-BrowseSIT.png
 *
 *
 * \page ToolBOS_Setup_User Shell configuration
 *
 * <h2>Linux</h2>
 *
 * ToolBOS needs some environment variables and files present in your
 * home directory.
 *
 * Please execute the following commands and follow their instructions:
 *
 * \code
   $ source /hri/sit/latest/DevelopmentTools/ToolBOSCore/3.3/BashSrc

   $ /hri/sit/latest/DevelopmentTools/ToolBOSCore/3.3/bin/ToolBOS-Setup.py
   \endcode
 *
 * As mentioned by the script, please add a line like this to your
 * ~/.bashrc, and then logout and login again.
 *
 * \code
   source /hri/sit/latest/DevelopmentTools/ToolBOSCore/3.3/BashSrc
   \endcode
 *
 * <hr>
 * <h2>Windows</h2>
 *
 * ToolBOS needs some environment variables which can be brought up with this
 * script:
 *
 * \verbatim
   S:\DevelopmentTools\ToolBOSCore\3.3\CmdSrc.bat
   \endverbatim
 *
 * \image html BuildSystemTools/WindowsSetEnv.png
 *
 *
 * \page ToolBOS_Setup_AddOns Sourcing additional packages
 *
 * To always have additional packages sourced, please do so directly in
 * your ~/.bashrc (after the sourcing of ToolBOSCore/3.3/BashSrc).
 *
 * \note At this point you may make use of ${SIT}.
 *
 * \verbatim
   # mandatory:
   source /hri/sit/latest/DevelopmentTools/ToolBOSCore/3.3/BashSrc

   # optional:
   source ${SIT}/Applications/ABC/1.0/BashSrc
   source ${SIT}/Libraries/Foo/42.0/BashSrc
   \endverbatim
 *
 * <hr>
 * <h2>Windows</h2>
 *
 * Create a custom batch script, e.g. C:\\CmdSrc.bat, to load additional
 * packages:
 *
 * \verbatim
   call ${SIT}/Applications/ABC/1.0/CmdSrc.bat
   call ${SIT}/Libraries/Foo/42.0/CmdSrc.bat
   \endverbatim
 *
 * Then invoke it on your Windows console:
 *
 * \verbatim
   c:\CmdSrc.bat
   \endverbatim
 */


/*!
 * \page ToolBOS_Concept Concepts
 *
 * \image html ToolBOS-Logo.png
 *
 * \li \subpage ToolBOS_Concept_SIT
 * \li \subpage ToolBOS_Concept_ProxyDir
 * \li \subpage ToolBOS_Concept_SoftwareQuality
 * \li \subpage ToolBOS_Concept_SourceTreeConventions
 * \li \subpage ToolBOS_Concept_InstallationConventions
 * \li \subpage ToolBOS_Concept_ToolBOSconf
 */


/*!
 * \page ToolBOS_Concept_SIT Software Installation Tree (SIT)
 *
 * <h2>Overview</h2>
 *
 * The idea of a centrally shared "Software Installation Tree" arose from
 * the problems of different software versions installed on several
 * machines.
 * Therefore we have established an NFS share containing all software.
 * This NFS share is mounted on all computers so that everybody uses the
 * same software state.
 *
 * \attention A basic principle is to NEVER hardcode the path anywhere
 *            in the software but always refer to the environment variable
 *            ${SIT} which is supposed to point to the root
 *            path which contains all the software. At HRI-EU the default
 *            SIT root path is \c /hri/sit/latest but you should never
 *            rely on this path as it changes from time to time.
 *
 * <h2>Directory structure</h2>
 *
 * <center>
 * \image html Concepts/SIT-Structure.png
 * <i>SIT directory structure as of December 2014</i>
 * </center>
 *
 * For human readability the directory tree is organized in categories,
 * e.g.:
 *
 * \li Applications (big standalone packages)
 * \li DeviceIO (drivers etc.)
 * \li Libraries (shared functionalities)
 * \li Modules (components to be used in larger frameworks)
 * \li External (3rd party software)
 *
 * \see \ref ToolBOS_Concept_ProxyDir
 * \see \ref ToolBOS_Concept_InstallationConventions
 *
 * <h2>Advanced: Bootstrapping a new SIT</h2>
 *
 * A brand-new SIT can be created using \c BootstrapSIT.py. This might be
 * useful when distributing software to partners. See also:
 *
 * \code
   $ BootstrapSIT.py --help
   \endcode
 */


/*!
 * \page ToolBOS_Concept_ProxyDir Proxy Directory
 *
 * A <b>proxy directory</b> is a sandbox for testing software.
 *
 * <h2>Key concepts</h2>
 * \li directory tree with same structure like the main \ref ToolBOS_Concept_SIT
 * \li used to test software (prior to release)
 * \li every user has such proxy directory which shadows/masks the content of
 *     the global SIT
 * \li referenced via environment variable \c SIT
 * \li at the beginning the proxy directory contains symlinks into global SIT
 * \li when installing software into the proxy directory such symlinks will
 *     be replaced by actual directories with real content
 * \li users can test changes of their software without affecting anybody else
 *
 * <h2>Creation</h2>
 *
 * Under Linux you typically don't need to create a new proxy directory as it
 * was already done by \c ToolBOS-Setup.py. This creates a proxy directory
 * located in \c ${HOME}/.HRI/sit/latest .
 *
 * \code
   $ CreateProxyDir.py
   \endcode
 *
 * Initially all "versions" inside the proxy directory are symlinks:
 *
 * \image html ProxyDirectory.png
 *
 * <h2>Installing into proxy directory</h2>
 *
 * To install a software package into a proxy directory, use:
 * \code
   $ BST.py -x
   \endcode
 *
 * Then you will find a corresponding directory with the package content
 * inside your proxy directory:
 *
 * \image html ProxyDirectory-afterProxyInstall.png
 *
 * <h2>Updating</h2>
 *
 * You need to update the proxy directory once in a while. This will add
 * symlinks to packages newly installed into the global SIT:
 *
 * \code
   $ UpdateProxyDir.py
   \endcode
 *
 * <h2>FAQ</h2>
 *
 * <h3>How can I find out which packages are currently installed in my proxy
 *     directory?</h3>
 *
 * \c FindProxyInstallations.py scans the proxy directory for installations.
 * It lists one software package per line. If you do not have any proxy
 * installations then this script will output nothing.
 *
 * \code
   $ FindProxyInstallations.py
   \endcode
 *
 * <h3>How can I remove a package from the proxy directory?</h3>
 *
 * There are 3 possibilities:
 *
 * \li Just delete the directory. If a global installation of the package
 *     exists you may run \c UpdateProxyDir.py to create again the symlink to
 *     the global installation.
 * \li Perform a global installation of the package. This will automatically
 *     delete any existing proxy installation of the package and create a
 *     symlink in the proxy pointing to the new global installation.
 * \li Delete ALL proxy installations using "UpdateProxyDir.py -r"
 *     (see question below).
 *
 * <h3>I have a bunch of packages installed in my proxy. Can I reset the proxy
 *     directory in one shot back to a clean state?</h3>
 *
 * Sure. \c UpdateProxyDir.py provides an "-r" option for such purposes:
 * \code
   $ UpdateProxyDir.py -r
   \endcode
 *
 * <h3>Do proxy directories work on Windows?</h3>
 *
 * This is theoretically possible but not implemented, yet. In case please
 * raise a feature request but be aware of:
 *
 * From Wikipedia: "The default security settings in Windows Vista/Windows 7
 * disallow non-elevated administrators and all non-administrators from
 * creating symbolic links."
 *
 * Hence regular users could not run \c UpdateProxyDir.py unless corresponding
 * privileges are granted by the administrator.
 *
 * \see http://en.wikipedia.org/wiki/NTFS_symbolic_link
 */


/*!
 * \page ToolBOS_Concept_InstallationConventions Installation conventions
 *
 * The path to a package within the SIT has the following structure:
 * \code
 * ${SIT}/<Category>/<PackageName>/<PackageVersion>
\endcode
 * for example:
 * \code
 * ${SIT}/DevelopmentTools/ToolBOSCore/3.3
\endcode
 *
 * A package name must start with an alphabetic character (A-Z, a-z).
 * The name must only contain alpha-numeric characters (A-Z, a-z, 0-9) and
 * dashes (-). Please give descriptive names so that someone who doesn't
 * know particular abbreviations could anyway guess what the package is
 * roughly about.
 *
 * Version-numbers have the general format
 * &lt;Major&gt;.&lt;Minor&gt;[.&lt;Patchlevel&gt;][-&lt;ExtraTag&gt;],
 * e.g.:
 * \code
 * 1.0
 * 3.3.12
 * 2012.0
 * 42.0.1337-rc1
\endcode
 *
 * \li see http://www.semver.org for the semantic meaning of
 *     major/minor/patchlevel
 * \li &lt;Major&gt;, &lt;Minor&gt; and &lt;Patchlevel&gt; must contain
 *     digits only.
 * \li &lt;ExtraTag&gt; is an optional extension separated by a dash ("-")
 *     which can contain any printable charcter.
 * \li It is forbidden to use symlinks like \c default, \c testing or
 *     \c stable pointing to a particular version as this creates troubles
 *     during upgrade phases in which some people use the "old" stable and
 *     some others already use the "new" stable version.
 * \li It is useful to install packages in 3-digit-form (\c 1.0.0 ) and
 *     provide a symlink \c 1.0 which points to this. In that way you can
 *     easily install other patchlevel versions and perform rollbacks in
 *     case of errors (by just changing the symlink to a previous release).
 * \li When using patchlevels, other packages which depend on this must
 *     refer to the two-digit symlink only.
 *
 * Please stick to those directory names for the mentioned content:
 * <table>
 * <tr>
 *   <th>directory name</th>
 *   <th>typically expected content</th>
 * </tr>
 *
 * <tr>
 *   <td>bin</td>
 *   <td>scripts and platform-independent executables such as Java
 *       bytecode</td>
 * </tr>
 *
 * <tr>
 *   <td>bin/&lt;platform&gt;</td>
 *   <td>platform-specific binaries such as Linux ELF and/or Windows
 *       executables</td>
 * </tr>
 *
 * <tr>
 *   <td>doc</td>
 *   <td>documentation
 *       <ul>
 *         <li>put \c *.pdf files directly inside the \c doc directory</li>
 *         <li>put doxygen/pydoc/matdoc docu inside an \c html
 *             subdirectory</li>
 *       </ul>
 *       If an \c html subdirectory exists, the entry page should be called
 *       \c index.html .</td>
 * </tr>
 *
 * <tr>
 *   <td>data</td>
 *   <td>bigger amounts of resource files needed by the application,
 *       such as images (icons) or file-oriented database files</td>
 * </tr>
 *
 * <tr>
 *   <td>etc</td>
 *   <td>configfiles and settings</td>
 * </tr>
 *
 * <tr>
 *   <td>examples</td>
 *   <td>tutorial material explaining the usage of the software</td>
 * </tr>
 *
 * <tr>
 *   <td>external</td>
 *   <td>3rd party content that can/should not be separately installed into
 *       SIT (${SIT}/External)</td>
 * </tr>
 *
 * <tr>
 *   <td>include</td>
 *   <td>headerfiles (\c *.h ) or Python files (\c *.py )</tr>
 * </tr>
 *
 * <tr>
 *   <td>lib</td>
 *   <td>platform-independent binaries such as Java \c *.jar files</td>
 * </tr>
 *
 * <tr>
 *   <td>lib/&lt;platform&gt;</td>
 *   <td>platform-specific libraries such as static libraries, shared
 *       objects and/or Windows DLL files</td>
 * </tr>
 * </table>
 *
 * \note For C/C++ libraries, the main header file should match the name of
 *       the package, e.g. \c ToolBOSCore.h for the ToolBOSCore package.
 *
 * \note C/C++ library packages may only provide static OR shared libraries.
 *       However, providing both is recommended for flexibility reasons.
 *
 * \note Python modules should best be grouped under
 *       \c include/&lt;PackageName&gt;
 *
 * \note If necessary the \c &lt;platform&gt; directory and the
 *       subdirectories can be reversed (\c &lt;platform&gt;lib/), but
 *       please try to avoid for consistency reasons.
 *
 * <h3>Example:</h3>
 *
\verbatim
Project
 |
 `--1.0
     |--bin
     |   |--MyScript.py
     |   |--<platform_A>
     |   |   |--myFirstExecutable
     |   |   `--mySecondExecutable
     |   |--<platform_B>
     |   |   |--myFirstExecutable
     |   |   `--mySecondExecutable
     |   `--<platform_C>
     |       |--myFirstExecutable.exe
     |       `--mySecondExecutable.exe
     |
     |--doc
     |   |--HowTo.pdf
     |   |--DesignSpecification.pdf
     |   `--html
     |       |--image.png
     |       `--index.html
     |
     |--etc
     |   `--config.xml
     |
     |--external
     |   |--cmake.org
     |   |  `--[3rd party content]
     |   |
     |   |--gnome.org
     |   |  `--[3rd party content]
     |   |
     |   |--mathworks.com
     |   |  `--[3rd party content]
     |   |
     |   `--subversion.apache.org
     |      `--[3rd party content]
     |
     |--include
     |   |--Project                   # Python modules
     |   |  `-- __init__.py
     |   |
     |   |--Project.py                # standalone Python scripts
     |   |
     |   |--Project.h
     |   |--<platform_A>              # if headerfiles differ for several platforms
     |   |  `-- ProjectArchDep.h      # they can be put into platform-subdirectories
     |   |--<platform_B>
     |   |  `-- ProjectArchDep.h
     |   `--<platform_C>
     |      `-- ProjectArchDep.h
     |
     |--lib
     |   |--<platform_A>
     |   |   |--libProject.a  -->  libProject.a.1.0
     |   |   |--libProject.a.1.0
     |   |   |--libProject.so  -->  libProject.so.1.0
     |   |   `--libProject.so.1.0
     |   |--<platform_B>
     |   |   |--libProject.a  -->  libProject.a.1.0
     |   |   |--libProject.a.1.0
     |   |   |--libProject.so  -->  libProject.so.1.0
     |   |   `--libProject.so.1.0
     |   `--<platform_C>
     |       |--libProject.1.0.a
     |       |--libProject.1.0.dll
     |       |--libProject.1.0.dll.manifest
     |       |--libProject.1.0.static.a
     |       |--libProject.dll  -->  libProject.1.0.dll
     |       `--libProject.static.a  -->  libProject.1.0.static.a
     |
     |-- BashSrc
     `-- pkgInfo.py
\endverbatim
 *
 * \see \ref ToolBOS_Concept_SourceTreeConventions
 * \see \ref ToolBOS_Concept_SIT
 */


/*!
 * \page ToolBOS_Concept_SoftwareQuality Quality Guideline
 *
 * <img src="../Logos/QualityGuideline.png" align="right">
 *
 * \li List of coding conventions, with explaination and weblinks.
 * \li Guideline for project board to define quality requirements.
 * \li Check functions for measurement and validation.
 *
 * <h2>Defining quality requirements</h2>
 *
 * \htmlonly
 * <table border="0" width="100%">
 * <tr>
 *      <th width="50%" style="background: #3d578c; color: white;">online</th>
 *      <th width="50%" style="background: #3d578c; color: white;">desktop utility</th>
 * </tr>
 * <tr>
 *      <td style="border-style: solid; border-width: 1px; border-color: #ced6e9;
 *                 vertical-align: top;">
 *      <center>
 *          <img src="../HowTo/SQ-Webpage-small.png"
 *               width="361" height="232"
 *               alt="Screenshot: SQ requirement definition on webpage"/>
 *      </center>
 *
 *      <ol>
 *          <li>Open <a href="https://doc.honda-ri.de/hri/sit/latest/Intranet/TopicPortal/3.0/web/QualityGuideline.html">Quality Guideline</a></li>
 *          <li>Choose a desired quality level from the dropdown menu,
 *              and in case opt-in/out further rules using the
 *              checkboxes.</li>
 *          <li>At the bottom of the page you can find the necessary
 *              settings for your <tt>pkgInfo.py</tt> file, or directly
 *              download it. Do not forget to commit them to your version
 *              control system.
 *          </li>
 *      </ol>
 *      </td>
 *
 *      <td style="border-style: solid; border-width: 1px; border-color: #ced6e9;">
 *
 *      <center>
 *          <img src="../BuildSystemTools/ZenBuildMode-SQCheck1-small.png"
 *               width="361" height="232"
 *               alt="Screenshot: SQ requirement definition via application"/>
 *      </center>
 *
 *      <ol>
 *          <li>Launch application:
 *              <div style="font-family: Monospace;">$ BST.py -qz</div></li>
 *
 *          <li>Choose a desired
 *              quality level from the dropdown menu, and in case opt-in/out
 *              further rules using the checkboxes.</li>
 *          <li>Finally press "Save settings".</li>
 *      </ol>
 *      </td>
 * </tr>
 * </table>
 * \endhtmlonly
 *
 * <h2>Validation</h2>
 *
 * <table border="0" width="100%">
 * <tr>
 *      <th width="50%" style="background: #3d578c; color: white;">command-line</th>
 *      <th width="50%" style="background: #3d578c; color: white;">desktop utility</th>
 * </tr>
 * <tr>
 *      <td style="border-style: solid; border-width: 1px; border-color: #ced6e9;
 *                 vertical-align: top;">
 *      Run the following command within your package:
 *      <div style="font-family: Monospace;">$ BST.py -q</div>
 *
 *      It is also possible to specify selected rules and/or
 *      files/directories, e.g. the following command will only validate
 *      rules C01,C02,C03 on the "src" subdirectory:
 *      <div style="font-family: Monospace;">$ cd MyPackage/1.0<br/>
 *                                           $ BST.py -q src C01 C02 C03</div>
 *      </td>
 *
 *      <td style="border-style: solid; border-width: 1px; border-color: #ced6e9;">
 *      <ol>
 *          <li>Press the individual "Check" buttons to perform the
 *              verification:
 *
 *              <center>
 *              <img src="../BuildSystemTools/ZenBuildMode-SQCheck2-small.png"
 *                   width="361" height="232"
 *                   alt="Screenshot: SQ validation in Zen Build Mode"/>
 *              </center>
 *          </li>
 *
 *          <li>Alternatively you could press "Check selected" to run all
 *              checkers.</li>
 *      </ol>
 *      </td>
 * </tr>
 * </table>
 * \endhtmlonly
 *
 * <b>see also:</b>
 * \li \ref ToolBOS_Util_BuildSystemTools_ZenBuildMode
  * \li http://en.wikipedia.org/wiki/Software_quality
 */


/*!
 * \page ToolBOS_Concept_SourceTreeConventions Source tree conventions
 *
 * We assume that software packages are organized in the following directory
 * structure, closely following the "Build system And Software Implementation
 * Standard (BASIS)" and "Semantic versioning" approach.
 *
 * \see http://www.semver.org
 *
 * <center>
 * \image html Concepts/PackageStructure.png
 * <i>Typical package directory structure</i>
 * </center>
 *
 * Only the pkgInfo.py file is mandatory. All others are optional
 * and you may freely add more. But for the once mentioned please try to
 * stick to the existing names and semantics for consistency reasons.
 *
 * <table>
 * <tr>
 *   <th>Name</th>
 *   <th>Things you should know about</th>
 *   <th>Content</th>
 * </tr>
 * <tr>
 *   <td>MyPackage</td>
 *   <td>Name of the package</td>
 *   <td>Contains one subdirectory per package version or branch</td>
 * </tr>
 * <tr>
 *   <td>bin</td>
 *   <td>Each source file will be compiled into one corresponding executable.</td>
 *   <td>Source code of the main programs / executables
 *       (e.g.: HelloWorld.c)</td>
 * </tr>
 * <tr>
 *   <td>doc</td>
 *   <td>You may put additional PDF files, diagrams etc. here and refer to
 *       it from within doxygen</td>
 *   <td>doxygen documentation will be created inside the subdirectory
 *       "html"</td>
 * </tr>
 * <tr>
 *   <td>examples</td>
 *   <td>similar to "bin"</td>
 *   <td>simple exemplary programs to demonstrate the usage of your
 *       software to the end user</td>
 * </tr>
 * <tr>
 *   <td>external</td>
 *   <td>3rd party content that can/should not be separately installed into
 *       SIT (${SIT}/External)</td>
 *   <td>Non-HRI parts</td>
 * </tr>
 * <tr>
 *   <td>install</td>
 *   <td>required directory used by Build System Tools</td>
 *   <td>auto-generated files used by ToolBOS and intermediate files during
 *       package installation phase</td>
 * </tr>
 * <tr>
 *   <td>lib</td>
 *   <td>You should not put any files there. This is directory is for
 *       exclusive use by the Build System Tools. You should remove such
 *       directory if your package is not about static and/or shared
 *       libraries.</td>
 *   <td>the generated static and shared libraries</td>
 * </tr>
 * <tr>
 *   <td>src</td>
 *   <td>put here your C/C++/Java/Matlab/... sources</td>
 *   <td>the main source code of the package</td>
 * </tr>
 <tr>
 *   <td>include</td>
 *   <td>put here your Python sources</td>
 *   <td>the main source code of the package</td>
 * </tr>
 * <tr>
 *   <td>test</td>
 *   <td>You may use any framework for implementing your unit tests.
 *       However it is strongly encouraged to provide a file "unittest.sh"
 *       within your directory which serves as launcher script
 *       for the Nightly Build system, e.g. MyPackage/unittest.sh.</td>
 *   <td>code and reference files for unittest</td>
 * </tr>
 * <tr>
 *   <td>pkgInfo.py</td>
 *   <td>General package related information. (Should always be present in the package)</td>
 *   <td>Contains the version of the package (Major.Minor), name of the package and
 *       the category this package belongs to. \b See \b also \ref ToolBOS_Util_BuildSystemTools_pkgInfo </td>
 * </tr>
 * </table>
 *
 *
 * \note Directories which contain the generated binaries (e.g. "bin" or
 *       "lib") will have one subdirectory per platforms the package was
 *       compiled for. You can later install the package for multiple
 *       platforms in one shot.
 */


/*!
 * \page ToolBOS_Concept_ToolBOSconf ToolBOS.conf
 *
 * If ToolBOS does not detect desired values, you may override or
 * customize certain settings via configfiles.
 * They are Python files typically with simple key-value pair assignments
 * only but might contain script logic as well. The content is being
 * evaluated when loading such files.<p>
 *
 * If a setting is not found in the current <tt>ToolBOS.conf</tt> file,
 * it will look-up the lower priority paths/files until it was found
 * otherwise fallback to the default value shipped with the ToolBOS SDK
 * itself.<p>
 *
 * <b>The paths/files are searched in the following order:</b>
 * \li <tt>./ToolBOS.conf</tt> (current working directory)
 * \li entries from additional search-paths if provided
 * \li <tt>${HOME}/.HRI/ToolBOS/ToolBOS.conf</tt> (user-settings)
 * \li <tt>/etc/ToolBOS.conf</tt> (machine-wide settings by sysadmin)
 * \li <tt>${TOOLBOSCORE_ROOT}/etc/ToolBOS.conf</tt> (fallback / defaults)
 *
 * <h2>Example</h2>
 *
 * In order to tell the \c SVNCheckout.py script to always use a different
 * username when connecting to the SVN server 'svnext', create a file
 * <tt>${HOME}/.HRI/ToolBOS/ToolBOS.conf</tt> with the following content:
 *
 * \code
   serverAccounts = { 'svnext': 'marcus' }
   \endcode
 *
 * <h2>Commandline usage</h2>
 *
 * You may configure your settings using <tt>ToolBOS-Config.py</tt>:
 *
 * \verbatim
   $ ToolBOS-Config.py                                 # list all settings

   $ ToolBOS-Config.py -p hostPlatform                 # print host platform

   $ ToolBOS-Config.py -s "foo=bar"                    # add custom setting
   \endverbatim
 *
 * <h2>List of possible settings</h2>
 *
 * <table>
 * <tr>
 *   <th>key</th>
 *   <th>description</th>
 * </tr>
 *
 * <tr>
 *   <td><tt>askGlobalInstallReason</tt></td>
 *   <td>enable / disable the need to provide globalinstall-reason
 *       (log message, default: True)</td>
 * </tr>
 *
 * <tr>
 *   <td><tt>BST_compileHosts</tt></td>
 *   <td>BST.py: mapping of platform names to names of native compile hosts in
 *       this network</td>
 * </tr>
 <tr>
 *   <td><tt>BST_confirmInstall</tt></td>
 *   <td>interactively confirm global installation? (default: False)</td>
 * </tr>
 * <tr>
 *   <td><tt>BST_crossCompileBSPs</tt></td>
 *   <td>BST.py: mapping of platform names to the canonical path of the
 *       extension package necessary to source prior to cross-compiling</td>
 * </tr>
 * <tr>
 *   <td><tt>BST_crossCompileHosts</tt></td>
 *   <td>BST.py: mapping of platform names to names of cross-compile hosts in
 *       this network</td>
 * </tr>
 * <tr>
 *   <td><tt>BST_modulePath</tt></td>
 *   <td>location of <tt>BuildSystemTools.cmake</tt></td>
 * </tr>
 * <tr>
 *   <td><tt>BST_svnCheck</tt></td>
 *   <td>perform SVN consistency check at global installation
 *       (default: True)</td>
 * </tr>
 * <tr>
 *   <td><tt>BST_useClang</tt></td>
 *   <td>enable / disable the usage of Clang/LLVM for compiling C/C++ code
 *       (default: False)</td>
 * </tr>
 * <tr>
 *   <td><tt>BST_useDoxypy</tt></td>
 *   <td>enable / disable the usage of \c Doxypy when creating
 *       doxygen-documentation for Python code (default: True)</td>
 * </tr>
 * <tr>
 *   <td><tt>bugtrackURL</tt></td>
 *   <td>location of the issue tracker system, e.g. JIRA (http://hostname/path)</td>
 * </tr>
 * <tr>
 *   <td><tt>CIA_account</tt></td>
 *   <td>CIA buildbot account name</td>
 * </tr>
 * <tr>
 *   <td><tt>CIA_startKey</tt></td>
 *   <td>path to the SSH keyfile which shall be used for connecting to the
 *       Nightly Build servers in order to trigger the build</td>
 * </tr>
 * <tr>
 *   <td><tt>CIA_checkoutKey</tt></td>
 *   <td>path to the SSH keyfile which shall be used by the Nightly Build
 *       process for connecting to the SVN server (read only access to SVN
 *       repositories)</td>
 * </tr>
 * <tr>
 *   <td><tt>CIA_commitKey</tt></td>
 *   <td>path to the SSH keyfile which shall be used by the Nightly Build
 *       process for connecting to the SVN server (read/write access to SVN
 *       repositories)</td>
 * </tr>
 * <tr>
 *   <td><tt>CIA_compileHosts</tt></td>
 *   <td>dict containing a mapping of platform names to the compile hosts
 *       to use</td>
 * </tr>
 * <tr>
 *   <td><tt>CIA_targetPlatforms</tt></td>
 *   <td>set of platforms CIA shall compile for</td>
 * </tr>
 * <tr>
 *   <td><tt>clang_lib</tt>
 *   <td>dict containing a mapping of platform names to the path to
 *       libclang.so, used by the SQ checkers</td>
 * </tr>
 * <tr>
 *   <td><tt>defaultPlatform</tt></td>
 *   <td>mainstream platform used by the majority of users</td>
 * </tr>
 * <tr>
 *   <td><tt>defaultSVNServer</tt></td>
 *   <td>server where to create new SVN repositories by default</td>
 * </tr>
 * <tr>
 *   <td><tt>defaultSVNRepositoryPath</tt></td>
 *   <td>path to repository root on 'defaultSVNServer' (root path where all
 *       the SVN repositories are located),
 *       e.g. /data/subversion/HRIREPOS</td>
 * </tr>
 * <tr>
 *   <td><tt>documentationServer</tt></td>
 *   <td>URL to documentation server (https://...)</td>
 * </tr>
 * <tr>
 *   <td><tt>documentationURL</tt></td>
 *   <td>location of the doxygen documentation of ToolBOSCore itself</td>
 * </tr>
 * <tr>
 *   <td><tt>documentationURL_sit</tt></td>
 *   <td>location of the SIT on the documentation server
 *       (http://.../sit/latest/)</td>
 * </tr>
 * <tr>
 *   <td><tt>documentationURL_dir</tt></td>
 *   <td>location of the doxygen documentation of ToolBOSCore itself
 *       (http://.../doc/html/)</td>
 * </tr>
 * <tr>
 *   <td><tt>documentationURL</tt></td>
 *   <td>URL to the doxygen documentation of ToolBOSCore itself
 *       (composed of <tt>documentationURL_dir + 'index.html'</tt></td>
 * </tr>
 * <tr>
 *   <td><tt>DTBOS_curvedLinks</tt></td>
 *   <td>use splines for the links between components (True), or straight lines (False)</td>
 * </tr>
 * <tr>
 *   <td><tt>DTBOS_showBoxShadows</tt></td>
 *   <td>boolean whether or not to display dropshadow effects around boxes</td>
 * </tr>
 * <tr>
 *   <td><tt>Git_allowedHosts</tt></td>
 *   <td>whitelist of hosts allowed to clone from during Nightly Build,
 *       aka servers considered to contain the official versions</td>
 * </tr>
 * <tr>
 *   <td><tt>hostArch</tt></td>
 *   <td>value of MAKEFILE_CPU to use inside Python scripts</td>
 * </tr>
 * <tr>
 *   <td><tt>hostOS</tt></td>
 *   <td>value of MAKEFILE_OS to use inside Python scripts</td>
 * </tr>
 * <tr>
 *   <td><tt>hostPlatform</tt></td>
 *   <td>value of MAKEFILE_PLATFORM to use inside Python scripts</td>
 * </tr>
 * <tr>
 *   <td><tt>installGroup</tt></td>
 *   <td>set group of installed files to specified group name</td>
 * </tr>
 * <tr>
 *   <td><tt>installUmask</tt></td>
 *   <td>override user's umask-setting when installing packages
 *       (can be specified as decimal integer, octal integer, or string)</td>
 * </tr>
 * <tr>
 *   <td><tt>kwLicenseServerHost</tt></td>
 *   <td>Klocwork license server hostname (e.g. "hri-licenses")</td>
 * </tr>
 * <tr>
 *   <td><tt>kwLicenseServerPort</tt></td>
 *   <td>Klocwork license server port (integer)</td>
 * </tr>
 * <tr>
 *   <td><tt>package_clion</tt></td>
 *   <td>canonical path of CLion SIT package (e.g. "External/CLion/1.0")</td>
 * </tr>
 * <tr>
 *   <td><tt>package_klocwork</tt></td>
 *   <td>canonical path of Klocwork SIT package (e.g. "External/klocwork/10.2")</td>
 * </tr>
 * <tr>
 *   <td><tt>package_libxml</tt></td>
 *   <td>canonical path of libxml SIT package (e.g. "External/libxml2/2.6")</td>
 * </tr>
 * <tr>
 *   <td><tt>package_matlab</tt></td>
 *   <td>canonical path of Matlab package (e.g. "External/Matlab/8.4")</td>
 * </tr>
 * <tr>
 *   <td><tt>package_nanomsg</tt></td>
 *   <td>canonical path of the NanoMsg library to use (e.g. "External/nanomsg/1.0")</td>
 * </tr>
 * <tr>
 *   <td><tt>package_pycharm</tt></td>
 *   <td>canonical path of PyCharm SIT package (e.g. "External/PyCharmPro/4.5")</td>
 * </tr>
 * <tr>
 *   <td><tt>package_totalview</tt></td>
 *   <td>canonical path of TotalView debugger package
 *       (e.g. "External/totalview/8.15")</td>
 * </tr>
 * <tr>
 *   <td><tt>RTBOS_portRange</tt></td>
 *   <td>tuple(min,max) for auto-assigning port numbers to RTBOS machines
 *       (e.g. (2000,2100) wheres the min-value is included but the max-value
 *       is excluded from the range)</td>
 * </tr>
 * <tr>
 *   <td><tt>serverAccounts</tt></td>
 *   <td>username to use for SSH when connecting to certain hosts
 *       (a Python dictionary mapping hostname => username)</td>
 * </tr>
 * <tr>
 *   <td><tt>SVN_allowedHosts</tt></td>
 *   <td>whitelist of hosts allowed to checkout from during Nightly Build,
 *       aka servers considered to contain the official versions</td>
 * </tr>
 * </table>
 *
 * \example ToolBOS.conf
 */


/*!
 * \page ToolBOS_Util Tools
 *
 * \image html ToolBOS-Logo.png
 *
 * \li \subpage ToolBOS_Util_PackageCreator
 * \li \subpage ToolBOS_Util_BuildSystemTools
 * \li \subpage ToolBOS_UseCases_ExecInAllProjects
 */


/*!
 * \page ToolBOS_Util_PackageCreator Package Creator
 *
 * The <b>Package Creator</b> uses the open-source <b>Mako Template
 * Engine</b> for creating new boilerplate software packages from templates.
 *
 * <h3>Usage</h3>
 * \li \subpage ToolBOS_Util_PackageCreator_GUI
 * \li \subpage ToolBOS_Util_PackageCreator_CLI
 * \li \subpage ToolBOS_Util_PackageCreator_API
 *
 * \see \ref ToolBOS_Concept_SourceTreeConventions
 * \see http://www.makotemplates.org
 *
 * \htmlonly
 * </div>
 * \endhtmlonly
 *
 * \page ToolBOS_Util_PackageCreator_GUI GUI
 *
 * Run this command:
 * \verbatim
 $ BST.py --new
 \endverbatim
 *
 * <center>
 * \image html PackageCreator/PackageCreatorGUI-1.png
 * <i>1. Select the type of package to create</i>
 *
 * \image html PackageCreator/PackageCreatorGUI-2.png
 * <i>2. fill the necessary fields and press 'Create'</i>
 * </center>
 *
 * \htmlonly
 * </div>
 * \endhtmlonly
 *
 * \page ToolBOS_Util_PackageCreator_CLI command-line
 *
 * \note Run <tt><b>BST.py --new help</b></tt> to see the full list of
 *       available templates.
 *
 * <h3>Syntax:</h3>
 * \verbatim
 BST.py --new <TEMPLATE> <PACKAGE_NAME> <PACKAGE_VERSION>
 \endverbatim
 *
 * <h3>Example:</h3>
 * \verbatim
 $ BST.py --new C_Library MyPackage 1.0
 [PackageCreator.py:244 INFO] creating skeleton dir. structure
 [PackageCreator.py:197 INFO] processing MyPackage/1.0/CMakeLists.txt
 [PackageCreator.py:197 INFO] processing MyPackage/1.0/src/MyPackage.c
 [PackageCreator.py:197 INFO] processing MyPackage/1.0/src/MyPackage.h
 [PackageCreator.py:197 INFO] processing MyPackage/1.0/test/unittest.c
 [PackageCreator.py:197 INFO] processing MyPackage/1.0/unittest.sh

 $ tree MyPackage/

 MyPackage/
 └── 1.0
     ├── CMakeLists.txt
     ├── src
     │   ├── MyPackage.c
     │   └── MyPackage.h
     ├── test
     │   └── unittest.c
     └── unittest.sh

 8 directories, 6 files
 \endverbatim
 *
 * \htmlonly
 * </div>
 * \endhtmlonly
 *
 * \page ToolBOS_Util_PackageCreator_API Python API
 *
 * The <b>Package Creator</b> can be embedded into your Python application
 * to create packages programmatically.
 *
 * <h3>Example</h3>
 *
 * This uses the \c C_Library template to create a package \c /tmp/test/Foo/1.0
 * with the \c category set to \c "Libraries/Data":
 *
 * \verbatim
   from ToolBOSCore.Packages.PackageCreator import PackageCreator_C_Library

   values = { 'category': 'Libraries/Data' }
   pc     = PackageCreator_C_Library( 'Foo', '1.0', values, '/tmp/test' )

   pc.run()
   \endverbatim
 *
 * <h3>"values" documentation</h3>
 *
 * \c values must be a Python \c dict containing any of the following keys:
 *
 * <table>
 * <tr>
 *   <th>key</th>
 *   <th>datatype</th>
 *   <th>description</th>
 * </tr>
 * <tr>
 *   <td><tt>buildRules</tt></td>
 *   <td>string</td>
 *   <td>Put this text verbatim in the \c CMakeLists.txt instead of the default
 *       build instructions. Note that if this key is specified then
 *       <tt>srcFilesPattern</tt>, <tt>exeFilesPattern</tt>,
 *       <tt>preBuildRules</tt> and <tt>postBuildRules</tt> have no effect.</td>
 * </tr>
 * <tr>
 *   <td><tt>preBuildRules</tt></td>
 *   <td>string</td>
 *   <td>Put this text verbatim in the \c CMakeLists.txt just before the
 *       default build rules.</td>
 * </tr>
 * <tr>
 *   <td><tt>postBuildRules</tt></td>
 *   <td>string</td>
 *   <td>Put this text verbatim in the \c CMakeLists.txt right after the
 *       default build rules.</td>
 * </tr>
 * <tr>
 *   <td><tt>srcFilesPattern</tt></td>
 *   <td>string</td>
 *   <td>Glob-expression which shall be used for searching library source
 *       files (e.g. <tt>"src/A/*.c src/B/*.c"</tt>).
 *       Has no effect if <tt>buildRules</tt> is specified.</td>
 * </tr>
 * <tr>
 *   <td><tt>exeFilesPattern</tt></td>
 *   <td>string</td>
 *   <td>Glob-expression which shall be used for searching main program source
 *       files (e.g. <tt>"bin/*.c examples/*.c"</tt>).
 *       Has no effect if <tt>buildRules</tt> is specified.</td>
 * </tr>
 * <tr>
 *   <td><tt>category</tt></td>
 *   <td>string</td>
 *   <td>SIT category of the package, such as \c "Libraries"</td>
 * </tr>
 * <tr>
 *   <td><tt>dependencies</tt></td>
 *   <td>list</td>
 *   <td>list of packages that will be put into "bst_find_package()" statements
 *       in the \c CMakeLists.txt </td>
 * </tr>
 * <tr>
 *   <td><tt>force</tt></td>
 *   <td>boolean</td>
 *   <td>ignore certain safety checks, f.i. overwrite existing files</td>
 * </tr>
 * </table>
 *
 * \see \ref PackageCreator.py
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools Build System Tools
 *
 * <img src="../Logos/BST.png" align="right">
 *
 * <h2>Getting started</h2>
 * \li \subpage ToolBOS_Util_BuildSystemTools_About
 * \li \subpage ToolBOS_Util_BuildSystemTools_QuickStart
 * \li \subpage ToolBOS_Util_BuildSystemTools_QuickStartWindows
 *
 * <h2>Creating packages</h2>
 * \li \subpage ToolBOS_Util_PackageCreator
 *
 * <h2>Building</h2>
 * \li \subpage ToolBOS_Util_BuildSystemTools_CheatSheet
 * \li \subpage ToolBOS_Util_BuildSystemTools_pkgInfo
 * \li \subpage ToolBOS_Util_BuildSystemTools_CrossCompiling
 * \li \subpage ToolBOS_Util_BuildSystemTools_ZenBuildMode
 * \li \subpage ToolBOS_Util_BuildSystemTools_StaticLinking
 * \li \subpage ToolBOS_Util_BuildSystemTools_OutOfTree
 * \li \subpage ToolBOS_Util_BuildSystemTools_Macros
 * \li \subpage ToolBOS_Util_BuildSystemTools_WindowsFAQ
 * \li \subpage ToolBOS_Util_BuildSystemTools_ClangLLVM
 *
 * <h2>Post-build</h2>
 * \li \subpage ToolBOS_Util_BuildSystemTools_Execution
 * \li \subpage ToolBOS_Util_BuildSystemTools_Unittesting
 * \li \subpage ToolBOS_Util_BuildSystemTools_Installation
 * \li \subpage ToolBOS_Util_BuildSystemTools_Uninstalling
 * \li \subpage ToolBOS_Util_BuildSystemTools_Cleaning
 *
 * <h2>Customization</h2>
 * \li \subpage ToolBOS_Util_BuildSystemTools_CustomScripts
 * \li \subpage ToolBOS_Util_BuildSystemTools_Variables
 * \li \subpage ToolBOS_Util_BuildSystemTools_MultiPlatform
 *
 * \see \ref ToolBOS_HowTo_Debugging
 * \see \ref ToolBOS_Concept_ToolBOSconf
 * \see http://www.cmake.org/cmake/help/documentation.html
 *
 * \htmlonly
 * </div>
 * \endhtmlonly
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_About About
 *
 * \image html Logos/BST-small.png
 *
 * \li The Build System Tools (BST.py) are using underlying OS-specific tools
 * such as compilers and linkers for compiling and installing software
 * packages.
 *
 * \li They can directly be used by the developers, but also integrated into
 * build automation systems (f.i. CIA).
 *
 * \li The Build System Tools attempt to handle different types of packages
 * equally (regardless their programming language or if they are
 * developed in-house or externally).
 *
 * \image html Concepts/BuildSystem.png
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_OutOfTree In-tree- vs. out-of-tree builds
 *
 * <h2>Source directory</h2>
 *
 * <center>
 * \image html BuildSystemTools/OutOfTreeBuild1.png
 * <i>Clean SVN working copy at start-up</i>
 * </center>
 *
 * <h2>In-tree builds</h2>
 *
 * For historical reasons most ToolBOS users perform <b>"in-tree builds"</b>,
 * f.i. the compiled binaries stay together with the source code. However
 * this somehow clutters the source tree.
 *
 * \verbatim
   $ cd ~/MasterClock/1.6

   $ BST.py
   [...]
   \endverbatim
 *
 * <center>
 * \image html BuildSystemTools/InTreeBuild.png
 * <i>After compilation the build artefacts can be found inside the source
      tree</i>
 * </center>
 *
 * <h2>Out-of-tree builds</h2>
 *
 * This way the source code (e.g. SVN working copy) stays separate from the
 * build artefacts. This implies working with two different file locations,
 * referred to as "source tree" and "binary tree".
 *
   \verbatim
   $ cd /tmp/mstein/outoftree

   $ BST.py ~/MasterClock/1.6
   [BST.py:482 INFO] source tree: /home/mstein/MasterClock/1.6
   [BST.py:483 INFO] binary tree: /tmp/mstein/outoftree
   [...]
   \endverbatim
 *
 * \note You need to pass the source-tree location only once. Subsequent
 *       calls of \c BST.py will remember the corresponding source-tree
 *       location.
 *
 * <center>
 * \image html BuildSystemTools/OutOfTreeBuild1.png
 * <i>The source tree stays untouched</i>
 *
 * \image html BuildSystemTools/OutOfTreeBuild2.png
 * <i>The build artefacts are separated from the source tree</i>
 * </center>
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_Macros Macros documentation
 *
 * ToolBOS provides a few helper macros to write \c CMakeLists.txt files.
 * Consider them as sugar, they are totally optional.
 *
 * Pass the \c -DCMAKE_MODULE_PATH=${TOOLBOSCORE_ROOT}/include/CMake option
 * to CMake to find the BuildSystemTools.cmake file. In your
 * \c CMakeLists.txt include it as follows:
 *
 * \code
   find_package(BuildSystemTools)
   \endcode
 *
 * \note \b Hint: For easy exchange with collaborative partners you may store
 *       a copy of these Build System Tools files within your package.
 *       This way they are also under your version control system.
 *
 * <h2>Dependency inclusion</h2>
 *
 * <table>
 * <tr>
 *   <th align="left"><tt>bst_find_package(PACKAGE)</tt></th>
 * </tr>
 * <tr>
 *   <td>Use this macro to import packages from the SIT.
 *       It is a decorator of CMake's \c find_package function specific for
 *       importing settings from a \c packageVar.cmake file located in the
 *       SIT.
 *
 *       \c PACKAGE must be a "canonical package name" f.i. no leading
 *       \c ${SIT} or the like, nor a trailing
 *       \c packageVar.cmake .
 *</td>
 * </tr>
 * <tr>
 *   <td>\b Example:
 *       \code
         bst_find_package(DevelopmentTools/ToolBOSCore/3.3)
         bst_find_package(Libraries/MasterClock/1.6)
         \endcode
 *
 *       This includes both packages ToolBOSCore 3.3 and MasterClock 1.6
 *       (and recursively all of their dependencies) from the SIT.
 *
 *       The \c packageVar.cmake inside each of these packages is
 *       responsible for setting the necessary include directories,
 *       library paths, and flags. One ToolBOS-specific addition is the
 *       variable \c BST_LIBRARIES_SHARED used to inherit the list of
 *       shared libraries to (optionally) later link against.</th>
 * </tr>
 * </table>
 *
 * <h2>Building static + shared libraries</h2>
 *
 * <table>
 * <tr>
 *   <th align="left"><tt>bst_build_libraries(FILELIST LIBNAME LINK_LIBRARIES)</tt></th>
 * </tr>
 * <tr>
 *   <td>This creates both static and shared libraries from all the source
 *       files listed in \c FILELIST .
 *
 *       If the package is only about one set of static/shared libraries,
 *       the \c LIBNAME should match the package name. Prefixes and suffixes
 *       (e.g. \c .so or \c .dll ) will be automatically added depending on
 *       the target platform. The libraries will will be placed into a
 *       subdirectory corresponding to the \c MAKEFILE_PLATFORM environment
 *       variable.
 *
 *       Additionally both libraries will be linked against the libraries
 *       listed in \c LINK_LIBRARIES. </td>
 * </tr>
 * <tr>
 *   <td>\b Example:
 *       \code
         file(GLOB SRC_FILES src/*.c src/*.cpp)

         bst_build_libraries("${SRC_FILES}" "${PROJECT_NAME}" "${BST_LIBRARIES_SHARED}")
         \endcode
 *
 *       This will compile all C/C++ source files within the \c src subdirectory
 *       to object files, and create static and shared libraries out of them.
 *
 *       The name of the library will correspond to the package name.
 *       Under Linux, a package "Foo/1.0" would result in \c libFoo.a and
 *       \c libFoo.so.1.0 . Additionally a non-versioned symlink
 *       \c libFoo.so pointing to \c libFoo.so.1.0 will be created.
 *
 *       The library will be linked against all the libraries listed in
 *       \c ${BST_LIBRARIES_SHARED} (which is the list of libraries inherited
 *       from prior \c bst_find_package inclusions). In this example
 *       this means the MasterClock library and all its dependent libraries
 *       such as ToolBOSCore, pthread,...</th>
 * </tr>
 * </table>
 *
 * <h2>Building one single executable</h2>
 *
 * <table>
 * <tr>
 *   <th align="left"><tt>bst_build_executable(TARGET_NAME FILELIST LINK_LIBRARIES)</tt></th>
 * </tr>
 * <tr>
 *   <td>Compiles all files in \c FILELIST into one single executable named
 *       \c TARGET_NAME. It will be placed into a subdirectory corresponding
 *       to the \c MAKEFILE_PLATFORM environment variable.
 *
 *       Additionally it will be linked against the libraries listed in
 *       \c LINK_LIBRARIES. </td>
 * </tr>
 * <tr>
 *   <td>\b Example:
 *       \code
 *       bst_find_package(Libraries/MasterClock/1.6)
 *
 *       file(GLOB FOO_FILES bin/Foo*.c)
 *       bst_build_executable(Foo "${FOO_FILES}" "${BST_LIBRARIES_SHARED}")
 *       \endcode
 *
 *       This will compile all files matching <tt>bin/Foo*.c</tt> into a single
 *       executable named \c bin/${MAKEFILE_PLATFORM}/Foo.
 *
 *       The executable will be linked against all the libraries listed in
 *       \c ${BST_LIBRARIES_SHARED} (which is the list of libraries inherited
 *       from prior \c bst_find_package inclusions). In this example
 *       this means the MasterClock library and all its dependent libraries
 *       such as ToolBOSCore, pthread,...</th>
 * </tr>
 * </table>
 *
 * <h2>Building multiple executables</h2>
 *
 * <table>
 * <tr>
 *   <th align="left"><tt>bst_build_executables(FILELIST LINK_LIBRARIES)</tt></th>
 * </tr>
 * <tr>
 *   <td>Invokes a \c bst_build_executable for each file in \c FILELIST .
 *       The filename of each executable will match the source file apart
 *       from the extension (\c Foo.c → \c Foo on Linux resp. \c Foo.exe
 *       on Windows). The executables will be placed into a subdirectory
 *       corresponding to the \c MAKEFILE_PLATFORM environment variable.
 *
 *       Additionally they will be linked against the libraries listed in
 *       \c LINK_LIBRARIES. </td>
 * </tr>
 * <tr>
 *   <td>\b Example:
 *       \code
 *       bst_find_package(Libraries/MasterClock/1.6)
 *
 *       file(GLOB FOO_FILES bin/Foo*.c)
 *       bst_build_executables("${FOO_FILES}" "${BST_LIBRARIES_SHARED}")
 *       \endcode
 *
 *       This will compile all files matching <tt>bin/Foo*.c</tt> into
 *       separate executables named \c bin/${MAKEFILE_PLATFORM}/Foo* (see
 *       documentation of \c bst_build_executable ).
 *
 *       The executables will be linked against all the libraries listed in
 *       \c ${BST_LIBRARIES_SHARED} (which is the list of libraries inherited
 *       from prior \c bst_find_package inclusions). In this example
 *       this means the MasterClock library and all its dependent libraries
 *       such as ToolBOSCore, pthread,...</th>
 * </tr>
 * </table>
 *
 * <h2>Building single MEX file for Matlab</h2>
 *
 * <table>
 * <tr>
 *   <th align="left"><tt>bst_build_mexfile(FILELIST LIBNAME LINK_LIBRARIES)</tt></th>
 * </tr>
 * <tr>
 *   <td>This creates a special type of library for Matlab ("mexfile").
 *       If the package only contains one mexfile,
 *       the \c LIBNAME should match the package name. Prefixes and suffixes
 *       (e.g. \c .mexglx ) will be automatically added depending on
 *       the target platform. The mexfile will be put into a subdirectory
 *       named \c wrapper .
 *
 *       Additionally the mexfile will be linked against the libraries
 *       listed in \c LINK_LIBRARIES.
 *       </td>
 * </tr>
 * <tr>
 *   <td>\b Example:
 *       \code
         bst_find_package(External/Matlab/8.2)
         bst_find_package(DevelopmentTools/ToolBOSPluginMatlab/1.2)

         file(GLOB WRAPPER_FILES wrapper/*.c wrapper/*.cpp)

         list(APPEND BST_LIBRARIES_SHARED "${PROJECT_NAME}-shared")
         bst_build_mexfile("${WRAPPER_FILES}" "${PROJECT_NAME}Wrapper" "${BST_LIBRARIES_SHARED}")
         \endcode
 *
 *       This will compile all C/C++ source files within the \c wrapper
 *       subdirectory to object files, and create a special "mexfile" for
 *       Matlab out of them.
 *
 *       The name of the library will correspond to the package name.
 *       Under 32 bit Linux a package "Foo/1.0" would result in
 *       \c Foo.mexglx while under 64 bit Linux it would be named
 *       \c Foo.mexa64 .
 *
 *       The library will be linked against all the libraries listed in
 *       \c ${BST_LIBRARIES_SHARED} (which is the list of libraries inherited
 *       from prior \c bst_find_package inclusions). The mexfile also gets
 *       linked against the package's main library (which under Linux
 *       would be \c libfoo.so).</th>
 * </tr>
 * </table>
 *
 * <h2>Building multiple MEX files for Matlab</h2>
 *
 * <table>
 * <tr>
 *   <th align="left"><tt>bst_build_mexfiles(FILELIST LINK_LIBRARIES)</tt></th>
 * </tr>
 * <tr>
 *   <td>Invokes a \c bst_build_mexfile for each file in \c FILELIST .
 *       The filename of each resulting binary will match the source file apart
 *       from the extension (\c Foo.c → \c Foo.mexglx on 32 bit resp.
 *       \c Foo.mexa64 on 64 bit). The binaries will be placed into the same
 *       directory where the source files are located, because Matlab requires
 *       them to stay together within one directory.
 *
 *       Additionally they will be linked against the libraries listed in
 *       \c LINK_LIBRARIES. </td>
 * </tr>
 * <tr>
 *   <td>\b Example:
 *       \code
         bst_find_package(External/Matlab/8.2)
         bst_find_package(DevelopmentTools/ToolBOSPluginMatlab/1.2)

         file(GLOB MEX_SOURCES bin/*.c)
         bst_build_mexfiles("${MEX_SOURCES}" "${BST_LIBRARIES_SHARED}")
         \endcode
 *
 *       This will compile all files matching <tt>bin/*.c</tt> into
 *       separate mexfiles named \c lib/${MAKEFILE_PLATFORM}/*.mexglx on 32 bit
 *       resp. \c *.mexa64 on 64 bit Linux, or \c *.mexw32 on Windows.
 *
 *       The mexfiles will be linked against all the libraries listed in
 *       \c ${BST_LIBRARIES_SHARED} (which is the list of libraries inherited
 *       from prior \c bst_find_package inclusions). In this example
 *       this means all the used libraries provided by Matlab and the
 *       ToolBOSPluginMatlab packages.</td>
 * </tr>
 * </table>
 *
 * <h2>Building a Java Archive (JAR)</h2>
 *
 * <table>
 * <tr>
 *   <th align="left"><tt>bst_build_jar(FILELIST LIBNAME JARS ENTRY SOURCEDIR)</tt></th>
 * </tr>
 * <tr>
 *   <td>Compiles all files in \c FILELIST and creates an output file
 *       \c LIBNAME.jar. All sources must be relative to \c SOURCEDIR.
 *       Additional Java archives to be included can be specified (empty list
 *       otherwise). The main entry class of the Java must be given using
 *       \c ENTRY and will be written into the Java Manifest. Note that the
 *       main class can be overriden at start-up of the Java VM process.
 * </tr>
 * <tr>
 *   <td>\b Example:
 *       \code
         file(GLOB FILELIST src/*.java)

         bst_build_jar("${FILELIST}" MyApp "3rdParty.jar" "de/honda-ri/MainClass" src)
         \endcode
         </td>
 * </tr>
 * </table>
 *
 * <h2>Building RTMaps packages (*.pck)</h2>
 *
 * <table>
 * <tr>
 *   <th align="left"><tt>bst_build_rtmaps_package(FILELIST LIBNAME LINK_LIBRARIES)</tt></th>
 * </tr>
 * <tr>
 *   <td>Creates an RTMaps package from all the source files listed in
 *       \c FILELIST (each source file corresponds to one RTMaps component).
 *
 *       By convention the \c LIBNAME should match the package name.
 *       Note that RTMaps requires the extension \c .pck even though these are
 *       regular shared library (\c .so or \c .dll ) files. Furthermore a
 *       valid RTMaps license is required at compile time, because the building
 *       process embeds a binary DRM blob into the shared library. In order to
 *       embed the correct DRM signature for the RTMaps version in use, please
 *       ensure that \c bst_find_package is used for adding the dependency to
 *       the desired RTMaps version.
 *
 *       Finally the RTMaps package will be linked against the libraries
 *       listed in \c LINK_LIBRARIES. </td>
 * </tr>
 * <tr>
 *   <td>\b Example:
 *       \code
         file(GLOB SRC_FILES src/*.c src/*.cpp)

         bst_build_rtmaps_package("${SRC_FILES}" "${PROJECT_NAME}" "${BST_LIBRARIES_SHARED}")
         \endcode
 *
 *       This will compile all C/C++ source files within the \c src subdirectory
 *       into an RTMaps package.
 *
 *       The name of the library will correspond to the package name.
 *       Under Linux, a package named "Foo" would result in \c Foo.pck.
 *
 *       The library will be linked against all the libraries listed in
 *       \c ${BST_LIBRARIES_SHARED} (which is the list of libraries inherited
 *       from prior \c bst_find_package inclusions).</th>
 * </tr>
 * </table>
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_QuickStart Quickstart on Linux
 *
 * \image html Logos/BST-small.png
 *
 * <h2>GUI usage</h2>
 *
 * Go to the top-level directory of your package and start the
 * \ref ToolBOS_Util_BuildSystemTools_ZenBuildMode. Within the GUI select
 * the desired platform(s) to build for and press the \c Build button.
 *
 * \verbatim
   $ cd MyPackage/1.0

   $ BST.py -z
   \endverbatim
 *
 * \image html BuildSystemTools/ZenBuildMode-800x487.png
 *
 * <h2>Command-line usage</h2>
 *
 * Go to the top-level directory of your package and run \c BST.py :
 * \verbatim
   $ cd MyPackage/1.0

   $ BST.py
   [...compiler output...]
   \endverbatim
 *
 * You will find the compiled executables in <tt>./bin/&lt;platform&gt;</tt>,
 * and libraries within <tt>./lib/&lt;platform&gt;</tt>.
 *
 * When you're done with you work you may want to clean-up the package:
 * \verbatim
   $ BST.py -d
   [BuildSystemTools.py:227 INFO] cleaning package
   \endverbatim
 *
 * To see all available commandline options, run:
 * \verbatim
   $ BST.py --help
   \endverbatim
 *
 * \htmlonly
 * </div>
 * \endhtmlonly
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_ClangLLVM Clang/LLVM
 *
 * Under Linux \c BST.py allows compiling using the Clang/LLVM compiler
 * infrastructure (default: GCC). Clang/LLVM is said to:
 * \li generally produce better error messages
 * \li compile faster than GCC
 * \li in some scenarios create faster / smaller binaries
 *
 * <h3>Usage</h3>
 *
 * \verbatim
   $ export BST_USE_CLANG=TRUE

   $ BST.py
   \endverbatim
 *
 * You may also fix this setting
 * \li in the \ref ToolBOS_Util_BuildSystemTools_pkgInfo if it is package-specific or
 * \li in the \ref ToolBOS_Concept_ToolBOSconf if it is a user- or site-preference.
 *
 * <h3>Weblinks</h3>
 *
 * \li http://www.llvm.org
 * \li http://www.clang.org
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_Unittesting Unittests
 *
 * \image html BST-small.png
 *
 * The command
 * \verbatim
   $ BST.py -t
   \endverbatim
 *
 * launches the script \c unittest.sh on Unix resp. \c unittest.bat on Windows.
 *
 * \image html WindowsUnittest.png
 *
 * You may call arbitrary test programs from such scripts, incl. calling
 * Python- or Matlab interpreters.
 *
 * \c BST.py considers the unittests to have passed as long as the
 * \c unittest.{sh|bat} script returns \c 0.
 *
 * <h3>Example</h3>
 *
 * ToolBOS SDK comes with built-in support for \b CuTest, a very easy to
 * use unittesting "framework" which is actually just a set of C macros.
 * It is supported on both Linux and Windows.
 *
 * \see \ref unittest.c
 *
 * In good cases it might look like this:
 *
 * \verbatim
   $ BST.py -t
   ................

   OK (16 tests)
   \endverbatim
 *
 * while in case the second testcase failed:
 *
 * \verbatim
   .F..............

   There was 1 failure:
   1) Test_myFunc2: unittest.c:58: expected <42> but was <123>

   !!!FAILURES!!!
   Runs: 2 Passes: 1 Fails: 1
   \endverbatim
 *
 * \see <a href="http://cutest.sourceforge.net">http://cutest.sourceforge.net</a>
 *
 * \example unittest.c
 *
 * \htmlonly
 * </div>
 * \endhtmlonly
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_ZenBuildMode Zen Build Mode
 *
 * \image html Logos/ZenBuildMode-100x100.png
 *
 * Be a zen-master and orchestrate complicated build scenarios with this
 * powerful yet simple GUI.
 *
 * <h3>Features:</h3>
 * \li build for multiple architectures in parallel
 * \li no need to worry about cross-compiler settings
 * \li operator shell: execute commands locally, or on all remote hosts
 * \li open SSH connection to build servers (right into remote working directory)
 * \li parallel + distributed compilation
 * \li launch developer tools
 * \li run \ref ToolBOS_Concept_SoftwareQuality "software quality" checks
 * \li ...
 *
 * <h3>Usage:</h3>
 *
 * Go to the top-level directory of your package and start the "Zen Build
 * Mode". Within the GUI select the desired platform(s) to build for
 * and press the \c Build button.
 *
 * \code
   $ cd MyPackage/1.0

   $ BST.py -z
   \endcode
 *
 * \image html BuildSystemTools/ZenBuildMode-800x487.png
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_QuickStartWindows Quickstart on Windows
 *
 * \image html Logos/BST-small.png
 *
 * <h2>Cross-compiling from Linux to Windows</h2>
 *
 * \li \ref ToolBOS_Util_BuildSystemTools_CrossCompiling
 *
 * <h2>Visual Studio 2010</h2>
 *
 * \li \subpage ToolBOS_Util_BuildSystemTools_WindowsXP
 * \li \subpage ToolBOS_Util_BuildSystemTools_WindowsManually
 *
 * <h2>Visual Studio 2012</h2>
 *
 * \li \subpage ToolBOS_Util_BuildSystemTools_Windows7
 *
 * \see \ref ToolBOS_Util_BuildSystemTools_WindowsFAQ
 * \see \ref ToolBOS_Util_BuildSystemTools_Execution
 * \see \ref ToolBOS_Util_BuildSystemTools_Unittesting
 *
 * \htmlonly
 * </div>
 * \endhtmlonly
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_WindowsFAQ FAQ (Windows)
 *
 * <h2>cl.exe not found</h2>
 *
 * <b>Error message:</b>
 * \code
 * wine: could not load L"C:\\windows\\system32\\cl.exe": Module not found
 * \endcode
 * or:
 * \code
 * wine: cannot find L"C:\\windows\\system32\\cl.exe"
 * \endcode
 *
 * <b>Solution:</b>
 * This happens if the symlink ${HOME}/.wine/drive_c/msvc-sdk is broken.
 * For example it was pointing to a proxy or SIT build that has been
 * (re-)moved.
 *
 * In rare cases the package name and/or version of the MSVC compiler
 * could have been changed so that the link gets broken.
 *
 * <h2>Include files and/or libraries not found</h2>
 *
 * If you get errors that header files or libraries are not found then
 * check that NO link to your home directory is present within
 * ${HOME}/.wine/dosdrives as this typically results in path conflicts.
 *
 * The directory should look like this:
 * \code
 * $ ls -ahl ~/.wine/dosdevices/
 * total 8.0K
 * drwxr-xr-x 2 mstein bstasc 4.0K Jun 13 13:35 .
 * drwxr-xr-x 4 mstein bstasc 4.0K Jul 25 14:21 ..
 * lrwxrwxrwx 1 mstein hriasc   10 Jun 13 13:35 c: -> ../drive_c
 * lrwxrwxrwx 1 mstein hriasc    1 Jun 13 13:35 z: -> /
 * \endcode
 *
 * <h2>Cannot open compiler intermediate file</h2>
 *
 * <b>Error message:</b>
 * \code
 * c1 : fatal error C1083: Cannot open compiler intermediate file:
 * 'c:\temp\_CL_f395d08bex': No such file or directory
 * \endcode
 *
 * <b>Solution:</b>
 * Your Wine configuration apparently lacks the typical Windows directory
 * for temporary files. Please create it:
 *
 * \code
 * $ mkdir ~/.wine/drive_c/temp
 * \endcode
 *
 * <h2>Cannot execute the specified program</h2>
 *
 * <b>Error message:</b>
 * \code
 * The system cannot execute the specified program
 * \endcode
 *
 * <b>Solution:</b>
 * Please install the Microsoft Visual Studio Runtime Libraries v.2008
 * (mind the 2008 version, 2005 doesn't work).
 *
 * <h2>MSVCR90.dll can't be found</h2>
 *
 * <b>Error message:</b>
 * \code
 * MSVCR90.dll can't be found
 * \endcode
 *
 * <b>Solution:</b>
 * Create the following manifest file:
 * \code
 * <?xml version='1.0' encoding='UTF-8' standalone='yes'?>
 * <assembly xmlns='urn:schemas-microsoft-com:asm.v1' manifestVersion='1.0'>
 *   <dependency>
 *     <dependentAssembly>
 *       <assemblyIdentity type='win32'
 *                         name='Microsoft.VC90.CRT'
 *                         version='9.0.21022.8'
 *                         processorArchitecture='x86'
 *                         publicKeyToken='1fc8b3b9a1e18e3b' />
 *     </dependentAssembly>
 *   </dependency>
 * </assembly>
 * \endcode
 * Then add this file to the Visual Studio project file
 * (Project -> Properties -> Configuration Properties -> Manifest Tool ->
 * Input and Output -> Additional Manifest Files). Then recompile the
 * package.
 *
 * <h2>C99 compliance</h2>
 *
 * Note that MSVC is not fully C99 compliant. Especially you will need to
 * put variables at the beginning of a code block.
 *
 * <b>Wrong (C99 standard, will not work with MSVC):</b>
 * \code
 * int myFunction( int x )
 * {
 *   int result = 0;
 *
 *   // ...do something...
 *
 *   for( int i = 0; i <= x; i++ )
 *   {
 *     // ...do something else...
 *   }
 *
 *   return result;
 * }
 * \endcode
 *
 * <b>Correct (C89 standard, MSVC compliant):</b>
 * \code
 * int myFunction( int x )
 * {
 *   int result = 0;
 *   int i      = 0;
 *
 *   // ...do something...
 *
 *   for( i = 0; i <= x; i++ )
 *   {
 *     // ...do something else...
 *   }
 *
 *   return result;
 * }
 * \endcode
 *
 * <h2>Path delimiter in Wine vs. native Windows</h2>
 *
 * There is a difference when executing (not compiling!) using Wine under
 * Linux, compared to executing on Windows:
 *
 * The FileSystem library (part of ToolBOSCore) has a constant called
 * \c FILESYSTEM_LINE_DELIMITER which evaluates to \c \\n on Linux and to
 * \c \\r\\n on Windows. When running a test program with Wine it is possible
 * that a file on Linux is expected to have lines terminating with \c \\r\\n
 * which is not valid for the underlying host operating system.
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_WindowsXP VS2010 on WinXP (console)
 *
 * \image html Logos/BST-small.png
 *
 * <h2>1. Have SIT available on Windows</h2>
 *
 * For a quickstart we expect to have the SIT network share mapped to drive
 * letter \c S:\ .
 *
 * You can map network drives under "MyComputer" → "Tools" →
 * "Map network drive".
 *
 * \image html BuildSystemTools/MapNetworkDrive-WinXP.png
 *
 * <h2>2. Step into package</h2>
 *
 * Open a console (cmd.exe) and navigate to your package.
 *
 * \image html BuildSystemTools/TopLevelDirectory-WinXP.png
 *
 * <h2>3. Launch build script</h2>
 *
 * Run \c buildVS2010.bat. This script auto-detects the CPU architecture
 * (32 / 64 bit), prepares the environment and then invokes \c BST.py.
 *
 * \image html BuildSystemTools/RunWindowsBuildScript-WinXP.png
 *
 * \image html BuildSystemTools/VisualStudio2010-WinXP.png
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_Windows7 VS2012 on Win7
 *
 * \image html Logos/BST-small.png
 *
 * <h2>1. Have SIT available on Windows</h2>
 *
 * For a quickstart we expect to have the SIT network share mapped to drive
 * letter \c S:\ .
 *
 * You can map network drives under "Start" → "Computer" → "Map network
 * drive".
 *
 * \image html BuildSystemTools/MapNetworkDrive-Win7.png
 *
 * <h2>2. Step into package</h2>
 *
 * Open a console (cmd.exe) and navigate to your package.
 *
 * \image html BuildSystemTools/TopLevelDirectory-Win7.png
 *
 * <h2>3. Launch build script</h2>
 *
 * Run \c buildVS2012.bat. This script auto-detects the CPU architecture
 * (32 / 64 bit), prepares the environment and then invokes \c BST.py.
 *
 * \image html BuildSystemTools/RunWindowsBuildScript-Win7.png
 *
 * \image html BuildSystemTools/VisualStudio2012-Win7.png
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_WindowsManually VS2010 on WinXP (IDE)
 *
 * \image html Logos/BST-small.png
 *
 * <h2>1. Have SIT available on Windows</h2>
 *
 * For a quickstart we expect to have the SIT network share mapped to drive
 * letter \c S:\ .
 *
 * You can map network drives under "MyComputer" → "Tools" →
 * "Map network drive".
 *
 * \image html BuildSystemTools/MapNetworkDrive-WinXP.png
 *
 * <h2>2. Step into package</h2>
 *
 * Open a console (cmd.exe) and navigate to your package.
 *
 * \image html BuildSystemTools/TopLevelDirectory-WinXP.png
 *
 * <h2>3. Launch package configuration</h2>
 *
 * Run \c buildVS2010.bat with "-c" parameter. This script auto-detects the
 * CPU architecture (32 / 64 bit), prepares the environment and then invokes
 * <tt>BST.py --setup</tt>.
 *
 * This will result in a Visual Studio project file ("solution").
 *
 * \image html BuildSystemTools/RunWindowsBuildScript-SetupOnly.png
 *
 * <h2>4. Open the Visual Studio solution-file (*.sln)</h2>
 *
 * \image html BuildSystemTools/VisualStudioSolutionFile.png
 * \image html BuildSystemTools/VisualStudioOpenDialog.png
 *
 * <h2>5. Switch to "release" mode and press build button</h2>
 *
 * \image html BuildSystemTools/VisualStudioSwitchToRelease.png
 *
 * \image html BuildSystemTools/VisualStudioRunButton.png
 *
 * \image html BuildSystemTools/VisualStudioBuild.png
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_CheatSheet CMakeLists.txt + packageVar.cmake
 *
 * <h2>Dependencies</h2>
 *
 * For each library to use from the SIT, put one include statement into your
 * CMakeLists.txt:
 *
 * \verbatim
   bst_find_package(DevelopmentTools/ToolBOSCore/3.3)
   bst_find_package(Libraries/MasterClock/1.6)
   \endverbatim
 *
 * <h2>Additional paths + flags</h2>
 *
 * If you need to specify the include- and/or library paths for the compiler,
 * and also settings such as CFLAGS, you have to edit the \c CMakeLists.txt file:
 *
 * \verbatim
   # additional location for headerfiles:
   include_directories($ENV{SIT}/Libraries/MasterClock/1.6/include)

   # additional location for libraries:
   link_directories($ENV{SIT}/Libraries/MasterClock/1.6/lib/$ENV{MAKEFILE_PLATFORM})

   # additional libraries to link (without "lib" prefix and filename extension):
   list(APPEND BST_LIBRARIES_SHARED MasterClock)

   # additional compiler defines:
   add_definitions(-D_POSIX_C_SOURCE=199506L -D__USE_XOPEN -D__USE_GNU)

   # additional compiler flags
   set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -ggdb")
   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -ggdb")
   \endverbatim
 *
 * <h2>External libraries</h2>
 *
 * If you want to use a library \a libExternal.so which is located in
 * /usr/local/External/lib, please specify this path in your CMakeLists.txt:
 *
 * \verbatim
   link_directories(/usr/local/External/lib)
   list(APPEND BST_LIBRARIES_SHARED External)
   \endverbatim
 *
 * <h2>Frequently asked</h2>
 *
 * <table>
 *
 * <tr>
 *   <th colspan="2">Defining targets</th>
 * </tr>
 * <tr>
 *   <td>building libraries</td>
 *   <td><tt>file(GLOB SRC_FILES src/*.c src/*.cpp)<br/>
 *           bst_build_libraries("${SRC_FILES}" "${PROJECT_NAME}"
 *           "${BST_LIBRARIES_SHARED}")</tt></td>
 * </tr>
 * <tr>
 *   <td>building an executable</td>
 *   <td><tt>file(GLOB FOO_FILES bin/Foo*.c)<br/>
 *           bst_build_executable(Foo "${FOO_FILES}"
 *           "${BST_LIBRARIES_SHARED}")</tt></td>
 * </tr>
 * <tr>
 *   <td>building a set of executables</td>
 *   <td><tt>file(GLOB FOO_FILES bin/Foo*.c)<br/>
 *           bst_build_executables("${FOO_FILES}"
 *           "${BST_LIBRARIES_SHARED}")</tt></td>
 * </tr>
 * <tr>
 *   <th colspan="2">Including dependencies</th>
 * </tr>
 * <tr>
 *   <td>add dependency to package</td>
 *   <td><tt>bst_find_package(Libraries/Foo/1.0)</tt></td>
 * </tr>
 * <tr>
 *   <th colspan="2">Build settings</th>
 * </tr>
 * <tr>
 *   <td>add include path</td>
 *   <td><tt>include_directories(dir1 dir2 ...)</tt></td>
 * </tr>
 * <tr>
 *   <td>add linker path</td>
 *   <td><tt>link_directories(dir1 dir2 ...)</tt></td>
 * </tr>
 * <tr>
 *   <td>link against libraries</td>
 *   <td><tt>list(APPEND BST_LIBRARIES_SHARED foo bar)</tt></td>
 * </tr>
 * <tr>
 *   <td>compiler definitions</td>
 *   <td><tt>add_definitions(-DFOO -ggdb)</tt></td>
 * </tr>
 * <tr>
 *   <td>force C++ compiler on *.c file</td>
 *   <td><tt>set_source_files_properties(filename.c PROPERTIES
 *                                                  LANGUAGE CXX)</tt></td>
 * </tr>
 * <tr>
 *   <td>add C compiler flags</td>
 *   <td><tt>set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -ggdb -fPIC")</tt></td>
 * </tr>
 * <tr>
 *   <td>add C++ compiler flags</td>
 *   <td><tt>set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")</tt></td>
 * </tr>
 * <tr>
 *   <th colspan="2">CMake variables</th>
 * </tr>
 * <tr>
 *   <td>define a variable</td>
 *   <td><tt>set(MYVAR a)            # one element<br/>
 *           set(MYVAR "a b c d e")  # one element (string)<br/>
 *           set(MYVAR a b c d e)    # five elements</tt></td>
 * </tr>
 * <tr>
 *   <td>environment variables</td>
 *   <td><tt>$ENV{VARNAME}</tt></td>
 * </tr>
 * <tr>
 *   <td>list of libraries to link</td>
 *   <td><tt>${BST_LIBRARIES_SHARED}</tt></td>
 * </tr>
 * <tr>
 *   <td>top-level directory</td>
 *   <td><tt>${CMAKE_HOME_DIRECTORY}</tt></td>
 * </tr>
 * <tr>
 *   <td>package name</td>
 *   <td><tt>${PACKAGE_NAME}</tt></td>
 * </tr>
 * <tr>
 *   <td>package version</td>
 *   <td><tt>${PACKAGE_VERSION}</tt></td>
 * </tr>
 * <tr>
 *   <th colspan="2">Conditions</th>
 * </tr>
 * <tr>
 *   <td>check for native Windows host</td>
 *   <td><tt>if(WINDOWS)<br/>...<br/>else()<br/>...<br/>endif()</tt></td>
 * </tr>
 * <tr>
 *   <td>check for particular platform</td>
 *   <td><tt>if("$ENV{MAKEFILE_PLATFORM}" STREQUAL "windows-amd64-vs2012")<br/>...<br/>else()<br/>...<br/>endif()</tt></td>
 * </tr>
 * </table>
 *
 * \see http://www.cmake.org/cmake/help/documentation.html
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_MultiPlatform Multi-platform support
 *
 * \image html Logos/BST-small.png
 *
 * When writing platform-specific code please use those defines within
 * preprocessor directives (they are automatically set by \c BST.py):
 *
 * <b>Operating systems:</b>
 * \li <pre>__linux__</pre>
 * \li <pre>__windows__</pre>
 * \li <pre>__win32__</pre>
 * \li <pre>__win64__</pre>
 *
 * <b>Compilers:</b>
 * \li <pre>__gcc__</pre>
 * \li <pre>__msvc__</pre>
 *
 * <b>Processor architectures:</b>
 * \li <pre>__32BIT__</pre>
 * \li <pre>__64BIT__</pre>
 * \li <pre>__arm__</pre>
 * \li <pre>__armv7__</pre>
 *
 * <h3>Example</h3>
 *
 * \code
   #if defined(__linux__)
      [... Linux code ...]
   #endif

   #if defined(__windows__) && !defined(__msvc__)
      [... Non-MSVC Windows code ...]
   #endif
   \endcode
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_CrossCompiling Cross-compiling
 *
 * \image html BST-small.png
 *
 * \note In case of Linux-to-Windows cross-compilation it means executing the
 *       compiler and linker from Microsoft Visual Studio under Linux, using
 *       the Wine framework. Thus these are the same executables in both
 *       environments. The generated binaries do not link against any emulation
 *       layer or helper libraries.
 *
 * <h2>GUI usage</h2>
 *
 * Go to the top-level directory of your package and start the
 * \ref ToolBOS_Util_BuildSystemTools_ZenBuildMode. Within the GUI select the
 * desired platform(s) to build for and press the \c Build button.
 *
 * \code
   $ cd MyPackage/1.0

   $ BST.py -z
   \endcode
 *
 * \image html BuildSystemTools/ZenBuildMode-800x487.png
 *
 * <h2>Command-line usage</h2>
 *
 * To compile for a different platform invoke \c BST.py with the \c -p
 * parameter and the target platform name. The names of supported platforms
 * can be listed using "-p help" or found here:
 * \ref ToolBOS_Setup_Platforms
 *
 * <h3>Example:</h3>
 *
 * \verbatim
   $ cd Example/1.6

   $ BST.py -p windows-amd64-vs2012
   [BST.py:532 INFO] targetPlatform=windows-amd64-vs2012
   -- The C compiler identification is MSVC 17.0.50727.1
   -- The CXX compiler identification is MSVC 17.0.50727.1
   -- Check for working C compiler: /home/mstein/.HRI/sit/latest/DevelopmentTools/ToolBOSPluginWindows/1.2/bin/cl
   -- Check for working C compiler: /home/mstein/.HRI/sit/latest/DevelopmentTools/ToolBOSPluginWindows/1.2/bin/cl -- works
   -- Detecting C compiler ABI info
   -- Detecting C compiler ABI info - done
   -- Check for working CXX compiler: /home/mstein/.HRI/sit/latest/DevelopmentTools/ToolBOSPluginWindows/1.2/bin/cl
   -- Check for working CXX compiler: /home/mstein/.HRI/sit/latest/DevelopmentTools/ToolBOSPluginWindows/1.2/bin/cl -- works
   -- Detecting CXX compiler ABI info
   -- Detecting CXX compiler ABI info - done

   Top-level directory:    /home/mstein/Example/1.6
   Package name:           Example
   Package full version:   1.6
   Major version:          1
   Minor version:          6
   CMake generator:        Unix Makefiles
   including package:      sit://DevelopmentTools/ToolBOSCore/3.3
   including package:      sit://Libraries/MasterClockCore/1.2
   -- Configuring done
   -- Generating done
   -- Build files have been written to: /home/mstein/Example/1.6/build/windows-amd64-vs2012
   Scanning dependencies of target Example-global

   [...]

   [100%] Building C object CMakeFiles/ExampleClient.dir/bin/ExampleClient.c.obj
   ExampleClient.c
   Linking C executable ../../bin/windows-amd64-vs2012/ExampleClient.exe
   [100%] Built target ExampleClient
   \endverbatim
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_Installation Installation
 *
 * \image html Logos/BST-small.png
 *
 * <h2>Usage</h2>
 *
 * The build system distinguishes between installing into a proxy and into
 * the main SIT. It also supports creating a tarball only (no installation).
 *
 * \see \ref ToolBOS_Concept_SIT
 * \see \ref ToolBOS_Concept_ProxyDir
 *
 * <table>
 * <tr>
 *   <th>command</th>
 *   <th>description</th>
 * </tr>
 * <tr>
 *   <td>BST.py -x</td>
 *   <td>installing into the user's SIT sandbox ("proxy directory") without
 *       altering the global installation, should be used while
 *       testing/debugging</td>
 * </tr>
 * <tr>
 *   <td>BST.py -i</td>
 *   <td>installing into the global SIT (official release)
 *       SIT</td>
 * </tr>
 * <tr>
 *   <td>BST.py -r</td>
 *   <td>create a tarball only (no installation)</td>
 * </tr>
 * <tr>
 *   <td>BST.py -U</td>
 *   <td>uninstall, see \ref ToolBOS_Util_BuildSystemTools_Uninstalling </td>
 * </tr>
 * </table>
 *
 * <h2>Install custom files/directories</h2>
 *
 * If you need to install more files than would automatically be detected,
 * you can specify them in the \c pkgInfo.py file.
 *
 * <h3>Install files/directories [recursively]</h3>
 *
 * This recursively installs the 3 directories "external, "etc" and "include"
 * from your source tree into the installation tree of your package.
 *
 * \code
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
   \endcode
 *
 * <h3>Install files/directories [recursively], with different destination</h3>
 *
 * If the destination shall be different, turn such a string-element into a
 * tuple of (source dir.,destination dir.).
 *
 * Same as above, except that 'external' will get installed as '3rdParty':
 *
 * \code
   install          = [ ( 'external', '3rdParty' ),           # tuple of (src,dst)
                        'etc',                                # src == dst
                        'include' ]                           # src == dst
   \endcode
 *
 * <h3>Install files/directories matching regular expression</h3>
 *
 * To install only those files matching a certain regexp, use the
 * copyMatching() function instead. Each element in the list must be a tuple
 * of (source dir.,regular expression).
 *
 * This installs all Java examples:
 *
 * \code
   installMatching  = [ ( 'examples', '\.java' ) ]            # (srcDir,regexp)
   \endcode
 *
 * <h3>Install files/directories matching regular expression, with different
 * destination</h3>
 *
 * Tuples might contain three elements in case the destination directory
 * shall be different.
 *
 * If Java examples were to be installed into a destination directory 'HowTo'
 * instead, the code would look like:
 * \code
   installMatching  = [ ( 'examples', '\.java', 'HowTo' ) ]   # (srcDir,regexp,dstDir)
   \endcode
 *
 * <h3>Installing symlinks</h3>
 *
 * To create a symlink during installation, put the following list of tuples
 * in your \c pkgInfo.py . Each tuple contains two elements (target, symlink).
 *
 * \code
   installSymlinks  = [ ( 'windows-amd64-vs2010',             # target
                          'windows-amd64-vs2012' ) ]          # symlink
   \endcode
 *
 * This creates a symlink within the installation directory. The symlink is
 * named "windows-amd64-vs2012" (2nd element) pointing to
 * "windows-amd64-vs2010" (1st element).
 *
 * Both elements may contain subdirectory pathnames.
 *
 * <h3>Setting ownership of files</h3>
 *
 * You can specify a particular group to whom the installed files shall belong:
 *
 * \code
   installGroup     = 'users'                                 # group name
   \endcode
 *
 * and also the umask-settings (permission modes), e.g.:
   \code
   installUmask     = '0002'                                  # group-writeable, world-readable
   \endcode
 *
 * <h2>Toggle incremental / clean-install mode</h2>
 *
 * \c BST.py defaults to performing incremental installations, this means
 * existing files won't be deleted prior to installing the new files.
 * This allows sequential installation for multiple platforms.
 *
 * The drawback is that files that in the meanwhile have been deleted from
 * the codebase, persist in the installation and eventually disturb.
 *
 * Please select an appropriate way and put either of the following settings
 * in your pkgInfo.py.
 *
 * <h3>Solution A: use patchlevel-installations (3-digit versions)</h3>
 *
 * \verbatim
   usePatchlevels   = True

   patchlevel       = 123                                     # default: SVN revision
   \endverbatim
 *
 * <h3>Solution B: clean existing installation</h3>
 *
 * \verbatim
   installMode      = 'clean'                                 # default: 'incremental'
   \endverbatim
 *
 *
 * <h2>For the experts: Install hooks (Python)</h2>
 *
 * You may implement any of the following Python functions in your
 * \c pkgInfo.py in order to manually extend the installation procedure.
 *
 * \li \c Install_onStartupStage1
 * \li \c Install_onExitStage1
 * \li \c Install_onStartupStage2
 * \li \c Install_onExitStage2
 * \li \c Install_onStartupStage3
 * \li \c Install_onExitStage3
 * \li \c Install_onStartupStage4
 * \li \c Install_onExitStage4
 * \li \c Install_onStartupStage5
 * \li \c Install_onExitStage5
 *
 * \code
    from ToolBOSCore.Util import FastScript

    def Install_onStartupStage2( self ):
        """
            Custom extension of install procedure.
        """
        logging.info( "Hello, World!" )
        logging.info( "packageName=%s", self.details.packageName )

        FastScript.execProgram( "myHelperProgram" )
   \endcode
 *
 * This hook function will be executed by the installation procedure at the
 * beginning of stage 2, f.i.:
 *
 * \verbatim
   [...]
   STAGE 2 # AUTO-GENERATING FILES

   [<string>:126 INFO] Hello, World!
   [<string>:127 INFO] packageName=MyPackage
   [...output of myHelperProgram...]
   [PackageCreator.py:966 INFO] cp BashSrc ./install/
   [PackageCreator.py:978 INFO] cp CmdSrc.bat ./install/
   [...]
   \endverbatim
 *
 * <h2>For the experts: Install hooks (Bash)</h2>
 *
 * As alternative to implementing Pythonic install hooks (see above) you can
 * write small shellscripts that will be executed during the install
 * procedure. They have to be located in the top-level directory of your
 * package and must be named:
 *
 * <h3>most relevant:</h3>
 * \li \c preInstallHook.sh (executed just before copying)
 * \li \c installHook.sh (this is the file you most probably look for)
 * \li \c postInstallHook.sh (executed after copying all files)
 *
 * <h3>for special cases, symmetric to the Python functions above:</h3>
 * \li \c Install_onStartupStage1.sh
 * \li \c Install_onExitStage1.sh
 * \li \c Install_onStartupStage2.sh
 * \li \c Install_onExitStage2.sh
 * \li \c Install_onStartupStage3.sh
 * \li \c Install_onExitStage3.sh
 * \li \c Install_onStartupStage4.sh
 * \li \c Install_onExitStage4.sh
 * \li \c Install_onStartupStage5.sh
 * \li \c Install_onExitStage5.sh
 *
 * Most common use case is to call the install routine of a 3rd party software
 * from our install procedure. To achieve this you would create a shellscript
 * \c installHook.sh looking similar to this:
 *
 * \verbatim
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
\endverbatim
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_Uninstalling Uninstalling
 *
 * Easily drop a package from Proxy- and Global-SIT and delete any DTBOS or
 * RTMaps registration entries (if applicable):
 *
 * \verbatim
   $ cd MyPackage/1.0

   $ BST.py --uninstall
   \endverbatim
 *
 * <h3>Parameters:</h3>
 *
 * <table>
 * <tr>
 *   <th>command</th>
 *   <th>description</th>
 * </tr>
 * <tr>
 *   <td>BST.py -U</td>
 *   <td>uninstall a package from both Proxy- and Global-SIT</td>
 * </tr>
 * <tr>
 *   <td>BST.py -Ux</td>
 *   <td>uninstall a package from Proxy-SIT only, leave Global-SIT
 *       untouched</td>
 * </tr>
 * </table>
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_CustomScripts Custom scripts for compilation + installation
 *
 * \image html Logos/BST-small.png
 *
 * BST.py searches for scripts that *entirely replace* the default compile-
 * resp. install procedures. If present, they get executed in behalf of
 * the standard procedure.
 *
 * <center>
 * \image html BuildSystemTools/BuildSystemTools-Timeline.png
 * <i>script execution when invoked within Nightly Build:
 * pre/post-&lt;stepName&gt;.sh scripts only once, and the
 * &lt;stepName&gt;.sh once per supported platform</i>
 * </center>
 *
 * \note Wherever the filename extension \c .sh (on Linux) is mentioned,
 *       the same applies for \c .bat on Windows. So you can provide e.g. both
 *       \c unittest.sh and \c unittest.bat on Windows
 *
 * The following stepNames are supported:
 * \li configure
 * \li compile
 * \li install
 * \li distclean
 * \li unittest
 *
 * <h3>Replacing the install procedure</h3>
 *
 * When writing a custom \c install.sh script you may call the tools'
 * native install procedure. However toolchains such as GNU Autotools
 * do not know about our proxy directories. Even more they may need to
 * pass the install location to the \c ./configure script and then the
 * final install location may get compiled into the executable ("rpath").
 *
 * In order to test the installation of such packages set the environment
 * variable \c DRY_RUN to \c TRUE before compiling. This way the install
 * location gets prefixed by \c /tmp . Then you can safely test the
 * installation of the package without actually altering the SIT.
 * Yes, this is only a sub-optimal workaround :-/ Please propose better
 * alternatives.
 *
 * <h3>Writing unittests</h3>
 *
 * see \ref ToolBOS_Util_BuildSystemTools_Unittesting
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_pkgInfo pkgInfo.py
 *
 * <img src="../Logos/redhat-system_settings-256x256.png" align="right">
 *
 * A \c pkgInfo.py file might be present in a package, both in VCS and/or in
 * the SIT.
 *
 * \li If such file exists within a source package (f.i. in VCS) it is used
 *     to configure the behavior of \c BST.py. Thus it typically is handcrafted.
 *
 * \li Each package installed in the SIT should have a \c pkgInfo.py file
 *     containing meta-information, such as location of VCS repository
 *     or current maintainer. These information are used e.g. by the
 *     CIA (aka Nightly Build) system. Such files are
 *     typically auto-generated at install time.
 *
 * \note A \c pkgInfo.py file may contain arbitrary Python code. If necessary
 *       you could even import packages to calculate some values.
 *
 * <h2>Recognized keywords</h2>
 *
 * The file is organized as key-value-pair assignments. However, you may use
 * any code to do such assignments. At loading time the Python code gets
 * evaluated and the following variables are searched:
 *
 * <table>
 * <tr>
 *   <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
 *       colspan="3">package meta info</td>
 * </tr>
 * <tr>
 *      <td><tt>name</tt></td>
 *      <td>string</td>
 *      <td>name of the package</td>
 * </tr>
 * <tr>
 *      <td><tt>version</tt></td>
 *      <td>string</td>
 *      <td>version number of the package</td>
 * </tr>
 * <tr>
 *      <td><tt>category</tt></td>
 *      <td>string</td>
 *      <td>category of the package (eg.: Development tools,
 *          Application or External etc.)</td>
 * </tr>

 * <tr>
 *   <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
 *       colspan="3">package interrelationship</td>
 * </tr>
 * <tr>
 *      <td><tt>depends</tt></td>
 *      <td>list of strings</td>
 *      <td>direct dependencies required by this package (for both building
 *          and execution), in canonical package notation</td>
 * </tr>
 * <tr>
 *      <td><tt>dependsArch</tt></td>
 *      <td>dict { string: list of strings }</td>
 *      <td>plaform-specific dependencies can be stored in this dictionary,
 *          e.g. { 'trusty64': [ 'deb://openjdk-7-jdk' ] }</td>
 * </tr>
 * <tr>
 *      <td><tt>buildDepends</tt></td>
 *      <td>list of strings</td>
 *      <td>direct dependencies required for building this package, in
 *          canonical package notation</td>
 * </tr>
 * <tr>
 *      <td><tt>buildDependsArch</tt></td>
 *      <td>dict { string: list of strings }</td>
 *      <td>plaform-specific build-dependencies can be stored in this
 *          dictionary, e.g. { 'trusty64': [ 'deb://gcc-4.8' ] }</td>
 * </tr>
 * <tr>
 *      <td><tt>recommended</tt></td>
 *      <td>list of strings</td>
 *      <td>packages often found / used together with this one, without
 *          a hard dependency on it, in canonical package notation</td>
 * </tr>
 * <tr>
 *      <td><tt>suggests</tt></td>
 *      <td>list of strings</td>
 *      <td>packages which might be of interest to users of this one</td>
 * </tr>
 *
 * <tr>
 *   <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
 *       colspan="3">compilation</td>
 * </tr>
 * <tr>
 *      <td><tt>BST_useClang</tt></td>
 *      <td>bool</td>
 *      <td>enable / disable the usage of Clang/LLVM for compiling C/C++ code</td>
 * </tr>
 *
 * <tr>
 *   <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
 *       colspan="3">distclean</td>
 * </tr>
 * <tr>
 *      <td><tt>delete</tt></td>
 *      <td>list of strings</td>
 *      <td>additional file patterns to be deleted (apart from default patterns),
 *          see \ref ToolBOS_Util_BuildSystemTools_Cleaning</td>
 * </tr>
 * <tr>
 *      <td><tt>doNotDelete</tt></td>
 *      <td>list of strings</td>
 *      <td>file patterns from the default set of patterns which shall be kept
 *          see \ref ToolBOS_Util_BuildSystemTools_Cleaning</td>
 * </tr>
 * <tr>
 *   <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
 *       colspan="3">Software Quality settings</td>
 * </tr>
 * <tr>
 *      <td><tt>sqLevel</tt></td>
 *      <td>string</td>
 *      <td>targeted SQ level, e.g. 'advanced',
 *          see \ref ToolBOSCore.SoftwareQuality.Common.sqLevelNames </td>
 * </tr>
 * <tr>
 *      <td><tt>sqOptInRules</tt></td>
 *      <td>list of strings</td>
 *      <td>list of SQ rules to be explicitly enabled,
 *          e.g. [ 'C15', 'C16' ]</td>
 * </tr>
 * <tr>
 *      <td><tt>sqOptOutRules</tt></td>
 *      <td>list of strings</td>
 *      <td>list of SQ to be explicitly disabled (please leave comment why),
 *          e.g. [ 'C04', 'C05' ]</td>
 * </tr>
 * <tr>
 *      <td><tt>sqOptInDirs</tt></td>
 *      <td>list of strings</td>
 *      <td>list of directories (relative paths) to be explicitly included
 *          in check, e.g. [ 'src' ]</td>
 * </tr>
 * <tr>
 *      <td><tt>sqOptOutDirs</tt></td>
 *      <td>list of strings</td>
 *      <td>list of directories (relative paths) to be explicitly excluded
 *          from check, e.g. [ 'external', '3rdParty' ]</td>
 * </tr>
 * <tr>
 *      <td><tt>sqOptInFiles</tt></td>
 *      <td>list of strings</td>
 *      <td>list of files (relative paths) to be explicitly included
 *          in check, e.g. [ 'helper.cpp' ]</td>
 * </tr>
 * <tr>
 *      <td><tt>sqOptOutFiles</tt></td>
 *      <td>list of strings</td>
 *      <td>list of files (relative paths) to be explicitly excluded
 *          from check, e.g. [ 'src/autoGeneratedWrapper.cpp' ]</td>
 * </tr>
 * <tr>
 *      <td><tt>sqComments</tt></td>
 *      <td>dict { string: list of strings }</td>
 *      <td>comments + annotations to SQ rules, e.g. why opt-in/out or
 *          justification why a rule cannot be fulfilled</td>
 * </tr>
 * <tr>
 *      <td><tt>sqCheckExe</tt></td>
 *      <td>list of strings</td>
 *      <td>paths to the executables, including arguments (if any), that
 *          shall be analyzed by the valgrind check routine</td>
 * </tr>
 * <tr>
 *   <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
 *       colspan="3">documentation</td>
 * </tr>
 * <tr>
 *      <td><tt>docTool</tt></td>
 *      <td>string</td>
 *      <td>force particular documentation tool ("doxygen", "matdoc"), or
 *          disable documentation creation using an empty string ("")</td>
 * </tr>
 * <tr>
 *   <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
 *       colspan="3">installation procedure</td>
 * </tr>
 * <tr>
 *      <td><tt>install</tt></td>
 *      <td>list of tuples</td>
 *      <td>additional files/directories to install,
 *          see \ref ToolBOS_Util_BuildSystemTools_Installation </td>
 * </tr>
 * <tr>
 *      <td><tt>installMatching</tt></td>
 *      <td>list of tuples</td>
 *      <td>additional files/directories to install,
 *          see \ref ToolBOS_Util_BuildSystemTools_Installation </td>
 * </tr>
 * <tr>
 *      <td><tt>installSymlink</tt></td>
 *      <td>list of tuples</td>
 *      <td>symlinks to be created at install time,
 *          see \ref ToolBOS_Util_BuildSystemTools_Installation </td>
 * </tr>
 * <tr>
 *      <td><tt>installMode</tt></td>
 *      <td>string</td>
 *      <td>"incremental": add files to previous installation (= default),
 *          "clean": wipe previous installation before installing</td>
 * </tr>
 * <tr>
 *      <td><tt>installGroup</tt></td>
 *      <td>string</td>
 *      <td>set group of installed files to specified group name, e.g.
 *          <tt>"users"</tt></td>
 * </tr>
 * <tr>
 *      <td><tt>installUmask</tt></td>
 *      <td>integer</td>
 *      <td>override user's umask-setting when installing packages, can be
 *          specified as decimal integer, octal integer, or string), e.g.:
 *          <tt>"0022"</tt> for permissions <tt>rwxr-xr-x</tt></td>
 * </tr>
 * <tr>
 *      <td><tt>usePatchlevels</tt></td>
 *      <td><tt>True</tt> or <tt>False</tt></td>
 *      <td>use 3-digit version scheme for installation, e.g. "1.0.123"
 *          (default: <tt>False</tt>)</td>
 * </tr>
 * <tr>
 *      <td><tt>patchlevel</tt></td>
 *      <td>integer</td>
 *      <td>number to use for last field in 3-digit version scheme,
 *          e.g. 123 to yield full version string "1.0.123"</td>
 * </tr>
 * <tr>
 *      <td><tt>linkAllLibraries</tt></td>
 *      <td>bool</td>
 *      <td>flag if CreateLibIndex for RTBOS shall consider all *.so files
 *          in the install directory, or only the main one named after the
 *          package</td>
 * </tr>
 * <tr>
 *      <td><tt>Install_on{Startup,Exit}Stage{1..5}</tt></td>
 *      <td>callable</td>
 *      <td>Python function to be executed at startup/exit of the
 *          corresponding stage 1..5</td>
 * </tr>
 * <tr>
 *   <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
 *       colspan="3">shellfiles customization</td>
 * </tr>
 * <tr>
 *      <td><tt>envVars</tt></td>
 *      <td>list of tuples</td>
 *      <td>environment variable assignments to put into auto-generated
 *          \c BashSrc and \c CmdSrc.bat files
 *
 *          each tuple (of two elements) contains a varName-value assignment
 *
 *          Note: this was not implemented as \c dict in order to preserve
 *          the list of appearance in the file</td>
 * </tr>
 * <tr>
 *      <td><tt>aliases</tt></td>
 *      <td>list of tuples</td>
 *      <td>command aliases to put into auto-generated
 *          \c BashSrc and \c CmdSrc.bat files
 *
 *          each tuple (of two elements) contains an alias-command assignment
 *
 *          Note: this was not implemented as \c dict in order to preserve
 *          the list of appearance in the file</td>
 * </tr>
 * <tr>
 *      <td><tt>bashCode</tt></td>
 *      <td>list of strings</td>
 *      <td>Bash code to be injected into auto-generated \c BashSrc files,
 *          line-wise</td>
 * </tr>
 * <tr>
 *      <td><tt>cmdCode</tt></td>
 *      <td>list of strings</td>
 *      <td>Windows \c cmd.exe code to be injected into auto-generated
 *          \c CmdSrc.bat files, line-wise</td>
 * </tr>
 * <tr>
 *   <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
 *       colspan="3">version control system</td>
 * </tr>
 * <tr>
 *      <td><tt>gitBranch</tt></td>
 *      <td>string</td>
 *      <td>Git branch name used for installation</td>
 * </tr>
 * <tr>
 *      <td><tt>gitCommitID</tt></td>
 *      <td>string</td>
 *      <td>Git commit ID</td>
 * </tr>
 * <tr>
 *      <td><tt>gitOrigin</tt></td>
 *      <td>string</td>
 *      <td>URL of Git blessed repository</td>
 * </tr>
 * <tr>
 *      <td><tt>gitRepoRelPath</tt></td>
 *      <td>string</td>
 *      <td>path of the files relative within the Git repository root</td>
 * </tr>
 * <tr>
 *      <td><tt>revision</tt></td>
 *      <td>string</td>
 *      <td>SVN revision number</td>
 * </tr>
 * <tr>
 *      <td><tt>revisionforCIA</tt></td>
 *      <td>string</td>
 *      <td>SVN revision which shall be build by CIA</td>
 * </tr>
 * <tr>
 *   <td style="background: #CCCCFF; text-align: center; font-weight: bold;"
 *       colspan="3">legacy settings</td>
 * </tr>
 * <tr>
 *      <td><tt>package</tt></td>
 *      <td>string</td>
 *      <td>name of the package (replaced by "name")</td>
 * </tr>
 * </table>
 * \endhtmlonly
 *
 * <h2>Example</h2>
 *
 * \code
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


   # explicitly state dependencies (otherwise extracted from CMakeLists.txt)

   depends       = [ 'sit://DevelopmentTools/ToolBOSCore/3.3',
                     'deb://libjpeg62' ]

   buildDepends  = [ 'sit://External/pthreads/1.0',
                     'deb://libjpeg-dev' ]



   # put environment variables + additional code into BashSrc/...

   envVars       = [ ( 'PATH', '${INSTALL_ROOT}/bin/${MAKEFILE_PLATFORM}:${PATH}' ),
                     ( 'LD_LIBRARY_PATH', '${INSTALL_ROOT}/lib/${MAKEFILE_PLATFORM}:${LD_LIBRARY_PATH}' ) ]

   bashCode      = [ 'echo "Hello, World!"' ]



   # well... it's possible ;-)

   import numpy

   patchlevel    = int( numpy.pi )


   # EOF
   \endcode
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_StaticLinking Static linking
 *
 * \image html Logos/BST-small.png
 *
 * When using static linking together with pthreads, the compile- and
 * targethosts have to have exactly matching glibc, otherwise leading to
 * strange segfaults.
 *
 * Therefore, when speaking in context of BST.py the term "static" linking of
 * executables is <b>actually wrong</b>: The HRI-EU and 3rd party libraries are
 * linked statically, but the executable still links dynamically against
 * essential system libraries (libc, pthread,...). True static compilation is
 * not possible as soon as <tt>dlopen()</tt> and friends (f.i. in
 * \c libToolBOSCore ) are needed.
 *
 *  Note that CMake supports true static linking of executables though.
 *
 * <h2>HowTo</h2>
 *
 * \li in your \c CMakeLists.txt, locate the line for building executables
 *     (\c bst_build_executable or \c bst_build_executables )
 * \li change the set of link libraries from
 *     \c BST_LIBRARIES_SHARED (= default) to \c BST_LIBRARIES_STATIC
 * \li <i>before</i> this line, add the switch to static link mode:
 *     <tt>set(BST_LINK_MODE STATIC)</tt>
 *
 * <b>Example:</b>
 *
 * \verbatim
   [...]

   #----------------------------------------------------------------------------
   # Build specification
   #----------------------------------------------------------------------------


   file(GLOB SRC_FILES src/*.c src/*.cpp)

   bst_build_libraries("${SRC_FILES}" "${PROJECT_NAME}" "${BST_LIBRARIES_SHARED}")


   file(GLOB EXE_FILES bin/*.c bin/*.cpp examples/*.c examples/*.cpp
                       test/*.c test/*.cpp)

   set(BST_LINK_MODE STATIC)
   bst_build_executables("${EXE_FILES}" "${BST_LIBRARIES_STATIC}")
   \endverbatim
 *
 * The resulting executable will link against essential libraries only (in
 * fact is a dynamically linked executable):
 *
 * \verbatim
   $ ldd test/precise64/unittest
        linux-vdso.so.1 =>  (0x00007fff12e2b000)
        librt.so.1 => /lib/x86_64-linux-gnu/librt.so.1 (0x00007fc41c3b4000)
        libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fc41c196000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fc41bdd6000)
        /lib64/ld-linux-x86-64.so.2 (0x00007fc41c5f5000)
   \endverbatim
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_Execution Executing applications
 *
 * <h2>Linux applications</h2>
 *
 * Executables are often using shared libraries, therefore they need to
 * know where those required files are located. On Linux/Unix the search
 * path for libraries is stored in the system variable $LD_LIBRARY_PATH
 * while for Windows it is $PATH.
 *
 * In order to properly setup the right path automatically, you may use
 * this script:
 * \verbatim
   RunFromSourceTree.sh ./examples/${MAKEFILE_PLATFORM}/ExampleProgram <arguments>
   \endverbatim
 *
 * <h2>Windows applications</h2>
 *
 * The easiest way to run an application with many libraries under Windows is
 * to collect all the *.exe and *.dll files into a single directory.
 *
 * Please refer to the Export Wizard documentation.
 *
 * <h2>Windows applications on Linux, using Wine</h2>
 *
 * With the "-p windows-amd64-vs2012" option you can execute Windows binaries on
 * Linux machines, using the <a href="http://www.winehq.org">Wine</a> framework.
 *
 * \verbatim
   $ RunFromSourceTree.sh -p windows-amd64-vs2012 test/windows-amd64-vs2012/testDataSet.exe
   [1266874888.373423 9:0 testDataSet.cpp:318 Info] base constructor sampling plan
   [1266874888.373423 9:0 testDataSet.cpp:326 Data] mNumDimensions=Dimension: 0
   [1266874888.373423 9:0 testDataSet.cpp:327 Data] mNumPoints=Points: 0
   [1266874888.373423 9:0 testDataSet.cpp:369 Info] class name: mySampling
   [1266874888.373423 9:0 testDataSet.cpp:391 Info] base init sampling plan
   [1266874888.373423 9:0 testDataSet.cpp:404 Data] mNumDimensions=Dimension: 5
   [1266874888.373423 9:0 testDataSet.cpp:405 Data] numSamples=Points: 100
   [...]
   \endverbatim
 *
 * \see \ref ToolBOS_HowTo_Debugging
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_Cleaning Cleaning
 *
 * \image html BST-small.png
 *
 * To remove binaries and auto-generated files from your package:
 * \verbatim
   $ BST.py -d
   \endverbatim
 *
 * or:
 *
 * \verbatim
   $ BST.py --distclean
   \endverbatim
 *
 * <h2>Customization</h2>
 *
 * To customize (opt-in / opt-out) file patterns that shall be deleted or not
 * upon 'BST.py -d', please create a file named \c pkgInfo.py within your
 * package's top-level directory (e.g. MyPackage/1.0/pkgInfo.py).
 *
 * <h3>Simple example</h3>
 *
 * \verbatim
   # also delete the following files:
   delete      = [ 'deleteMe.*\.txt' ]

   # do not delete the following files:
   doNotDelete = [ 'install/??shSrc' ]
   \endverbatim
 *
 * <h3>Complicated example</h3>
 *
 * The \c pkgInfo.py file may contain arbitrary Python code, e.g.:
 *
 * \code
   from ToolBOSCore.Platforms.Platforms import getPlatformNames

   platformList = getPlatformNames()


   # also delete the following files:

   delete = [ 'doc/man',
              'etc/mirror/*.log',
              'lib/*.jar',
              '*py.class' ]

   for item in ( 'foo', 'bar', 'baz' ):
        for platform in platformList:
            delete.append( '%s/%s' % ( item, platform ) )
   \endcode
 * \see \ref ToolBOS_Util_BuildSystemTools_pkgInfo
 */


/*!
 * \page ToolBOS_Util_BuildSystemTools_Variables Environment variables
 *
 * \image html Logos/BST-small.png
 *
 * <table>
 * <tr>
 *   <th>environment variable</th>
 *   <th>description</th>
 * </tr>
 * <tr>
 *   <td colspan="2" bgcolor="#CCCCFF"><center><b>User settings
 *       (e.g. in scripts or interactive shells)</b></center></td>
 * </tr>
 * <tr>
 *   <td><tt>export BST_BUILD_JOBS=NUM</tt></td>
 *   <td>number of parallel jobs, can also be specified using
 *       <tt>BST.py -j NUM</tt></td>
 * </tr>
 * <tr>
 *   <td><tt>export BST_CMAKE_OPTIONS="..."</tt></td>
 *   <td>additional parameters to pass to CMake, e.g. <tt>--trace</tt></td>
 * </tr>
 * <tr>
 *   <td><tt>export BST_INSTALL_PREFIX=/path/to/SIT</tt></td>
 *   <td>install package to different path (e.g. /tmp), mostly useful for
 *       testing external software</td>
 * </tr>
 * <tr>
 *   <td><tt>export BST_SKIP_SCRIPTS=TRUE</tt></td>
 *   <td>do not execute custom build scripts such as \c compile.sh (used to
 *       avoid recursion when called from within \c compile.sh)</td>
 * </tr>
 * <tr>
 *   <td><tt>export BST_USE_ICECC=TRUE</tt></td>
 *   <td>explicitly force usage of IceCC distributing compiler on Linux
 *       (TRUE or FALSE)</td>
 * </tr>
 *
 * <tr>
 *   <td><tt>export DRY_RUN=TRUE</tt></td>
 *   <td>don't actually do anything (considered by install procedure and
 *       cleaning routine only)</td>
 * </tr>
 * <tr>
 *   <td><tt>export MAKEFILE_DOC=FALSE</tt></td>
 *   <td>skip documentation creation (doxygen/matdoc)</td>
 * </tr>
 * <tr>
 *   <td><tt>export MAKEFILE_GLOBALINSTALLREASON="NEW: fixed XY"</tt></td>
 *   <td>Non-Interactive global installation (e.g. for shell scripts)</td>
 * </tr>
 * <tr>
 *   <td><tt>export MAKEFILE_GLOBALINSTALLUSER=username</tt></td>
 *   <td>override auto-detected global install username, maybe useful if
 *       LDAP server is busy and not responsive</td>
 * </tr>
 * <tr>
 *   <td><tt>export MAKEFILE_INSTALL_GROUPNAME=hriasc</tt></td>
 *   <td>force groupname when installing packages</td>
 * </tr>
 * <tr>
 *   <td><tt>export MAKEFILE_INSTALL_UMASK=0002</tt></td>
 *   <td>force umask (file permissions) when installing packages</td>
 * </tr>
 * <tr>
 *   <td><tt>export VERBOSE=TRUE</tt></td>
 *   <td>show all compiler output and debug messages</td>
 * </tr>
 * <tr>
 *   <td colspan="2" bgcolor="#CCCCFF"><center><b>Variables to use in
 *       packageVar.cmake for platform-dependent settings</b></center></td>
 * </tr>
 * <tr>
 *   <td><tt>COMPILER</tt></td>
 *   <td>compiler dependent build settings (e.g. gcc/msvc)</td>
 * </tr>
 * <tr>
 *   <td><tt>MAKEFILE_PLATFORM</tt></td>
 *   <td>attempt to build for specified target platform, or check if current
 *       build is about this platform</td>
 * </tr>
 * <tr>
 *   <td><tt>HOSTARCH / TARGETARCH</tt></td>
 *   <td>CPU architecture dependent build settings (e.g. 32/64 bit)</td>
 * </tr>
 * <tr>
 *   <td><tt>HOSTOS / TARGETOS</tt></td>
 *   <td>O.S. dependent build settings (e.g. Linux/Windows/MacOS)</td>
 * </tr>
 * <tr>
 *   <td colspan="2" bgcolor="#CCCCFF"><center><b>Legacy
 *       variables</b></center></td>
 * </tr>
 * <tr>
 *   <td><tt>MAKEFILE_CC</tt></td>
 *   <td>use COMPILER instead</td>
 * </tr>
 * <tr>
 *   <td><tt>MAKEFILE_CPU</tt></td>
 *   <td>use TARGETARCH instead</td>
 * </tr>
 * <tr>
 *   <td><tt>MAKEFILE_OS</tt></td>
 *   <td>use TARGETOS instead</td>
 * </tr>
 * <tr>
 *   <td><tt>MAKEFILE_SKIPSVNCHECK</tt></td>
 *   <td>use \ref ToolBOS_Concept_ToolBOSconf instead</td>
 * </tr>

 * </table>
 */


/*!
 * \page ToolBOS_UseCases_ExecInAllProjects ExecInAllProjects.py
 *
 * This is a simple script to automatize batch operations on multiple
 * packages.
 *
 * It optionally takes a list of packages to work on, and a script file for
 * executing more complicated tasks.
 *
 * <h3>Examples</h3>
 *
 * recursively update all SVN working copies (starting from current working
 * directory):
 * \verbatim
   ExecInAllProjects.py "svn up"
   \endverbatim
 *
 * update all SVN working copies listed in \c packages.txt
 * \verbatim
   ExecInAllProjects.py -l packages.txt "svn up"
   \endverbatim
 *
 * execute \c script.sh within each package (searched recursively from current
 * working directory on):
 * \verbatim
   ExecInAllProjects.py -f script.sh
   \endverbatim
 */


/*!
 * \page ToolBOS_HowTo HowTo's
 *
 * \image html ToolBOS-Logo.png
 *
 * \li \subpage ToolBOS_HowTo_Libraries
 * \li \subpage ToolBOS_HowTo_External_Packages
 * \li \subpage ToolBOS_HowTo_UserDoxyfile
 * \li \subpage ToolBOS_HowTo_Debugging
 * \li \subpage ToolBOS_HowTo_SITSwitch
 * \li \subpage ToolBOS_HowTo_ParticularRelease
 * \li \subpage ToolBOS_HowTo_Deprecated
 */


/*!
 * \page ToolBOS_HowTo_External_Packages External packages
 *
 * It is recommended to integrate 3rd party software in the same way as
 * other HRI-EU packages:
 *
 * \li install into SIT ("External" or "ExternalAdapted" category)
 * \li provide a \c packageVar.cmake (see \ref ToolBOS_Util_BuildSystemTools )
 *
 * \note If the package is shipped with its own \c FindXY.cmake you may or
 *       may not use this inside the packageVar.cmake. This likely will depend
 *       on how "smart" the \c FindXY.cmake is: Does it auto-locate itself or
 *       assumes hardcoded paths such as \c /usr/bin ?
 *
 * <h3>Example (External/python/2.6/packageVar.cmake):</h3>
 * \code
 * [...]
 *
 * include_directories($ENV{SIT}/External/python/2.6/$ENV{MAKEFILE_PLATFORM}/include/python2.6)
 *
 * link_directories($ENV{SIT}/External/python/2.6/$ENV{MAKEFILE_PLATFORM}/lib)
 *
 * list(APPEND BST_LIBRARIES_SHARED python2.6)
 *
 * [...]
\endcode
 *
 * <h3>Example (External/qt/4.6/packageVar.cmake):</h3>
 * \code
 * [...]
 *
 * find_package(Qt4)
 *
 * include(${QT_USE_FILE})
 *
 * list(APPEND BST_LIBRARIES_SHARED ${QT_LIBRARIES})
 *
 * [...]
\endcode
 *
 * <h3>HowTo</h3>
 *
 * To create a ToolBOS-style wrapper package for the 3rd party software
 * you may use the \ref ToolBOS_Util_PackageCreator and follow the
 * HowTo which you'll find within the generated package.
 *
 * \code
 * # if package requires compilation:
 * BST.py -n External_with_compilation MyPackage 1.0
 *
 * # if package comes precompiled:
 * BST.py -n External_without_compilation MyPackage 1.0
\endcode
 */


/*!
 * \page ToolBOS_HowTo_SITSwitch SIT builds
 *
 * <h3>What is an SIT build?</h3>
 *
 * Software Installation Trees can be seen as set of software modules that
 * have been tested and used together. The default (latest stable) SIT is
 * called "latest".
 *
 * Once in a while incompatible changes may occur. That's the time we
 * perform "SIT switches" in which we rebase our development onto a new
 * set of external libraries, or internal concepts. This means rebuilding
 * all software and making such more recent release the new "latest" stable
 * SIT. The former "latest" becomes "oldstable".
 *
 * <h3>Which releases exist, and what are they used for?</h3>
 *
 * <table>
 * <tr>
 *     <th><tt>oldstable</tt></th>
 *     <td><ul><li>the former "stable" SIT</li>
 *             <li>for transition period in case you experience problems
 *                 with "lastest" SIT</li>
 *             <li>maybe useful if project deadlines do not allow software
 *                 changes right now</li>
 *             <li>the installed ToolBOS SDK typically does not get altered
 *                 but exceptional / important backports are possible
 *                 (very sparse)</li></ul></td>
 * </tr>
 *
 * <tr>
 *     <th><tt>latest</tt> (=&nbsp;default)</th>
 *     <td><ul><li>the latest stable / production release</li>
 *             <li>this is the place where ongoing work is published</ul></td>
 * </tr>
 *
 * <tr>
 *     <th><tt>testing</tt></th>
 *     <td><ul><li>for in-depth testing of new features + versions</li>
 *             <li>you may globally install into this SIT (for testing
 *                 purposes)</li>
 *             <li>not for production use</li>
 *             <li>update frequency: ~2 weeks</li></ul></td>
 * </tr>
 *
 * <tr>
 *     <th><tt>unstable</tt></th>
 *     <td><ul><li>bleeding edge / nightly build</li>
 *             <li>highly experimental</li>
 *             <li>global installations are discouraged</li>
 *             <li>update frequency: daily</li></ul></td>
 * </tr>
 * </table>
 *
 * \see http://www.debian.org/releases
 *
 * <h3>How to switch?</h3>
 *
 * The desired build can be set by using the \c SIT_VERSION environment
 * variable. It needs to be set before sourcing the ToolBOSCore package.
 *
 * \code
 * export SIT_VERSION=oldstable
 * source /hri/sit/${SIT_VERSION}/DevelopmentTools/ToolBOSCore/3.3/BashSrc
\endcode
 *
 * To work permanently with this build you should set this in your
 * \c ~/.bashrc . For short usage you may open an SSH connection to
 * localhost and temporarily set this directly in the shell.
 *
 * <h3>What about proxy directories?</h3>
 *
 * The proxy directories are independent and map to the SIT_VERSION.
 * For example:
 *
 * \code
 * $ ls -ahl ~/.HRI/sit
 * [...]
 * drwxr-xr-x 13 marcus marcus 4.0K 2013-05-13 11:20 latest
 * drwxr-xr-x 16 marcus marcus 4.0K 2011-10-21 16:24 oldstable
 * drwxr-xr-x 16 marcus marcus 4.0K 2011-07-01 15:52 testing
\endcode
 *
 * \attention When using another SIT build for the first time you will
 *            not have a proxy directory for it, yet. Learn how to create
 *            a proxy directory: \ref ToolBOS_Concept_ProxyDir
 */


/*!
 * \page ToolBOS_HowTo_ParticularRelease ToolBOS release rollback or beta-test
 *
 * You may want to use a specific ToolBOS release version
 * (major.minor.patchlevel, e.g. 2.0.1234) in case of:
 * \li trouble with mainstream version (rollback to previous release)
 * \li beta-testing new features (future version)
 *
 * Set this in your ~/.bashrc:
 * \code
 * export TOOLBOSCORE_AUTO_VERSION=FALSE
 * source /hri/sit/latest/DevelopmentTools/ToolBOSCore/3.3.1234
\endcode
 * where "2.0.1234" is the particular version you are interested in.
 *
 * \note Generally you should not use a particular release, f.i. you should
 *       not set TOOLBOSCORE_AUTO_VERSION. Consider it only for the two use
 *       cases listed above.
 */


/*!
 * \page ToolBOS_HowTo_Deprecated Deprecated packages
 *
 * We encourage to <b>not delete</b> a package from SIT as it could be still
 * referenced somewhere. Instead, you should flag it as <i>deprecated</i>.
 * Hence, it won't be considered by the Nightly Build anymore and thus
 * won't appear in the next SIT build.
 *
 * <h3>Recommended way</h3>
 *
 * Use BST.py as follows:
 *
 * \code
 * BST.py [-M<message>] --deprecate[-all] [canonicalPath]
 * \endcode
 *
 * --deprecate will only deprecate a certain version, adding -all will
 * deprecate all versions. The location can be extracted from the
 * source-directory (if no canonical path is provided). Your current
 * working-directory has to be the source-directory of the package you
 * want to deprecate. If you do not have access to the source or just
 * don't want to check it out, you can provide the canonical path as
 * a parameter.
 *
 * -M allows you to specify a message, e.g. a reason why the package
 * has been deprecated and/or a hint as to which other package may be
 * used instead.
 *
 * <h4>Examples</h4>
 *
 * \code
 * BST.py -M "I don't need a reason!" --deprecate
 * BST.py -M "No replacement!" --deprecate-all DeviceIO/CanMessage/0.3
 * BST.py --deprecate Libraries/CameraModel/0.5
 * \endcode
 *
 * <h3>The manual way</h3>
 *
 * <h4>Particular version only:</h4>
 *
 * To flag a particular version of a package as deprecated, create a file
 * with the following name in the SIT:
 *
 * \code
 * $ touch /hri/sit/latest/Libraries/MyPackage/1.0/deprecated.txt
 * \endcode
 *
 * <h4>All versions of a package</h4>
 *
 * To flag all versions of a package as deprecated, you can flag the
 * versions individually or leave a central deprecated.txt in the package
 * name directory:
 *
 * \code
 * $ touch /hri/sit/latest/Libraries/MyPackage/deprecated.txt
 * \endcode
 *
 * \note You may leave a message in the \c deprecated.txt explaining what
 *       to use instead or whom to contact in case it is still needed.
 *
 * \note The \c deprecated.txt does not need to stay in VCS. It is
 *       sufficient to manually create it directly within the SIT.
 *
 * \note Packages depending on the deprecated one will automatically be
 *       considered deprecated, too.
 */


/*!
 * \page ToolBOS_HowTo_Libraries Writing C/C++ libraries
 *
 * \li prefer Any_strncpy() over strncpy() [and friends] for Windows
 *     compatibility
 *
 * \li prefer Any_sleepSeconds() over sleep() for human readability and
 *     platform independence
 *
 * \li use ANY_FREE() instead of free() for Windows compatibility
 *
 * \li check the parameters your function received from untrusted environment
 *     for semantic correctness (e.g. index ranges, existence of files,
 *     buffer lengths etc.
 *
 * \li mind to always release locks, bad example (pseudo-code):
 *     \code
 *     Mutex_lock()
 *
 *     if( foo )
 *     {
 *       return Foo          // lock is not released
 *     }
 *
 *     Mutex_unlock()
 *     \endcode
 *
 * \li allocate pointers to structs on the heap instead of using stack
 *     variables
 *
 * \li check return values of constructors and destructors, especially
 *     Mutex_init()
 *
 * \li reset pointers to NULL after _delete()
 *
 * \li do not use global buffers or variables in multi-threaded environments
 *
 * \li do not rely on the execution of function calls within the
 *     ANY_REQUIRE macro since they could be turned off (\#undef)
 */


/*!
 * \page ToolBOS_HowTo_Debugging Debugging
 *
 * \li \subpage ToolBOS_HowTo_Debugging_BuildProblems
 * \li \subpage ToolBOS_HowTo_Debugging_StartupProblems
 * \li \subpage ToolBOS_HowTo_Debugging_FindingAnyRequire
 * \li \subpage ToolBOS_HowTo_Debugging_Memory
 * \li \subpage ToolBOS_HowTo_Debugging_PerformanceProblems
 * \li \subpage ToolBOS_HowTo_Debugging_NetworkProblems
 * \li \subpage ToolBOS_HowTo_Debugging_gdbserver
 * \li \subpage ToolBOS_HowTo_Debugging_Sources
 * \li \subpage ToolBOS_HowTo_Debugging_CoreDumps
 * \li \subpage ToolBOS_HowTo_Debugging_Remote
 *
 * \note Many scripts and applications from the ToolBOS SDK provide a
 *       "-v" (verbose) option and/or consider the env.variable \c VERBOSE .
 *       If \c VERBOSE=TRUE they will show detailed progress information.
 *       Debug output is beneficial when reporting bugs on JIRA.
 *
 * \see \ref ToolBOS_Concept_SoftwareQuality
 * \see http://www.brendangregg.com/linuxperf.html
 */


/*!
 * \page ToolBOS_HowTo_Debugging_BuildProblems Compilation problems
 *
 * Enable very strict compilation settings in your \c CMakeLists.txt :
 *
 * \verbatim
   add_definitions(-Wextra)
   \endverbatim
 *
 * <h3>Utilities:</h3>
 *
 * Check predefined macros and their values:
 * \verbatim
   $ gcc -E -dM - < /dev/null
   #define __DBL_MIN_EXP__ (-1021)
   #define __UINT_LEAST16_MAX__ 65535
   #define __FLT_MIN__ 1.17549435082228750797e-38F
   #define __UINT_LEAST8_TYPE__ unsigned char
   #define __INTMAX_C(c) c ## L
   #define __CHAR_BIT__ 8
   #define __UINT8_MAX__ 255
   #define __WINT_MAX__ 4294967295U
   #define __ORDER_LITTLE_ENDIAN__ 1234
   #define __SIZE_MAX__ 18446744073709551615UL
   [...]
   \endverbatim
 *
 * Show from where a certain symbol is coming (e.g. "printf"):
 * \verbatim
   $ gcc -Wl,-y,printf main.c
   /tmp/ccehkm0g.o: reference to printf
   /lib/x86_64-linux-gnu/libc.so.6: definition of printf
   \endverbatim
 *
 * Trace which files the linker is considering:
 * \verbatim
   $ gcc -Wl,-t main.c
   /usr/bin/ld: mode elf_x86_64
   /usr/lib/gcc/x86_64-linux-gnu/4.6/../../../x86_64-linux-gnu/crt1.o
   /usr/lib/gcc/x86_64-linux-gnu/4.6/../../../x86_64-linux-gnu/crti.o
   /usr/lib/gcc/x86_64-linux-gnu/4.6/crtbegin.o
   /tmp/ccYCg1bh.o
   -lgcc_s (/usr/lib/gcc/x86_64-linux-gnu/4.6/libgcc_s.so)
   /lib/x86_64-linux-gnu/libc.so.6
   (/usr/lib/x86_64-linux-gnu/libc_nonshared.a)elf-init.oS
   /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
   -lgcc_s (/usr/lib/gcc/x86_64-linux-gnu/4.6/libgcc_s.so)
   /usr/lib/gcc/x86_64-linux-gnu/4.6/crtend.o
   /usr/lib/gcc/x86_64-linux-gnu/4.6/../../../x86_64-linux-gnu/crtn.o
   \endverbatim
 */


/*!
 * \page ToolBOS_HowTo_Debugging_StartupProblems Startup + Library loading
 *
 * <h2>Linux</h2>
 *
 * Library paths search order:
 *
 * -# \c DT_RPATH section in the ELF binary
 * -# \c LD_LIBRARY_PATH
 * -# \c DT_RUNPATH section in the ELF binary
 * -# \c /etc/ld.so.conf
 * -# \c /lib
 * -# \c /usr/lib
 *
 * <h3>Utilities:</h3>
 *
 * Show which libraries are really taken at runtime:
 *
 * \code
   $ LD_DEBUG=libs ./MyExample
   \endcode
 *
 * Show which functions are called at runtime:
 * \code
   $ ltrace ./MyExample
   \endcode
 *
 * List all libraries where myLibrary.so depends on (mind \c -r for symbol
 * relocation):
 * \code
   $ ldd -r myLibrary.so
   \endcode
 *
 * Show symbols within a particular library:
 * \code
   $ nm myLibrary.so
   \endcode
 *
 * <hr>
 * <h2>Windows</h2>
 *
 * \c depends.exe shows a tree view of all the DLL files required by an
 * executable.
 *
 * \see http://www.dependencywalker.com
 */


/*!
 * \page ToolBOS_HowTo_Debugging_FindingAnyRequire Finding an ANY_REQUIRE
 *
 * In a large graph with many identical components or libraries
 * (e.g. BPL) it's hard to find out which one caused the ANY_REQUIRE
 * and why.
 *
 * \li use \ref ANY_REQUIRE_MSG and \ref ANY_REQUIRE_VMSG within libraries
 * \li convince people to use descriptive error messages (i.e. not
 *     "ROI failed" but containing the actual values of the ROI) in order
 *     to get a hint on where to start investigating
 */


/*!
 * \page ToolBOS_HowTo_Debugging_PerformanceProblems Performance problems
 *
 * Distributing big graphs over multiple machines, still keeping the network
 * load as low as possible is non-trivial. You may loose the big picture
 * of which subsystems performing which function. Virtual modules help
 * grouping subsystems but may result in suboptimal overall performance
 * due to high network traffic.
 *
 * <h3>Utilities:</h3>
 *
 * Profile the necessary system calls:
 * \code
   $ strace ./myProgram
   \endcode
 *
 * Useful options for \c strace :
 * \li <tt>-f</tt>: follow forks
 * \li <tt>-T</tt>: timing stats
 * \li <tt>-p PID</tt>: attach to running process
 *
 * Profile the application's function callgraph (which functions are called
 * and how often, how much CPU time they consume). Then you may visualize
 * the data with \c kcachegrind .
 * \verbatim
   $ valgrind --tool=callgrind --log-file-exactly=/tmp/out.log ./myProgram

   $ kcachegrind /tmp/out.log
   \endverbatim
 */


/*!
 * \page ToolBOS_HowTo_Debugging_NetworkProblems Network problems
 *
 * <h3>Utilities (no special privileges needed):</h3>
 *
 * \li \c ifconfig
 * \li \c ping
 *
 * <h3>Utilities (root privileges needed):</h3>
 *
 * \li \c iftop
 * \li \c mii-tool
 * \li \c tcpdump
 * \li \c wireshark
 */


/*!
 * \page ToolBOS_HowTo_Debugging_Memory Segfaults + Memory leaks
 *
 * The operating system "tracks" the memory regions assigned to processes.
 * If the O.S. detects an access to other memory regions, it will terminate
 * the process with \c SEGV (<b>segmentation violation</b> aka "segfault").
 * This is typically caused by an invalid or \c NULL pointer. The root of
 * the problem might be access on freed memory or wrong pointer arithmetics.
 *
 * In case of <b>memory leaks</b> the developer forgot to free unused memory.
 * Even though this often does not harm, the operating system can not grant
 * this memory anymore until the application terminated. But if there is a
 * problem in recycling memory areas or memory is wrongly recycled, more and
 * more memory is allocated resulting in increasing memory consumption over
 * time. The machine will entirely run out of (available) memory because the
 * faulty application consumes it all. Once all the machine's memory is
 * allocated, the application may crash.
 *
 * \see http://en.wikipedia.org/wiki/Segmentation_fault
 * \see http://en.wikipedia.org/wiki/Memory_leak
 *
 * <hr>
 * \section ToolBOS_HowTo_Debugging_Memory_SystemMonitors System monitors
 *
 * \li \c top
 * \li \c htop
 * \li \c gkrellm
 *
 * <hr>
 * \section ToolBOS_HowTo_Debugging_Memory_TraceMessages Trace messages
 *
 * Put the macro \c ANY_WHERE in your C/C++ code. At execution time this
 * will log some trace message like:
 * \verbatim
   [5257.337489 3452:0 AnyWhere.c:24 Info] in function: main()
   \endverbatim
 *
 * This might help to identify which functions are executed.
 *
 * <hr>
 * \section ToolBOS_HowTo_Debugging_Memory_Valgrind Valgrind
 *
 * Check application for memory leaks:
 * \code
   $ valgrind --tool=memcheck --leak-check=full --show-reachable=yes ./myProgram
   \endcode
 *
 * \note For finding memory leaks in large DTBOS graphs, divide the crashing
 *       graph into subgraphs and place parts on separate hosts resp. processes
 *       (green "machine" boxes). Then see which machine crashes, and iterate
 *       this until the crashing component was encircled. Then you can debug
 *       this component in detail.
 *
 * <hr>
 * \section ToolBOS_HowTo_Debugging_Memory_DrMemory Dr. Memory
 *
 * Similar to \ref ToolBOS_HowTo_Debugging_Memory_Valgrind is Dr. Memory
 * which can also be hooked into Visual Studio.
 *
 * \verbatim
   $ drmemory -- <executable> [arguments]
   \endverbatim
 *
 * \see http://www.drmemory.org
 * \see http://www.drmemory.org/docs/index.html
 *
 * <hr>
 * \section ToolBOS_HowTo_Debugging_Memory_libefence Electric Fence
 *
 * The "libefence" tracks memory access and immediately fires a
 * segfault if unauthorized access is detected. With the help of that,
 * you can run the application under control of a debugger and quickly
 * find the location where the segfault has occurred.
 *
 * Simply link against \c libefence.so by adding \b efence to the
 * \b BST_LIBRARIES_SHARED in your \b CMakeLists.txt file:
 *
 * \code
   list(APPEND BST_LIBRARIES_SHARED efence)
   \endcode
 *
 * \attention Only heap memory allocated via \c malloc() will be checked.
 *            Stack variables are not considered by Electric Fence.
 *
 * \attention Electric Fence supports only 512 \c malloc() calls. Use
 *            \ref ToolBOS_HowTo_Debugging_Memory_libDUMA for larger
 *            applications.
 *
 * The \c malloc() function will be replaced by the Electric Fence library.
 * You can see it at the beginning of the console output:
 *
 * \verbatim
   Electric Fence 2.1 Copyright (C) 1987-1998 Bruce Perens.
   Segmentation fault
   \endverbatim
 *
 * If a memory violation occurs a segfault will be triggered.
 * Analyze the location of the segfault with a debugger.
 *
 * <hr>
 * \section ToolBOS_HowTo_Debugging_Memory_libDUMA libDUMA
 *
 * The DUMA (Detect Unintended Memory Access) library is a fork of
 * Electric Fence (see above) with more features:
 * \li "overloads" more C functions, e.g. \c memalign(), \c strdup(),
 *     \c free() etc.
 * \li C++ \c new / \c delete support
 * \li utilizes the MMU (memory management unit) of the CPU
 * \li leak detection: detect memory blocks which were not deallocated
 *     until program exit
 *
 * \see http://duma.sourceforge.net
 *
 * To use it:
 *
 * \code
   $ source ${SIT}/External/duma/2.5/BashSrc
   $ export LD_PRELOAD=libduma.so.0.0.0
   \endcode
 *
 * The \c malloc() etc. functions will be replaced by the DUMA library.
 * You can see it at the beginning of the console output:
 *
 * \verbatim
   DUMA 2.5.15 (shared library, NO_LEAKDETECTION)
   Copyright (C) 2006 Michael Eddington <meddington@gmail.com>
   Copyright (C) 2002-2008 Hayati Ayguen <h_ayguen@web.de>, Procitec GmbH
   Copyright (C) 1987-1999 Bruce Perens <bruce@perens.com>
   \endverbatim
 *
 * If a memory violation occurs a segfault will be triggered.
 * Analyze the location of the segfault with a debugger.
 *
 * \see \ref ToolBOS_HowTo_Debugging_Sources
 *
 * <hr>
 * \section ToolBOS_HowTo_Debugging_Memory_MemoryScape MemoryScape
 *
 * ...is a commercial product by Rogue Wave Software, Inc.&nbsp;.
 * HRI-EU got a license bundled together with the TotalView debugger.
 *
 * \see http://www.roguewave.com/products/memoryscape.aspx
 * \see http://www.roguewave.com/support/product-documentation/totalview.aspx
 *
 * \verbatim
   $ source ${SIT}/External/totalview/8.15/BashSrc

   $ memscape <executable> [-a <arguments>]
   \endverbatim
 *
 * Example:
 * \verbatim
   $ memscape $TOOLBOSCORE_ROOT/bin/$MAKEFILE_PLATFORM/RTBOS -a -i local -f Foo.cml
   \endverbatim
 *
 * \image html HowTo/MemoryScape-Event.png
 *
 * <hr>
 * \section ToolBOS_HowTo_Debugging_Memory_mtrace MTrace
 *
 * \c mtrace is the memory debugger included in the GNU C Library.
 * \see http://en.wikipedia.org/wiki/Mtrace
 *
 * <h3>1. Enable "mtrace" in your package</h3>
 *
 * Include the headerfile:
 * \code
   #include <mcheck.h>
   \endcode
 *
 * Encircle the portion of code to be checked with the following function
 * calls:
 * \code
   mtrace();
   ...
   muntrace();     // optional
   \endcode
 *
 * \note For small programs it is typically fine to just put \c mtrace()
 *       at the beginning of the \c main() function.
 *
 * Recompile your package. No additional libraries are needed.
 *
 * <h3>2. Execute the program</h3>
 *
 * \c mtrace writes memory usage information into a file. Specify its path
 * using the \c MALLOC_TRACE env.variable:
 *
 * \verbatim
   $ export MALLOC_TRACE=mtrace.log
   \endverbatim
 *
 * Then run your program, e.g.:
 * \verbatim
   $ RunFromSourceTree.sh ./examples/${MAKEFILE_PLATFORM}/ExampleProgram [args]
   \endverbatim
 *
 * <h3>3. Show memory information</h3>
 *
 * Use the \c mtrace utility to parse the temporary file. It will show the
 * locations of memory violations. It takes the path to the executable and
 * temporary file as arguments.
 *
 * \verbatim
   $ mtrace <executable> <logfile>
   \endverbatim
 *
 * <b>Example:</b>
 * \verbatim
   $ mtrace ./examples/${MAKEFILE_PLATFORM}/ExampleProgram mtrace.log

   Memory not freed:
   -----------------
              Address     Size     Caller
   0x0000000001be9460      0x4  at ./examples/AnyFree.c:29
   \endverbatim
 *
 * As you can see, \c AnyFree.c:29 contains the location of the memory leak.
 *
 * \note There is also a KDE-based GUI "kmtrace" for visualizing mtrace
 *       outputs.
 */


/*!
 * \page ToolBOS_HowTo_Debugging_gdbserver gdbserver
 *
 * In a nutshell, \c gdbserver is a program providing necessary debug
 * information to debuggers, which may run on the same machine or on
 * a remote host.
 *
 * It allows also to attach a debugger to a running process. This way
 * of debugging is called <b>"remote debugging"</b>.
 *
 * \note Remote debugging is common practice for embedded software running
 *       on a resource-limited target machine where you can't run \c GDB
 *       or \c DDD natively on.
 *
 * \verbatim
   $ gdbserver [:port] <executable>
   \endverbatim
 *
 *
 * <h2>Case 1: Starting the executable under control of gdbserver</h2>
 *
   \verbatim
   $ gdbserver ./myExecutable
   $ gdbserver :1234 ./myExecutable
   \endverbatim
 *
 * This opens a TCP connection on the specified port (or 3000 by default).
 * Then you can use the remote debugging feature of your compiler to connect
 * to this process.
 *
 * <h2>Case 2: Attaching to a running process</h2>
 *
 * \code
 * $ gdbserver --multi <port>
\endcode
 *
 * The running process (PID) to attach to is later selected within the
 * debugger.
 *
 * \see \ref ToolBOS_HowTo_Debugging_Remote
 */


/*!
 * \page ToolBOS_HowTo_Debugging_Remote Remote debugging
 *
 * You need a running \ref ToolBOS_HowTo_Debugging_gdbserver to remotely
 * debug an application.
 *
 * <h2>if development and target machine architecture are the same</h2>
 *
 * <h3>Case 1: dedicated application</h3>
 *
 * \code
 * $ gdb ./myExecutable
 * (gdb) target remote <ip:port>
 * (gdb) attach <PID>
\endcode
 *
 * <h3>Case 2: attach to running process</h3>
 *
 * \code
 * $ gdb
 * (gdb) target extended-remote <ip:port>
 * (gdb) attach <PID>
\endcode
 *
 * <h2>if development and target machines differ (e.g. Intel <--> ARM)</h2>
 *
 * <h3>Case 1: dedicated application</h3>
 *
 * \code
 * $ cross-gdb ./myExecutable
 * (gdb) set solib-absolute-prefix /tftpboot/nfsroot
 * (gdb) target extended-remote <ip:port>
 * (gdb) attach <PID>
\endcode
 *
 * <h3>Case 2: attach to running process</h3>
 *
 * \code
 * $ cross-gdb
 * (gdb) set solib-absolute-prefix /tftpboot/nfsroot
 * (gdb) target extended-remote <ip:port>
 * (gdb) attach <PID>
\endcode
 */


/*!
 * \page ToolBOS_HowTo_Debugging_Sources Source-code debugging
 *
 * <h2>Tutorials:</h2>
 *
 * \li \subpage ToolBOS_HowTo_Debugging_Sources_with_TotalView "using TotalView"
 * \li \subpage ToolBOS_HowTo_Debugging_Sources_with_GDB "using GDB"
 * \li \subpage ToolBOS_HowTo_Debugging_Sources_with_DDD "using DDD"
 *
 * \see \ref ToolBOS_HowTo_Debugging_gdbserver
 * \see \ref ToolBOS_HowTo_Debugging_CoreDumps
 */


/*!
 * \page ToolBOS_HowTo_Debugging_Sources_with_TotalView Debugging with TotalView
 *
 * <b>TotalView for HPC</b> is a commercial product by Rogue Wave Software, Inc.&nbsp;.
 * HRI-EU got a license bundled together with
 * \ref ToolBOS_HowTo_Debugging_Memory_MemoryScape .
 *
 * Usage:
 * \verbatim
   $ runTotalView.sh <executable> [-a <arguments>]
   \endverbatim
 *
 * Example:
 * \verbatim
   $ runTotalView.sh $TOOLBOSCORE_ROOT/bin/$MAKEFILE_PLATFORM/RTBOS -a -i local -f Foo.cml
   \endverbatim
 *
 * \image html HowTo/TotalView.png
 *
 * \see http://www.roguewave.com/products-services/totalview
 * \see http://www.roguewave.com/help-support/documentation/totalview
 */


/*!
 * \page ToolBOS_HowTo_Debugging_Sources_with_GDB Debugging with GDB
 *
 * <b>GDB</b>, the <b>GNU Project debugger</b>, allows you to see what is going
 * on inside another program while it executes -- or what another program was
 * doing at the moment it crashed.
 *
 * \see https://www.gnu.org/software/gdb
 *
 * \verbatim
   $ source ${SIT}/External/gdb/7.9/BashSrc

   $ gdb --args <executable> [arguments]
   \endverbatim
 *
 * <h2>Commands</h2>
 *
 * <table>
 * <tr>
 *   <th colspan="2">Useful \c GDB commands</th>
 * </tr>
 * <tr>
 *   <td><tt>break [file:]function</tt>
 *   <td>set a breakpoint at function (in file)</td>
 * </tr>
 * <tr>
 *   <td><tt>bt</tt>
 *   <td>backtrace: display the program stack</td>
 * </tr>
 * <tr>
 *   <td><tt>c</tt>
 *   <td>continue running your program (after stopping, e.g. at a
 *       breakpoint)</td>
 * </tr>
 * <tr>
 *   <td><tt>edit [file:]function</tt>
 *   <td>look at the program line where it is presently stopped</td>
 * </tr>
 * <tr>
 *   <td><tt>frame</tt>
 *   <td>jump to outer frame (e.g. caller function)</td>
 * </tr>
 * <tr>
 *   <td><tt>info breakpoints</tt>
 *   <td>show breakpoints</td>
 * </tr>
 * <tr>
 *   <td><tt>list [file:]function</tt>
 *   <td>type the text of the program in the region of where it is
 *       stopped</td>
 * </tr>
 * <tr>
 *   <td><tt>next</tt>
 *   <td>execute next program line (after stopping); step over any function
 *       calls in the line</td>
 * </tr>
 * <tr>
 *   <td><tt>print expr</tt>
 *   <td>display the value of an expression</td>
 * </tr>
 * <tr>
 *   <td><tt>quit</tt>
 *   <td>exit from GDB</td>
 * </tr>
 * <tr>
 *   <td><tt>run [arglist]</tt>
 *   <td>start your program (with arglist, if specified)</td>
 * </tr>
 * <tr>
 *   <td><tt>step</tt>
 *   <td>execute next program line (after stopping); step into any function
 *       calls in the line</td>
 * </tr>
 * </table>
 *
 * <h2>Example: Debugging RTBOS</h2>
 *
 * Suppose you have launched RTBOS under control of \c gdbserver .
 * Then connect to it by using \c GDB in remote mode:
 *
 * \verbatim
   $ gdb ${TOOLBOSCORE_ROOT}/bin/${MAKEFILE_PLATFORM}/RTBOS
   (gdb) target remote localhost:3000
   \endverbatim
 *
 * Set the breakpoints using the command \b break \c (b):
 * \verbatim
   (gdb) b main
   \endverbatim
 * sets a breakpoint on the RTBOS \c main function while
 * \verbatim
   (gdb) b UltimaTest_new
   Function "UltimaTest_new" not defined.
   Make breakpoint pending on future shared library load? (y or [n]) y
   Breakpoint 1 (UltimaTest_new) pending.
   \endverbatim
 * sets a breakpoint on the \c UltimaTest_new function. Note that at this
 * moment RTBOS has not loaded any shared object, yet, so \c GDB will ask
 * you if you want to set the specified breakpoint pending until the
 * associated symbol is loaded.
 *
 * Start the execution typing \b continue \c (c):
 * \verbatim
   (gdb) c
   Continuing.
   [New thread 23768]
   [Switching to thread 23768]
   Breakpoint 1, main (argc=7, argv=0xbf8942e4) at RTBOS.c:83
   83      BeginRTBOX
   \endverbatim
 *
 * The execution is stopped on the first breakpoint. At this point you
 * can now query the application through the standard \c GDB commands:
 * \verbatim
   (gdb) bt
   #0  main (argc=7, argv=0xbf8942e4) at RTBOS.c:83
   \endverbatim
 * to print out the backtrace of the current thread.
 *
 * \verbatim
   (gdb) info threads
   1 thread 23768  main (argc=7, argv=0xbf8942e4) at RTBOS.c:83
   \endverbatim
 * to print out the list of the current threads. Type \c (c) again to
 * continue.
 *
 * \verbatim
   (gdb) c
   Continuing.
   Breakpoint 3 at 0xb73b8dc9: file UltimaTest.c, line 180.
   Pending breakpoint "UltimaTest_new" resolved

   Breakpoint 3, UltimaTest_new () at UltimaTest.c:180
   180       UltimaTest *self = (UltimaTest*)NULL;
   \endverbatim
 * The execution is stopped on the second breakpoint. Print the code
 * around the breakpoint typing the command \b list \c (l):
   \verbatim
   (gdb) l
   175
   176
   177
   178     UltimaTest* UltimaTest_new( void )
   179     {
   180       UltimaTest *self = (UltimaTest*)NULL;
   181
   182       self = ANY_TALLOC( UltimaTest );
   183       ANY_REQUIRE( self );
   184
   \endverbatim
 *
 * Type \c (l) again to display the rest of the function:
   \verbatim
   (gdb) l
   185       return self;
   186     }
   187
   188     int UltimaTest_setup( UltimaTest *self )
   189     {
   190       int result = 0;
   191       int index = 0;
   192       int setupFunctionsLen = 0;
   193       int (*setupFunctions[])(UltimaTest* self) =
   194         {
   \endverbatim
 *
 * You can navigate within the code using the commands \b nexti \c (ni),
 * \b stepi \c (si) and \b finish. For example:
 * \verbatim
   (gdb) ni
   182       self = ANY_TALLOC( UltimaTest );
   \endverbatim
 * to advance to the next instruction within the \c UltimaTest_new function.
 *
 * To print the value of the symbols use the command \b display :
 * \verbatim
   (gdb) display self
   1: self = (UltimaTest *) 0x0
   \endverbatim
 */


/*!
 * \page ToolBOS_HowTo_Debugging_Sources_with_DDD Debugging with DDD
 *
 * See \ref ToolBOS_HowTo_Debugging_RTBOS how to start RTBOS under control
 * of \c gdbserver . Then Connect to the \c gdbserver by using \c DDD in
 * remote mode:
 *
 * \verbatim
   $ ddd ${TOOLBOSCORE_ROOT}/bin/${MAKEFILE_PLATFORM}/RTBOS
   \endverbatim
 *
 * GUI overview:
 * \image html HowTo/DDD-Overview.png
 *
 * On the "GDB Console" call the command:
 * \verbatim
   (gdb) target remote localhost:3000
   \endverbatim
 *
 * You can set breakpoints by using the command \b break \c (b) command
 * with the GDB Console or, when the source code is available within the
 * Source Window, double-clicking at the left-hand side of the instruction
 * you are interested in.
 *
 * The two cases are shown in the image below where the breakpoint on the
 * RTBOS \c main function is set directly from the Source Window while the
 * breakpoint on the \c UltimaTest_new function is set from the GDB Console:
 * \image html HowTo/DDD-SettingBreakpoints.png
 *
 * As you can see the breakpoint on the \c UltimaTest_new is set as pending.
 * This is because, at this moment, RTBOS has not loaded yet any shared
 * object, so \c gdb will set it automatically pending until the associated
 * symbol will be loaded.
 *
 * Click on the \b cont button into the Command Tool to continue the program
 * execution. The next screenshot shows the arrival to the
 * \c UltimaTest_new breakpoint. The content of the Source Window, Code
 * Machine Window and GDB Console is updated accordingly.
 * \image html HowTo/DDD-BreakpointReached.png
 *
 * You can now query the application through the Status menu in the DDD
 * main bar or by using the Command Tool to navigate into the code. You can
 * visualize the status of variable double-clicking on it from the Source
 * Window:
 * \image html HowTo/DDD-DisplayValues.png
 */


/*!
 * \page ToolBOS_HowTo_Debugging_CoreDumps Core dumps
 *
 * You can instruct your system to create a memory dump (coredump) file
 * upon application crash for postmortem analysis. You can set the max.
 * size of such corefiles. If the max. coresize is 0 Bytes (= default),
 * creating corefiles is disabled.
 *
 * \verbatim
   $ ulimit -a
   [...]
   core file size          (blocks, -c) 0
   [...]
   \endverbatim
 *
 * <h2>Enable coredump generation</h2>
 *
 * \verbatim
   $ ulimit -c unlimited
   \endverbatim
 *
 * The naming scheme of corefiles is configure via the file
 * \c /proc/sys/kernel/core_pattern . You may set it e.g. to
 * \c "/tmp/core-%p" (\c %p will be replaced by the PID).
 *
 * \attention Ubuntu Linux by default sets a pipe to \c Apport as
 *            \c core_pattern . You should ask your system administrator to
 *            change it using:
 * \verbatim
   $ sysctl kernel.core_pattern=/var/crash/%E.%p.%t.%s
   \endverbatim
 *
 * <h2>Example of crash</h2>
 *
 * \verbatim
   $ ./CrashNow
   Segmentation fault (core dumped)

   $ ls -lh /var/crash
   total 128K
   drwxrwxrwt  2 root   root   4.0K Jan 22 16:10 .
   drwxr-xr-x 15 root   root   4.0K Apr 25  2013 ..
   -rw-------  1 mstein hriasc 256K Jan 22 16:16 !home!mstein!tmp!HelloWorld!1.0!bin!precise64!CrashNow.22475.1421939771.11
   \endverbatim
 *
 * Then you can open this corefile with your preferred debugger, e.g.:
   \verbatim
   $ gdb ./CrashNow /var/crash/\!home\!mstein\!tmp\!HelloWorld\!1.0\!bin\!precise64\!CrashNow.22475.1421939771.11
   [...]
   Core was generated by `./CrashNow'.
   Program terminated with signal 11, Segmentation fault.
   #0  0x000000000040085b in printf (__fmt=0x400993 "crash  = %f\n") at /usr/include/x86_64-linux-gnu/bits/stdio2.h:105
   105       return __printf_chk (__USE_FORTIFY_LEVEL - 1, __fmt, __va_arg_pack ());
   (gdb)
   \endverbatim
 *
 * \see \ref ToolBOS_HowTo_Debugging_Sources
 */


/*!
 * \page ToolBOS_HowTo_UserDoxyfile userDoxyfile
 *
 * At globalinstall time \c doxygen is invoked to create HTML documentation
 * for your package.
 *
 * The Doxygen settings are centrally maintained in this file:
 * \c ${TOOLBOSCORE_ROOT}/etc/Doxyfile
 *
 * You may override any settings in a file \c doc/userDoxyfile within your
 * package. Just copy and paste particular lines from the master Doxyfile
 * to yours and set the desired values.
 *
 * \attention Mind to set all path names relative to the working directory
 *            where \c doxygen will be invoked. It is launched from within
 *            the \c "doc" directory.
 *
 * <h3>Example:</h3>
 *
 * To index also files in a custom \c "mySources" directory, do the
 * following steps:
 *
 * \code
 * $ mkdir -p doc
 * $ cp ${TOOLBOSCORE_ROOT}/etc/Doxyfile doc/userDoxyfile
\endcode
 *
 * Delete all but the following line to override the particular setting,
 * e.g.:
 *
 * \code
 * INPUT = ../src ../mySources
\endcode
 *
 * Upon next \c doxygen run the directory "../mySources" will be indexed.
 *
 * \see http://www.stack.nl/~dimitri/doxygen/manual/config.html
 */


/*!
 * \page ToolBOS_Contact Authors / Contact
 *
 * \section Authors
 * \li Marcus Stein
 * \li Roberto Fichera
 * \li Alessandro Piras
 * \li Mattia Ziulu
 * \li Siddhata Naik
 * \li and contributions by many other people
 *
 * \section Contact
 *
 * <table>
 * <tr>
 *     <td style="vertical-align: top;">Address:</td>
 *     <td>Honda Research Institute Europe GmbH<br>
 *         Carl-Legien-Straße 30<br>
 *         63073 Offenbach am Main<br>
 *         Germany</td>
 * </tr>
 * <tr>
 *     <td>Phone:</td>
 *     <td>+49 (0)69 / 89011750</td>
 * </tr>
 * <tr>
 *     <td>Fax:</td>
 *     <td>+49 (0)69 / 89011749</td>
 * </tr>
 * <tr>
 *     <td>Weblink:</td>
 *     <td><a href="https://www.honda-ri.de">www.honda-ri.de</a></td>
 * </tr>
 * <tr>
 *     <td>E-Mail:</td>
 *     <td>info@honda-ri.de</td>
 * </tr>
 * </table>
 */


/* EOF */
