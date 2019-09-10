###  Macros documentation

ToolBOS provides a few helper macros to write CMakeLists.txt files. Consider them as sugar, they are totally optional.

Pass the -DCMAKE_MODULE_PATH=${TOOLBOSCORE_ROOT}/include/CMake option to CMake to find the BuildSystemTools.cmake file.
In your CMakeLists.txt include it as follows:

    find_package(BuildSystemTools)

> Note  
>    Hint: For easy exchange with collaborative partners you may store a copy of these Build System Tools files within
>    your package. This way they are also under your version control system.


###  Dependency inclusion

<table>
<tr><th>bst_find_package(PACKAGE)</th></tr>
<tr><td>Use this macro to import packages from the SIT. It is a decorator of CMake's find_package function specific for
        importing settings from a packageVar.cmake file located in the SIT. PACKAGE must be a "canonical package name" 
        f.i. no leading ${SIT} or the like, nor a trailing packageVar.cmake.</td></tr>
<tr><td>Example</td></tr>
<tr><td>
   bst_find_package(DevelopmentTools/ToolBOSCore/3.2)
   bst_find_package(Libraries/MasterClock/1.6)</td></tr>
</table>

