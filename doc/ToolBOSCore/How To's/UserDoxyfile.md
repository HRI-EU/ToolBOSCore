###  userDoxyfile

At globalinstall time doxygen is invoked to create HTML documentation for your package.

The Doxygen settings are centrally maintained in this file: ${TOOLBOSCORE_ROOT}/etc/Doxyfile

You may override any settings in a file doc/userDoxyfile within your package. Just copy and paste particular lines
from the master Doxyfile to yours and set the desired values.

> **Attention**
>    Mind to set all path names relative to the working directory where doxygen will be invoked. It is launched from within the "doc" directory.

####  Example:

To index also files in a custom "mySources" directory, do the following steps:

    $ mkdir -p doc
    $ cp ${TOOLBOSCORE_ROOT}/etc/Doxyfile doc/userDoxyfile

Delete all but the following line to override the particular setting, e.g.:

    INPUT = ../src ../mySources

Upon next doxygen run the directory "../mySources" will be indexed.

**See also**   
    http://www.stack.nl/~dimitri/doxygen/manual/config.html 

