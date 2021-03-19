###  Debugging with GDB

**GDB**, the **GNU Project debugger**, allows you to see what is going on inside another program while it executes – 
or what another program was doing at the moment it crashed.

**See also**  
    https://www.gnu.org/software/gdb
    
    $ source ${SIT}/External/gdb/7.9/BashSrc
    
    $ gdb --args <executable> [arguments]
    
###  Commands

* <table>
 <tr>
   <th colspan="2">Useful GDB commands</th>
 </tr>
 <tr>
   <td>break [file:]function
   <td>set a breakpoint at function (in file)</td>
 </tr>
 <tr>
   <td>bt
   <td>backtrace: display the program stack</td>
 </tr>
 <tr>
   <td>c
   <td>continue running your program (after stopping, e.g. at a
       breakpoint)</td>
 </tr>
 <tr>
   <td>edit [file:]function
   <td>look at the program line where it is presently stopped</td>
 </tr>
 <tr>
   <td>frame
   <td>jump to outer frame (e.g. caller function)</td>
 </tr>
 <tr>
   <td>info breakpoints
   <td>show breakpoints</td>
 </tr>
 <tr>
   <td>list [file:]function
   <td>type the text of the program in the region of where it is
       stopped</td>
 </tr>
 <tr>
   <td>next
   <td>execute next program line (after stopping); step over any function
       calls in the line</td>
 </tr>
 <tr>
   <td>print expr
   <td>display the value of an expression</td>
 </tr>
 <tr>
   <td>quit
   <td>exit from GDB</td>
 </tr>
 <tr>
   <td>run [arglist]
   <td>start your program (with arglist, if specified)</td>
 </tr>
 <tr>
   <td>step
   <td>execute next program line (after stopping); step into any function
       calls in the line</td>
 </tr>
 </table>
 

###  Example: Debugging RTBOS

Suppose you have launched RTBOS under control of gdbserver. Then connect to it by using GDB in remote mode:

    $ gdb ${TOOLBOSCORE_ROOT}/bin/${MAKEFILE_PLATFORM}/RTBOS
    (gdb) target remote localhost:3000
    
Set the breakpoints using the command **break** (b):

    (gdb) b main
    
sets a breakpoint on the RTBOS main function while

    (gdb) b UltimaTest_new
    Function "UltimaTest_new" not defined.
    Make breakpoint pending on future shared library load? (y or [n]) y
    Breakpoint 1 (UltimaTest_new) pending.

sets a breakpoint on the UltimaTest_new function. Note that at this moment RTBOS has not loaded any shared object, yet,
so GDB will ask you if you want to set the specified breakpoint pending until the associated symbol is loaded.

Start the execution typing **continue** (c):

    (gdb) c
    Continuing.
    [New thread 23768]
    [Switching to thread 23768]
    Breakpoint 1, main (argc=7, argv=0xbf8942e4) at RTBOS.c:83
    83      BeginRTBOX
    
The execution is stopped on the first breakpoint. At this point you can now query the application through the 
standard GDB commands:

    (gdb) bt
    #0  main (argc=7, argv=0xbf8942e4) at RTBOS.c:83
    
to print out the backtrace of the current thread.

    (gdb) info threads
    1 thread 23768  main (argc=7, argv=0xbf8942e4) at RTBOS.c:83
    
 to print out the list of the current threads. Type (c) again to continue.

    (gdb) c
    Continuing.
    Breakpoint 3 at 0xb73b8dc9: file UltimaTest.c, line 180.
    Pending breakpoint "UltimaTest_new" resolved
    
    Breakpoint 3, UltimaTest_new () at UltimaTest.c:180
    180       UltimaTest *self = (UltimaTest*)NULL;
    
The execution is stopped on the second breakpoint. Print the code around the breakpoint typing the command list (l):

    gdb) l
    175
    176
    177
    178     UltimaTest* UltimaTest_new( void )
    179     {
    180       UltimaTest *self = (UltimaTest*)NULL;
    181
    182       self = ANY_TALLOC( UltimaTest );
    183       ANY_REQUIRE( self );
    184
    
Type (l) again to display the rest of the function:

    (gdb) l
    185       return self;
    186     }
    187
    188     int UltimaTest_setup( UltimaTest *self )
    189     {
    190       int result = 0;
    191       int index = 0;
    192       int setupFunctionsLen = 0;
    193       int (*setupFunctions[])(UltimaTest* self) =
    194         { 
    
You can navigate within the code using the commands nexti (ni), stepi (si) and finish. For example:

    (gdb) ni
    182       self = ANY_TALLOC( UltimaTest );
  
to advance to the next instruction within the UltimaTest_new function.

To print the value of the symbols use the command **display** :

    (gdb) display self
    1: self = (UltimaTest *) 0x0
