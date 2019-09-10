##  Installation conventions

The path to a package within the SIT has the following structure:

    ${SIT}/<Category>/<PackageName>/<PackageVersion> 
    
for example: 

    ${SIT}/DevelopmentTools/ToolBOSCore/3.2

A package name must start with an alphabetic character (A-Z, a-z). The name must only contain alpha-numeric 
characters (A-Z, a-z, 0-9) and dashes (-). Please give descriptive names so that someone who doesn't know particular 
abbreviations could anyway guess what the package is roughly about.

Version-numbers have the general format <Major>.<Minor>\[.<Patchlevel>\]\[-<ExtraTag>\]', e.g.: 

    1.0
    3.2.12
    2012.0
    42.0.1337-rc1
    

* see http://www.semver.org for the semantic meaning of major/minor/patchlevel
* \<Major\>, \<Minor\> and \<Patchlevel\> must contain digits only.
* \<ExtraTag\> is an optional extension separated by a dash ("-") which can contain any printable characters.
* It is forbidden to use symlinks like default, testing or stable pointing to a particular version as this creates 
  troubles during upgrade phases in which some people use the "old" stable and some others already use the "new" stable
  version.
* It is useful to install packages in 3-digit-form (1.0.0 ) and provide a symlink 1.0 which points to this. In that way 
  you can easily install other patch level versions and perform rollbacks in case of errors (by just changing the symlink 
  to a previous release).
* When using patch levels, other packages which depend on this must refer to the two-digit symlink only.

Please stick to those directory names for the mentioned content: 


| directory name  | typically expected content                                                               |
| :-------------- | :-----------------------------------------------------------                             |
| bin             | scripts and platform-independent executables such as Java bytecode                       |
| bin/\<platform\>| platform-specific binaries such as Linux ELF and/or Windows executables                  |
| doc             | documentation <br> - put \*.pdf files directly inside the doc directory <br> - put doxygen/pydoc/matdoc docu inside an html subdirectory<br> <br>If an html subdirectory exists, the entry page should be called index.html.  |
| data            | bigger amounts of resource files needed by the application, such as images (icons) or file-oriented database files |
| etc             | configfiles and settings                                                                 |
| examples        | tutorial material explaining the usage of the software                                   |
| external        | 3rd party content that can/should not be separately installed into SIT (${SIT}/External) |
| include         | headerfiles (*.h ) or Python files (*.py )                                               |
| lib             | platform-independent binaries such as Java *.jar files                                   |
| lib/\<platform\>| platform-specific libraries such as static libraries, shared objects and/or Windows DLL files |


> **Note**
>
>    * For C/C++ libraries, the main header file should match the name of the package, e.g. ToolBOSCore.h for 
>      the ToolBOSCore package.
>    * C/C++ library packages may only provide static OR shared libraries. However, providing both is recommended 
>      for flexibility reasons.
>    * Python modules should best be grouped under include/\<PackageName\> 
>    * If necessary the \<platform\> directory and the subdirectories can be reversed (\<platform\>lib/), but please try to 
       avoid for consistency reasons.


###  Example:

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

   
**See also**

[Source tree conventions](SourceTreeConventions.md)  
[Software Installation Tree (SIT)](SIT.md)

