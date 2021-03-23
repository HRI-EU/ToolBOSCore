###  External packages

It is recommended to integrate 3rd party software in the same way as other HRI-EU packages:

* install into SIT ("External" or "ExternalAdapted" category)
* provide a packageVar.cmake (see [Build System Tools](../Tools/BuildSystemTools/BuildSystemTools.md) )

> **Note**
> If the package is shipped with its own FindXY.cmake you may or may not use this inside the packageVar.cmake.
> This likely will depend on how "smart" the FindXY.cmake is: Does it auto-locate itself or assumes hardcoded paths 
> such as /usr/bin ?

#### Example (External/python/2.6/packageVar.cmake):

    [...]
    include_directories($ENV{SIT}/External/python/2.6/$ENV{MAKEFILE_PLATFORM}/include/python2.6)
    link_directories($ENV{SIT}/External/python/2.6/$ENV{MAKEFILE_PLATFORM}/lib)
    list(APPEND BST_LIBRARIES_SHARED python2.6)
    [...]
    
####  Example (External/qt/4.6/packageVar.cmake):

     [...]
     find_package(Qt4)
     include(${QT_USE_FILE})
     list(APPEND BST_LIBRARIES_SHARED ${QT_LIBRARIES})
     [...]
     
####  HowTo

To create a ToolBOS-style wrapper package for the 3rd party software you may use the 
[Package Creator](../Tools/PackageCreator/PackageCreator.md) and follow the 
HowTo which you'll find within the generated package.

    # if package requires compilation:
    BST.py -n External_with_compilation MyPackage 1.0
    # if package comes precompiled:
    BST.py -n External_without_compilation MyPackage 1.0   
