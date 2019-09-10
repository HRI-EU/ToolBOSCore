###  Custom scripts for compilation + installation

![](BST-small.png)

BST.py searches for scripts that entirely replace the default compile- resp. install procedures. If present,
they get executed in behalf of the standard procedure.

![](/home/snaik/code/ToolBOSCore/doc/html/BuildSystemTools-Timeline.png)
*script execution when invoked within Nightly Build: pre/post-<stepName>.sh scripts only once, and the <stepName>.sh
 once per supported platform*
 
> **Note**  
> Wherever the filename extension .sh (on Linux) is mentioned, the same applies for .bat on Windows.
> So you can provide e.g. both unittest.sh and unittest.bat on Windows


The following stepNames are supported:

* configure
* compile
* install
* distclean
* unittest

**Replacing the install procedure**

When writing a custom install.sh script you may call the tools' native install procedure.
However toolchains such as GNU Autotools do not know about our proxy directories. Even more they may need to pass the 
install location to the ./configure script and then the final install location may get compiled into the executable ("rpath").

In order to test the installation of such packages set the environment variable DRY_RUN to TRUE before compiling.
This way the install location gets prefixed by /tmp . Then you can safely test the installation of the package without 
actually altering the SIT. Yes, this is only a sub-optimal workaround :-/ Please propose better alternatives.

#### Writing unittests

**see**  
[Unittests](Unittests.md) 