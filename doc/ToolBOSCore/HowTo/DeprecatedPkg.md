###  Deprecated packages

We encourage to **not delete** a package from SIT as it could be still referenced somewhere. Instead, you should flag it 
as deprecated. Hence, it won't be considered by the Nightly Build anymore and thus won't appear in the next SIT build.

#### Recommended way

Use BST.py as follows:

    BST.py [-M<message>] --deprecate[-all] [canonicalPath]

–deprecate will only deprecate a certain version, adding -all will deprecate all versions. The location can be extracted 
from the source-directory (if no canonical path is provided). Your current working-directory has to be the source-directory
 of the package you want to deprecate. If you do not have access to the source or just don't want to check it out, you
 can provide the canonical path as a parameter.

-M allows you to specify a message, e.g. a reason why the package has been deprecated and/or a hint as to which other 
package may be used instead.

####  Examples

    BST.py -M "Please use newer version 2.0 instead." --deprecate
    BST.py -M "Package is discontinued." --deprecate-all DeviceIO/CanMessage/0.3
    BST.py --deprecate Libraries/CameraModel/0.5

**The manual way**

**Particular version only:**

To flag a particular version of a package as deprecated, create a file with the following name in the SIT:

    $ touch /hri/sit/latest/Libraries/MyPackage/1.0/deprecated.txt

You may also put some information to the user into this file, e.g. what to use instead.
    
**All versions of a package**

To flag all versions of a package as deprecated, you can flag the versions individually or leave a central deprecated.txt 
in the package name directory:

    $ touch /hri/sit/latest/Libraries/MyPackage/deprecated.txt

> Note
>   You may leave a message in the deprecated.txt explaining what to use instead or whom to contact in case it is still needed.
>   The deprecated.txt does not need to stay in VCS. It is sufficient to manually create it directly within the SIT.
>   Packages depending on the deprecated one will automatically be considered deprecated, too. 

