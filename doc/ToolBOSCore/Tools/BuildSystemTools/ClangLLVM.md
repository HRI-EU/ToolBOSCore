##  Clang/LLVM

Under Linux BST.py allows compiling using the Clang/LLVM compiler infrastructure (default: GCC). Clang/LLVM is said to:

* generally produce better error messages
* compile faster than GCC
* in some scenarios create faster / smaller binaries

#### Usage

    $ export BST_USE_CLANG=TRUE

    $ BST.py

You may also fix this setting

* in the pkgInfo.py if it is package-specific or
* in the ToolBOS.conf if it is a user- or site-preference.

#### Weblinks

*   [The LLVM Compiler Infrastructure](http://www.llvm.org)
*   [Clang](http://www.clang.org)

