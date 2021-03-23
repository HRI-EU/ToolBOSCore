### Writing C/C++ libraries

* prefer Any_strncpy() over strncpy() [and friends] for Windows compatibility

* prefer Any_sleepSeconds() over sleep() for human readability and platform independence

* use ANY_FREE() instead of free() for Windows compatibility

*  check the parameters your function received from untrusted environment for semantic correctness (e.g. index ranges, existence of files, buffer lengths etc.

* mind to always release locks, bad example (pseudo-code):

      Mutex_lock()
      if( foo )
      {
        return Foo          // lock is not released
      }
      Mutex_unlock()
    
        
* allocate pointers to structs on the heap instead of using stack variables

* check return values of constructors and destructors, especially Mutex_init()

* reset pointers to NULL after _delete()

* do not use global buffers or variables in multi-threaded environments

* do not rely on the execution of function calls within the ANY_REQUIRE macro since they could be turned off (#undef)

