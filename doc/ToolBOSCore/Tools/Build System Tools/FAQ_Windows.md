##  FAQ (Windows)


##  cl.exe not found

**Error message:**

    wine: could not load L"C:\\windows\\system32\\cl.exe": Module not found

or:

    wine: cannot find L"C:\\windows\\system32\\cl.exe"

**Solution:** This happens if the symlink ${HOME}/.wine/drive_c/msvc-sdk is broken. For example it was pointing to a 
proxy or SIT build that has been (re-)moved.   
In rare cases the package name and/or version of the MSVC compiler could have been changed so that the link gets broken.


##  Include files and/or libraries not found

If you get errors that header files or libraries are not found then check that NO link to your home directory is 
present within ${HOME}/.wine/dosdrives as this typically results in path conflicts.

The directory should look like this: 
     
      $ ls -ahl ~/.wine/dosdevices/
      total 8.0K
      drwxr-xr-x 2 mstein bstasc 4.0K Jun 13 13:35 .
      drwxr-xr-x 4 mstein bstasc 4.0K Jul 25 14:21 ..
      lrwxrwxrwx 1 mstein hriasc   10 Jun 13 13:35 c: -> ../drive_c
      lrwxrwxrwx 1 mstein hriasc    1 Jun 13 13:35 z: -> /
      

##  Cannot open compiler intermediate file

**Error message:**
     
    c1 : fatal error C1083: Cannot open compiler intermediate file:
    'c:\temp\_CL_f395d08bex': No such file or directory

**Solution:** Your Wine configuration apparently lacks the typical Windows directory for temporary files.
 Please create it:
 
     $ mkdir ~/.wine/drive_c/temp
    
    
##  Cannot execute the specified program
     
**Error message:**   
   
    The system cannot execute the specified program
     
**Solution:** Please install the Microsoft Visual Studio Runtime Libraries v.2008 
(mind the 2008 version, 2005 doesn't work).


##  MSVCR90.dll can't be found

**Error message:**   

    MSVCR90.dll can't be found

Solution: Create the following manifest file: 

    <?xml version='1.0' encoding='UTF-8' standalone='yes'?>
    <assembly xmlns='urn:schemas-microsoft-com:asm.v1' manifestVersion='1.0'>
      <dependency>
        <dependentAssembly>
          <assemblyIdentity type='win32'
                            name='Microsoft.VC90.CRT'
                            version='9.0.21022.8'
                            processorArchitecture='x86'
                            publicKeyToken='1fc8b3b9a1e18e3b' />
        </dependentAssembly>
      </dependency>
    </assembly>
    
Then add this file to the Visual Studio project file
(Project -> Properties -> Configuration Properties -> Manifest Tool -> Input and Output -> Additional Manifest Files).  
Then recompile the package.
 
 
##  C99 compliance
      
Note that MSVC is not fully C99 compliant. Especially you will need to put variables at the beginning of a code block.
      
**Wrong (C99 standard, will not work with MSVC):**

    int myFunction( int x )
    {
      int result = 0;
      // ...do something...
      for( int i = 0; i <= x; i++ )
      {
        // ...do something else...
      }
      return result;
    }
    
**Correct (C89 standard, MSVC compliant):**

    int myFunction( int x )
    {
      int result = 0;
      int i      = 0;
      // ...do something...
      for( i = 0; i <= x; i++ )
      {
        // ...do something else...
      }
      return result;
    }

 
##  Path delimiter in Wine vs. native Windows
 
There is a difference when executing (not compiling!) using Wine under Linux, compared to executing on Windows:
 
The FileSystem library (part of ToolBOSCore) has a constant called FILESYSTEM_LINE_DELIMITER which evaluates to \n 
on Linux and to \r\\n on Windows. When running a test program with Wine it is possible that a file on Linux is expected 
to have lines terminating with \r\\n which is not valid for the underlying host operating system. 