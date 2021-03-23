### gdbserver

In a nutshell, gdbserver is a program providing necessary debug information to debuggers, which may run on the same
machine or on a remote host.

It allows also to attach a debugger to a running process. This way of debugging is called **"remote debugging".**

> **Note**
> Remote debugging is common practice for embedded software running on a resource-limited target machine where you 
> can't run GDB or DDD natively on.

    $ gdbserver [:port] <executable>

#### Case 1: Starting the executable under control of gdbserver

    $ gdbserver ./myExecutable
    $ gdbserver :1234 ./myExecutable

This opens a TCP connection on the specified port (or 3000 by default). Then you can use the remote debugging feature
of your compiler to connect to this process.

####Case 2: Attaching to a running process

    $ gdbserver --multi <port>

The running process (PID) to attach to is later selected within the debugger.

See also
    [Remote debugging](RemoteDebugging.md) 

