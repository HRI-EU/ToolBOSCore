##  Cross-compiling from Linux to Windows

### How it works

We execute the Microsoft Visual Studio compiler and linker under Linux,
using the Wine framework. Thus, the resulting binaries do not link against
any emulation layer or helper libraries.    


###  GUI usage

Go to the top-level directory of your package and launch the "Zen Build Mode"
of `BST.py`.
Within the GUI select the desired platform(s) to build for and press the
"Build" button.

  BST.py -z

###  Command-line usage

Go to the top-level directory of your package and run the following command:

    $ BST.py -p windows-amd64-vs2012
