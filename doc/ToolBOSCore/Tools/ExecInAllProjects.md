###  ExecInAllProjects.py

This is a simple script to automatize batch operations on multiple packages.

It optionally takes a list of packages to work on, and a script file for executing more complicated tasks.


####  Examples

recursively update all SVN working copies (starting from current working directory):

    ExecInAllProjects.py "svn up"

update all SVN working copies listed in packages.txt

    ExecInAllProjects.py -l packages.txt "svn up"

execute script.sh within each package (searched recursively from current working directory on):

    ExecInAllProjects.py -f script.sh

