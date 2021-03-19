##  Executing applications

###  Linux applications

Executables are often using shared libraries, therefore they need to know where those required files are located.
On Linux/Unix the search path for libraries is stored in the system variable $LD_LIBRARY_PATH while for Windows it is $PATH.

In order to properly setup the right path automatically, you may use this script:

    RunFromSourceTree.sh ./examples/${MAKEFILE_PLATFORM}/ExampleProgram <arguments>


###  Windows applications

The easiest way to run an application with many libraries under Windows is to collect all the *.exe and *.dll files
into a single directory.

Please refer to the Export Wizard documentation.


###  Windows applications on Linux, using Wine

With the "-p windows-amd64-vs2012" option you can execute Windows binaries on Linux machines, using the Wine framework.

    $ RunFromSourceTree.sh -p windows-amd64-vs2012 test/windows-amd64-vs2012/testDataSet.exe
    [1266874888.373423 9:0 testDataSet.cpp:318 Info] base constructor sampling plan
    [1266874888.373423 9:0 testDataSet.cpp:326 Data] mNumDimensions=Dimension: 0
    [1266874888.373423 9:0 testDataSet.cpp:327 Data] mNumPoints=Points: 0
    [1266874888.373423 9:0 testDataSet.cpp:369 Info] class name: mySampling
    [1266874888.373423 9:0 testDataSet.cpp:391 Info] base init sampling plan
    [1266874888.373423 9:0 testDataSet.cpp:404 Data] mNumDimensions=Dimension: 5
    [1266874888.373423 9:0 testDataSet.cpp:405 Data] numSamples=Points: 100
    [...]
    
**See also**   
    [Debugging](../../HowTo/Debugging.md)
