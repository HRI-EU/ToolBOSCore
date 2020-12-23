##  Static linking


When using static linking together with pthreads, the compile and target hosts have to have exactly matching glibc,
otherwise leading to strange segfaults.

Therefore, when speaking in context of BST.py the term "static" linking of executables is **actually wrong**: 
The HRI-EU and 3rd party libraries are linked statically, but the executable still links dynamically against essential
system libraries (libc, pthread,...). True static compilation is not possible as soon as dlopen() and 
friends (f.i. in libToolBOSCore ) are needed.

Note that CMake supports true static linking of executables though.

###  HowTo

* in your CMakeLists.txt, locate the line for building executables (bst_build_executable or bst_build_executables )
* change the set of link libraries from BST_LIBRARIES_SHARED (= default) to BST_LIBRARIES_STATIC
* before this line, add the switch to static link mode: set(BST_LINK_MODE STATIC)


**Example:**

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
    
The resulting executable will link against essential libraries only (in fact is a dynamically linked executable):

    $ ldd test/focal64/unittest
         linux-vdso.so.1 =>  (0x00007fff12e2b000)
         librt.so.1 => /lib/x86_64-linux-gnu/librt.so.1 (0x00007fc41c3b4000)
         libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fc41c196000)
         libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fc41bdd6000)
         /lib64/ld-linux-x86-64.so.2 (0x00007fc41c5f5000)
