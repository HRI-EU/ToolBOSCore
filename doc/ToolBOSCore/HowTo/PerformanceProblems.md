### Performance problems

Distributing big graphs over multiple machines, still keeping the network load as low as possible is non-trivial.
You may loose the big picture of which subsystems performing which function. Virtual modules help grouping subsystems
but may result in suboptimal overall performance due to high network traffic.

#### Utilities:

Profile the necessary system calls:

    $ strace ./myProgram

Useful options for strace :

* -f: follow forks
* -T: timing stats
* -p PID: attach to running process

Profile the application's function callgraph (which functions are called and how often, how much CPU time they consume).
Then you may visualize the data with kcachegrind .

    $ valgrind --tool=callgrind --log-file-exactly=/tmp/out.log ./myProgram

    $ kcachegrind /tmp/out.log

