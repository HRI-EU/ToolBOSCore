##  command-line


> Note  
>    Run **BST.py --new help** to see the full list of available templates.


### Syntax

    BST.py --new <TEMPLATE> <PACKAGE_NAME> <PACKAGE_VERSION>
    

### Example:

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
        │   ├── MyPackage.c
        │   └── MyPackage.h
        ├── test
        │   └── unittest.c
        └── unittest.sh

    8 directories, 6 files
