##  CMakeLists.txt + packageVar.cmake

###  Dependencies

For each library to use from the SIT, put one include statement into your CMakeLists.txt:

    bst_find_package(DevelopmentTools/ToolBOSCore/3.2)
    bst_find_package(Libraries/MasterClock/1.6)
  
    
###  Additional paths + flags

If you need to specify the include- and/or library paths for the compiler, and also settings such as CFLAGS,
you have to edit the CMakeLists.txt file:

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
    

###  External libraries
     
If you want to use a library libExternal.so which is located in /usr/local/External/lib, please specify this path
in your CMakeLists.txt:

    link_directories(/usr/local/External/lib)
    list(APPEND BST_LIBRARIES_SHARED External)
    
###  Frequently asked

  <table>
 
  <tr>
    <th colspan="2">Defining targets</th>
  </tr>
  <tr>
    <td>building libraries</td>
    <td>file(GLOB SRC_FILES src/.c src/.cpp)<br/>
            bst_build_libraries("${SRC_FILES}" "${PROJECT_NAME}"
            "${BST_LIBRARIES_SHARED}")</td>
  </tr>
  <tr>
    <td>building an executable</td>
    <td>file(GLOB FOO_FILES bin/Foo.c)<br/>
            bst_build_executable(Foo "${FOO_FILES}"
            "${BST_LIBRARIES_SHARED}")</td>
  </tr>
  <tr>
    <td>building a set of executables</td>
    <td>file(GLOB FOO_FILES bin/Foo.c)<br/>
            bst_build_executables("${FOO_FILES}"
            "${BST_LIBRARIES_SHARED}")</td>
  </tr>
  <tr>
    <th colspan="2">Including dependencies</th>
  </tr>
  <tr>
    <td>add dependency to package</td>
    <td>bst_find_package(Libraries/Foo/1.0)</td>
  </tr>
  <tr>
    <th colspan="2">Build settings</th>
  </tr>
  <tr>
    <td>add include path</td>
    <td>include_directories(dir1 dir2 ...)</td>
  </tr>
  <tr>
    <td>add linker path</td>
    <td>link_directories(dir1 dir2 ...)</td>
  </tr>
  <tr>
    <td>link against libraries</td>
    <td>list(APPEND BST_LIBRARIES_SHARED foo bar)</td>
  </tr>
  <tr>
    <td>compiler definitions</td>
    <td>add_definitions(-DFOO -ggdb)</td>
  </tr>
  <tr>
    <td>force C++ compiler on .c file</td>
    <td>set_source_files_properties(filename.c PROPERTIES
                                                   LANGUAGE CXX)</td>
  </tr>
  <tr>
    <td>add C compiler flags</td>
    <td>set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -ggdb -fPIC")</td>
  </tr>
  <tr>
    <td>add C++ compiler flags</td>
    <td>set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")</td>
  </tr>
  <tr>
    <th colspan="2">CMake variables</th>
  </tr>
  <tr>
    <td>define a variable</td>
    <td>set(MYVAR a)            # one element<br/>
            set(MYVAR "a b c d e")  # one element (string)<br/>
            set(MYVAR a b c d e)    # five elements</td>
  </tr>
  <tr>
    <td>environment variables</td>
    <td>$ENV{VARNAME}</td>
  </tr>
  <tr>
    <td>list of libraries to link</td>
    <td>${BST_LIBRARIES_SHARED}</td>
  </tr>
  <tr>
    <td>top-level directory</td>
    <td>${CMAKE_HOME_DIRECTORY}</td>
  </tr>
  <tr>
    <td>package name</td>
    <td>${PACKAGE_NAME}</td>
  </tr>
  <tr>
    <td>package version</td>
    <td>${PACKAGE_VERSION}</td>
  </tr>
  <tr>
    <th colspan="2">Conditions</th>
  </tr>
  <tr>
    <td>check for native Windows host</td>
    <td>if(WINDOWS)<br/>...<br/>else()<br/>...<br/>endif()</td>
  </tr>
  <tr>
    <td>check for particular platform</td>
    <td>if("$ENV{MAKEFILE_PLATFORM}" STREQUAL "windows-amd64-vs2017")<br/>...<br/>else()<br/>...<br/>endif()</td>
  </tr>
  </table>
  
  
See also  
     [CMake](http://www.cmake.org/cmake/help/documentation.html) 
