###  Remote debugging

You need a running [gdbserver](GdbServer.md) to remotely debug an application.

#### If development and target machine architecture are the same

**Case 1: dedicated application**

    $ gdb ./myExecutable
    (gdb) target remote <ip:port>
    (gdb) attach <PID>
    
**Case 2: attach to running process**

     $ gdb
     (gdb) target extended-remote <ip:port>
     (gdb) attach <PID>
     
#### If development and target machines differ (e.g. Intel <--> ARM)

**Case 1: dedicated application**

    $ cross-gdb ./myExecutable
    (gdb) set solib-absolute-prefix /tftpboot/nfsroot
    (gdb) target extended-remote <ip:port>
    (gdb) attach <PID>
    
**Case 2: attach to running process**

    $ cross-gdb
    (gdb) set solib-absolute-prefix /tftpboot/nfsroot
    (gdb) target extended-remote <ip:port>
    (gdb) attach <PID>