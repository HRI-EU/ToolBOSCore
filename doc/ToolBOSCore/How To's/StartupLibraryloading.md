###  Startup + Library loading

###  Linux

Library paths search order:

* 1\. DT_RPATH section in the ELF binary
* 2\. LD_LIBRARY_PATH
* 3\. DT_RUNPATH section in the ELF binary
* 4\. /etc/ld.so.conf
* 5\. /lib
* 6\. /usr/lib
 
 
 ###  Utilities:
      
Show which libraries are really taken at runtime:

    $ LD_DEBUG=libs ./MyExample
    
Show which functions are called at runtime: 

    $ ltrace ./MyExample
    
List all libraries where myLibrary.so depends on (mind -r for symbol relocation):

    $ ldd -r myLibrary.so
    
Show symbols within a particular library:

    $ nm myLibrary.so
    
####  Windows

depends.exe shows a tree view of all the DLL files required by an executable.

**See also**  
    http://www.dependencywalker.com 