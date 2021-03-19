##  Multi-platform support

![](BST-small.png)

When writing platform-specific code please use those defines within preprocessor directives 
(they are automatically set by BST.py):

#### Operating systems:

* __linux__

* __windows__

* __win32__

* __win64__

#### Compilers:

* __gcc__

* __msvc__

#### Processor architectures:

* __32BIT__

* __64BIT__

* __arm__

* __armv7__

#### Example

    #if defined(__linux__)
       [... Linux code ...]
    #endif
    #if defined(__windows__) && !defined(__msvc__)
       [... Non-MSVC Windows code ...]
    #endif